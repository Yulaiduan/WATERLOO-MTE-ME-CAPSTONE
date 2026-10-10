"""Independent SymPy energy derivation checked against browser model via Node.

Run: python scripts/validate_linkage_reference.py
Writes compact offline reference fixtures; Python is not an app dependency.
"""
from pathlib import Path
import copy
import json
import subprocess
import shutil

import numpy as np
import sympy as sp
from scipy.linalg import eigvals, solve
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
if not NODE: raise RuntimeError('Install Node.js and put it on PATH.')
q, phi, dq, dphi = sp.symbols("q phi dq dphi", real=True)
z = sp.Matrix([q, phi])
zd = sp.Matrix([dq, dphi])


def node(script, data=None):
    run = subprocess.run([str(NODE), "--input-type=module", "-e", script], cwd=ROOT,
                         input=json.dumps(data) if data is not None else None,
                         text=True, capture_output=True, check=True)
    return json.loads(run.stdout)


def derive(c, angle, drive):
    """Build scalar kinetic/potential energies, differentiate symbolically."""
    g, m, s = c["geometry"], c["mass"], c["spring"]
    direction = lambda a: sp.Matrix([sp.sin(a), -sp.cos(a)])
    beta = (1-g["guideRatio"])*q + g["guidePhase"]
    knee = g["upperLength"]*direction(q)
    axle = knee + g["lowerLength"]*direction(beta)
    upper = m["upperComFraction"]*knee
    lower = knee + g["lowerLength"]*m["lowerComFraction"]*direction(beta)
    alpha = g["driveRatio1"]*phi + (1-g["driveRatio1"])*q
    theta = g["driveRatio2"]*alpha + (1-g["driveRatio2"])*beta
    kinetic = 0
    gravity = 0
    for point, mass in [(upper,m["upperMass"]),(lower,m["lowerMass"]),(axle,m["wheelMass"])]:
        vel = point.jacobian(z)*zd
        kinetic += mass*vel.dot(vel)/2
        gravity += m["gravity"]*mass*point[1]
    for orient, inertia in [(q,m["upperInertia"]),
                            (beta,m["lowerInertia"]),
                            (alpha,m["compoundPulleyInertia"]),(theta,m["wheelInertia"])]:
        speed = (sp.Matrix([orient]).jacobian(z)*zd)[0]
        kinetic += inertia*speed**2/2
    for coordinate, speed, axis in [(q,dq,"fold"),(phi,dphi,"drive")]:
        a = c["actuators"][axis]
        kinetic += a["rotorInertia"]*a["reduction"]**2*speed**2/2
    if s["type"] == "torsion":
        delta = q-s["restAngle"]
        spring = s["stiffness"]*delta**2/2-s["preloadTorque"]*delta
    elif s["type"] == "linear":
        point = s["attachFraction"]*knee if s["attachLink"] == "upper" else knee+g["lowerLength"]*s["attachFraction"]*direction(beta)
        separation = point-sp.Matrix([s["anchorX"],s["anchorY"]])
        length = sp.sqrt(separation.dot(separation))
        extension = length-s["freeLength"]
        if s["tensionOnly"] and float(extension.subs(q,angle)) <= 0:
            spring = sp.Integer(0)
        else:
            spring = s["linearStiffness"]*extension**2/2
    else:
        spring = sp.Integer(0)
    massmatrix = sp.hessian(kinetic,zd)
    axle_jac = axle.jacobian(z)
    wheel_jac = sp.Matrix([theta]).jacobian(z)
    load = axle_jac.T*sp.Matrix([c["load"]["forceX"],c["load"]["forceY"]])+wheel_jac.T*c["load"]["wheelMoment"]
    sub = {q:angle,phi:drive,dq:0.7,dphi:-2.3}
    values = lambda expr: np.array(expr.subs(sub).evalf(),dtype=float).tolist()
    scalar = lambda expr: float(expr.subs(sub).evalf())
    spring_torque = -sp.diff(spring,q)
    expected = {"C":values(axle.T)[0], "wheelAngle":scalar(theta),
                "jacobian":values(axle_jac.col_join(wheel_jac)),
                "massMatrix":values(massmatrix),
                "gravity":scalar(sp.diff(gravity,q)),
                "gravityDerivative":scalar(sp.diff(gravity,q,2)),
                "gravitationalEnergy":scalar(gravity),
                "springEnergy":scalar(spring),"springElasticTorque":scalar(spring_torque),
                "springTangent":scalar(sp.diff(spring,q,2)),
                "staticFoldTorque":scalar(sp.diff(gravity,q)-load[0]-spring_torque)}
    cartesian_power = (sp.Matrix([c["load"]["forceX"],c["load"]["forceY"]]).T*axle_jac*zd)[0]+c["load"]["wheelMoment"]*(wheel_jac*zd)[0]
    generalized_power = (load.T*zd)[0]
    assert abs(scalar(cartesian_power-generalized_power)) < 1e-10
    expected["power"] = scalar(cartesian_power)
    loaded_curvature = sp.diff(gravity,q,2)-sp.diff(load[0],q)+sp.diff(spring,q,2)
    spring_damping = s["damping"] if s["type"] == "torsion" else (s["linearDamping"]*scalar(sp.diff(length,q))**2 if s["type"] == "linear" else 0)
    stiffness = np.diag([scalar(loaded_curvature)+c["actuators"]["fold"]["kp"],c["actuators"]["drive"]["kp"]])
    damping = np.diag([spring_damping+c["actuators"]["fold"]["viscousFriction"]+c["actuators"]["fold"]["kd"],c["actuators"]["drive"]["viscousFriction"]+c["actuators"]["drive"]["kd"]])
    mass_numeric = np.array(expected["massMatrix"])
    ideal_a = np.block([[np.zeros((2,2)),np.eye(2)],[-np.linalg.solve(mass_numeric,stiffness),-np.linalg.solve(mass_numeric,damping)]])
    expected["idealStateMatrix"] = ideal_a.tolist()
    expected["idealPoles"] = [[float(p.real),float(p.imag)] for p in eigvals(ideal_a)]
    physical_k = np.diag([scalar(loaded_curvature),0])
    physical_d = damping-np.diag([c["actuators"]["fold"]["kd"],c["actuators"]["drive"]["kd"]])
    kp = np.diag([c["actuators"]["fold"]["kp"],c["actuators"]["drive"]["kp"]])
    kd = np.diag([c["actuators"]["fold"]["kd"],c["actuators"]["drive"]["kd"]])
    inv_lag = np.diag([1/c["actuators"]["fold"]["lag"],1/c["actuators"]["drive"]["lag"]])
    finite_a = np.block([[np.zeros((2,2)),np.eye(2),np.zeros((2,2))],[-np.linalg.solve(mass_numeric,physical_k),-np.linalg.solve(mass_numeric,physical_d),np.linalg.solve(mass_numeric,np.eye(2))],[-inv_lag@kp,-inv_lag@kd,-inv_lag]])
    expected["finiteUnsaturatedStateMatrix"] = finite_a.tolist()
    expected["finiteUnsaturatedPoles"] = [[float(p.real),float(p.imag)] for p in eigvals(finite_a)]
    for prefix, matrix in [("ideal",ideal_a),("finiteUnsaturated",finite_a)]:
        forcing = np.zeros(matrix.shape[0])
        forcing[2:4] = np.linalg.solve(mass_numeric,np.array([1.,0.]))
        response = []
        for frequency in [0.05,np.sqrt(10),200.]:
            transfer = solve(2j*np.pi*frequency*np.eye(matrix.shape[0])-matrix,forcing)
            y_transfer = scalar(sp.diff(axle[1],q))*transfer[0]
            wheel_transfer = scalar(sp.diff(theta,q))*transfer[0]+scalar(sp.diff(theta,phi))*transfer[1]
            response.append({"frequencyHz":frequency,"qMagnitude":abs(transfer[0]),"qPhaseDeg":np.angle(transfer[0],deg=True),"yMagnitude":abs(y_transfer),"wheelMagnitude":abs(wheel_transfer)})
        expected[prefix+"FrequencyResponse"] = response
    return expected


