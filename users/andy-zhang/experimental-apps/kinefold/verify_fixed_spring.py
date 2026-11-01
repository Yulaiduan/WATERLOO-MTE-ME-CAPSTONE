"""Check fixed-chassis spring work, browser/native drawing and short engines.

Run app Python verify_fixed_spring.py [--real] [--capture DIR]. Inputs portable
V4.5 mm/deg/kg/N design; geometry SI internals, torque Nm and energy J. Outputs
assertions/compact JSON and optional ignored paired {payload,result} captures.
No profile writes/server/GUI. Numerical model checks, not hardware validation.
"""
import argparse,json,math
from pathlib import Path
from dynamic_model import Model,defaults,R,SPRING_CONVENTION
from contact_cases import ContactGeometry,CASE_DEFAULTS,model_identity
from desktop_viewer import spring_drawing

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--real',action='store_true');parser.add_argument('--capture',type=Path);parser.add_argument('--parity-json',type=Path);args=parser.parse_args()
    p=json.loads((ROOT/'saved-configurations/vsl-v45-flat-support-balanced-alpha0.json').read_text(encoding='utf-8'))['params'];p.update(springK=8,p0=330.8692828089511,theta2=135)
    config=defaults();config.update(duration=.1,dt=.0005,outputHz=100,inputRiseMm=10,inputHeightMm=0,inputSpeedMmS=100)
    count=0;max_error=0.;hashes=[];parity=[]
    for alpha in (0,20,45):
        params={**p,'alpha':alpha};model=Model(params,config);display=model.world_spring();hashes.append(model.hash())
        for i in range(101):
            q=(p['te']+(p['tc']-p['te'])*i/100)*R;s=model.spring(q);w=display.spring(q)
            assert abs(s['force']-w['force'])<1e-9 and abs(s['torque']-w['torque'])<1e-9
            eps=1e-6;error=abs((model.spring(q+eps)['energy']-model.spring(q-eps)['energy'])/(2*eps)+s['torque']);max_error=max(max_error,error);assert error<1e-6
            frame=dict(t=0,theta2=q/R,A=[11,0,700],springConvention=SPRING_CONVENTION)
            drawing=spring_drawing(model,frame);assert abs(drawing['S'][0]-(11-p['Su']))<1e-9 and abs(drawing['S'][2]-(700+p['Sv']))<1e-9
            assert abs(drawing['fixedSeat'][2]-drawing['movingSeat'][2])<1e-9
            count+=5
            parity.append(dict(params=params,theta=q/R,force=s['force'],torque=s['torque'],energy=s['energy'],delta=s['payout']-model.reference_payout,S=drawing['S'],D=drawing['D']))
        cc={**config,'inputRiseMm':0,'inputSpeedMmS':0};contact=ContactGeometry(params,cc);assert abs(contact.spring(contact.q0)['torque']-model.spring(model.q0)['torque'])<1e-10
    assert len(set(hashes))==3
    results={}
    if args.real:
        import dynamics,analytical_contact,contact_dynamics
        # Two prescribed and two actual finite-link contact runs, no search.
        for engine in ('analytical','pymunk'):
            req=dict(engine=engine,params={**p,'alpha':20},runConfig=config)
            result=dynamics.simulate(req);assert result['scope']['springConvention']==SPRING_CONVENTION;assert all(f['springConvention']==SPRING_CONVENTION for f in result['frames']);results['prescribed-'+engine]=len(result['rows'])
        actual_config={**config,'inputRiseMm':0,'inputSpeedMmS':0};contact=dict(mode='terrain-contact',friction=.8,restitution=0,drive='free')
        for engine,fn in [('analytical',analytical_contact.simulate_contact),('pymunk',contact_dynamics.simulate_contact)]:
            req=dict(engine=engine,params={**p,'alpha':20},runConfig=actual_config,contactConfig=contact,caseConfig=dict(CASE_DEFAULTS))
            result=fn(req);assert result['scope']['springConvention']==SPRING_CONVENTION;assert all(f['springConvention']==SPRING_CONVENTION for f in result['frames']);results['contact-'+engine]=dict(samples=len(result['rows']),Fs=result['rows'][0]['Fs'],hash=result['designHash'])
            if args.capture:
                args.capture.mkdir(parents=True,exist_ok=True);(args.capture/(engine+'.json')).write_text(json.dumps(dict(payload=req,result=result)),encoding='utf-8')
        assert results['contact-analytical']['hash']==results['contact-pymunk']['hash']
        assert abs(results['contact-analytical']['Fs']-results['contact-pymunk']['Fs'])<1e-10
    if args.parity_json:
        args.parity_json.parent.mkdir(parents=True,exist_ok=True);args.parity_json.write_text(json.dumps(parity),encoding='utf-8')
    print(json.dumps(dict(status='PASS',checks=count,maxEnergyDerivativeErrorNm=max_error,runs=results)))

if __name__=='__main__':main()
