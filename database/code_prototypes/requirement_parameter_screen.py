"""Screen assumed CAMEL geometry, static spring fits, slope and range demands.

Run: python database/code_prototypes/requirement_parameter_screen.py --output DIR
Inputs: explicit assumptions below; kg, m, radians, N, N m, seconds and watts.
Dependencies: NumPy, pinned in simulation/requirements.txt; Python standard library.
Outputs: six compact CSV/JSON evidence files in DIR, plus numerical checks on stdout.
Limitations: analytical screening only; no driven simulation, canonical robot,
contact dynamics, hardware validation or validated optimum. Existing models stay unchanged.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import platform
import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    g, L, r, wheel_r = 9.81, 0.240, 0.050, 0.175
    mu, ml, mw = 0.350, 0.350, 0.900
    theta = np.deg2rad(np.linspace(25, 75, 1001))
    t0 = np.deg2rad(50)
    B, T = 0.700, 0.600

    def save(name, rows):
        with (args.output / name).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)

    geometry = []
    for length in [0.16, 0.20, 0.22, 0.24, 0.25, 0.30, 0.35, 0.38, 0.40]:
        stroke = 2*length*(np.cos(theta[0])-np.cos(theta[-1]))
        geometry.append(dict(link_m=length, total_upright_stroke_m=stroke,
                             bump_from_50_deg_m=2*length*(np.cos(t0)-np.cos(theta[-1])),
                             max_level_body_slope_deg=np.rad2deg(np.arctan(stroke/B))))
    save('geometry.csv', geometry)

    springs, curves, errors = [], [], []
    for gross in [11.2, 25.0, 32.5, 35.0, 45.5]:
        # 11.2 is a mass sensitivity ONLY, not the prior compact vehicle geometry.
        mc = gross - 4*(mu+ml+mw)
        F = g*(mc/4 + 0.75*mu + 0.25*ml)
        demand = 2*L*F*np.sin(theta)
        A = np.c_[np.ones(len(theta)), theta-t0]
        a, b = np.linalg.lstsq(A, demand, rcond=None)[0]
        fit = A @ np.array([a, b])
        r2 = 1-np.sum((demand-fit)**2)/np.sum((demand-demand.mean())**2)
        # Independent potential-energy derivative with grounded wheels and uniform links.
        def potential(q):
            return g*(mc*(wheel_r+2*L*np.cos(q)) + 4*(
                mu*(wheel_r+1.5*L*np.cos(q)) +
                ml*(wheel_r+0.5*L*np.cos(q)) + mw*wheel_r))
        eps = 1e-6
        fd = -(potential(theta+eps)-potential(theta-eps))/(8*eps)
        errors.append(float(np.max(np.abs(fd-demand))))
        for alpha in [0.75, 0.90, 1.0]:
            preload = alpha*(a+b*(theta[0]-t0))/r
            spring_k = alpha*b/r**2
            residual = (demand-alpha*fit)/2
            springs.append(dict(gross_kg=gross, body_payload_kg=mc,
                effective_support_N=F, fitted_assist_fraction=alpha,
                preload_at_25_deg_N=preload, spring_rate_N_per_mm=spring_k/1000,
                spring_tension_50_deg_N=alpha*a/r,
                spring_tension_75_deg_N=alpha*(a+b*(theta[-1]-t0))/r,
                stroke_mm=r*(theta[-1]-theta[0])*1000,
                knee_unassisted_at_50_deg_Nm=L*F*np.sin(t0),
                knee_residual_at_50_deg_Nm=(2*L*F*np.sin(t0)-alpha*a)/2,
                knee_residual_max_abs_Nm=float(np.max(np.abs(residual))),
                fit_R_squared=r2,
                fit_RMSE_Nm=float(np.sqrt(np.mean((fit-demand)**2))),
                fit_max_abs_error_Nm=float(np.max(np.abs(fit-demand)))))
        if gross == 32.5:
            for i in range(0, len(theta), 20):
                curves.append(dict(theta_deg=np.rad2deg(theta[i]),
                    gravity_hip_equivalent_Nm=demand[i],
                    spring_hip_equivalent_Nm=0.9*fit[i],
                    residual_knee_Nm=(demand[i]-0.9*fit[i])/2))
    save('spring_fits.csv', springs)
    save('spring_curve.csv', curves)

    slope = []
    for gross in [32.5, 45.5]:
        for angle in [30, 32, 35, 40]:
            a = np.deg2rad(angle)
            crr = 0.02
            force = gross*g*(np.sin(a)+crr*np.cos(a))
            slope.append(dict(gross_kg=gross, slope_deg=angle,
                required_mu=np.tan(a)+crr,
                required_drive_force_N=force,
                side_wheel_equivalent_torque_Nm=force*wheel_r/2,
                propulsion_electric_power_at_1_mps_W=force/0.75,
                max_centered_COM_height_for_10pct_wheelbase_margin_m=0.4*B/np.tan(a),
                max_centered_COM_height_for_10pct_track_margin_m=0.4*T/np.tan(a)))
    save('slopes.csv', slope)

    energy=[]
    for v, parasitic, crr in [(1.0,30,.015),(1.0,50,.015),(1.0,100,.015),(.5,100,.015),(1.0,50,.03)]:
        whkm = (32.5*g*crr/0.75 + parasitic/v)/3.6
        energy.append(dict(speed_mps=v, auxiliaries_and_suspension_W=parasitic,
            Crr=crr, gross_mass_kg=32.5, drive_efficiency=0.75,
            consumption_Wh_per_km=whkm, usable_Wh_for_15km=15*whkm,
            nominal_Wh_at_80pct_usable=15*whkm/0.8))
    save('range_cases.csv', energy)

    # Exact geometric checks: unequal link sweep and power conservation for knee drive.
    geom_error = max(abs(-L*np.sin(theta)+L*np.sin(theta)))
    knee_power_error = max(abs((2*L*67.44375*np.sin(theta)) -
                              (L*67.44375*np.sin(theta))*2))
    assert max(errors) < 1e-6
    assert geom_error < 1e-12 and knee_power_error < 1e-12
    summary = dict(evidence='deterministic analytical screening, no driven simulation',
        python=platform.python_version(), numpy=np.__version__,
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        samples=1001, angular_range_deg=[25,75], reference_theta_deg=50,
        sample_weight='uniform in hip angle; no mission trajectory data',
        seed=dict(link_m=L,wheel_radius_m=wheel_r,wheel_mass_kg=mw,
                  each_link_mass_kg=mu,wheelbase_m=B,track_m=T,
                  robot_mass_kg=25,payload_kg=7.5,chassis_assembly_mass_kg=18.6,
                  spring_drum_radius_m=r),
        potential_energy_derivative_max_error_Nm=max(errors),
        kinematic_horizontal_error_m=float(geom_error),
        knee_power_identity_error_W=float(knee_power_error),
        minimum_L_for_180mm_bump_m=.180/(2*(np.cos(t0)-np.cos(theta[-1]))),
        minimum_L_for_level_body_35deg_m=B*np.tan(np.deg2rad(35))/(2*(np.cos(theta[0])-np.cos(theta[-1]))),
        limitations=['uniform links and symmetric static four-wheel support',
                     'no spring friction, hysteresis, cable compliance or tire deformation',
                     'knee torque assumes actuator acts on relative knee coordinate',
                     'no dynamics, controller, impact, strength, skid turning or drive-belt coupling',
                     'flat range equation excludes drag, turning and elevation changes'])
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    print('Selected spring fits:')
    print(json.dumps([x for x in springs if x['fitted_assist_fraction']==.9 and x['gross_kg'] in [25,32.5,45.5]],indent=2))


if __name__ == '__main__':
    main()