def main():
    base = node("import {defaultConfig} from './src/linkage/model.js'; console.log(JSON.stringify(defaultConfig()));")
    cases = []
    for name in ["reference_equal_links", "unequal_links_carrier_drive", "linear_spring_lower_attachment"]:
        c = copy.deepcopy(base)
        if name != "reference_equal_links":
            c["geometry"].update(upperLength=0.21,lowerLength=0.16,guideRatio=1.7,guidePhase=0.12,driveRatio1=1.5,driveRatio2=0.8)
            c["load"].update(forceX=11,forceY=47,wheelMoment=0.7)
        if name == "linear_spring_lower_attachment":
            c["spring"].update(type="linear",attachLink="lower",anchorX=-0.075,anchorY=0.035,attachFraction=0.64,freeLength=0.24)
        angle, drive = 0.63, 0.27
        c["geometry"]["pose"] = angle
        c["motion"]["initialDriveAngle"] = drive
        cases.append({"name":name,"config":c,"q":angle,"phi":drive,"expected":derive(c,angle,drive)})
    actual = node("import {pose,virtualWork,localStability} from './src/linkage/model.js'; let s=''; for await(const x of process.stdin)s+=x; console.log(JSON.stringify(JSON.parse(s).map(c=>{let finite=structuredClone(c.config); finite.actuators.fold.torqueLimit=1e6;finite.actuators.drive.torqueLimit=1e6;return {pose:pose(c.config,c.q,c.phi),stability:localStability(c.config,'ideal'),finite:localStability(finite,'finite'),power:virtualWork(c.config,c.q,[c.config.load.forceX,c.config.load.forceY],c.config.load.wheelMoment,[.7,-2.3]).inputPower};})));", cases)
    for case, result in zip(cases,actual):
        p = result["pose"]
        flat = {**p,"springEnergy":p["spring"]["energy"],"springElasticTorque":p["spring"]["elasticTorque"],"springTangent":p["spring"]["tangentStiffness"],"staticFoldTorque":p["static"]["foldTorque"],"power":result["power"]}
        for key, expected in case["expected"].items():
            if key in ["idealStateMatrix","idealPoles","finiteUnsaturatedStateMatrix","finiteUnsaturatedPoles","idealFrequencyResponse","finiteUnsaturatedFrequencyResponse"]:
                continue
            np.testing.assert_allclose(flat[key],expected,rtol=2e-10,atol=2e-11,err_msg=f"{case['name']} {key}")
        for response, prefix in [("stability","ideal"),("finite","finiteUnsaturated")]:
            np.testing.assert_allclose(result[response]["stateMatrix"],case["expected"][prefix+"StateMatrix"],rtol=2e-7,atol=2e-7,err_msg=f"{case['name']} {prefix} state matrix")
            reference_poles = np.array([complex(*p) for p in case["expected"][prefix+"Poles"]])
            actual_poles = np.array([complex(p["real"],p["imag"]) for p in result[response]["poles"]])
            rows, columns = linear_sum_assignment(abs(reference_poles[:,None]-actual_poles[None,:]))
            np.testing.assert_allclose(actual_poles[columns],reference_poles[rows],rtol=2e-7,atol=2e-7,err_msg=f"{case['name']} {prefix} SciPy poles")
            for index, expected_response in zip([0,60,120],case["expected"][prefix+"FrequencyResponse"]):
                actual_response = result[response]["frequencyResponse"][index]
                for key, value in expected_response.items():
                    np.testing.assert_allclose(actual_response[key],value,rtol=2e-7,atol=2e-7,err_msg=f"{case['name']} {prefix} frequency response {key}")
        print(f"PASS {case['name']}: symbolic energies, geometry, power, ideal and finite-lag SciPy poles")
    destination = ROOT/"tests"/"fixtures"/"linkage"/"sympy-reference.json"
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps({"derivation":"Independent SymPy kinetic-energy Hessian and potential derivatives","cases":cases},indent=2)+"\n",encoding="utf-8")
    print(f"Saved {len(cases)} reference cases to {destination}")


if __name__ == "__main__":
    main()
