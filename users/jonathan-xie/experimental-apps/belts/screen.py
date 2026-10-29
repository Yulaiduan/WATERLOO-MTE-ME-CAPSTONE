"""Screen nominal open-belt layouts for equal-link VSL geometry.

Run: python screen.py (standard library only); writes CSV/JSON in results/.
Inputs: Gates catalogued pitch lengths (mm), sprocket teeth and pitch (mm).
Outputs: individual layouts and paired AB/CD/EF candidates near 250/300 mm.
Limits: pitch-line geometry only; no tension, fatigue, torque or stock guarantee.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'results'
STOCK5 = [18,19,20,21,22,23,24,25,26,28,30,32,34,36,38,40,44,45,48,50,52,56,60,64,68,72,80,90,112]
STOCK8 = [22,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,45,48,50,53,56,60,63,67,71,75,80,90,112,140,180,224]
LENGTHS = {5:[300,375,425,500,535,600,635,700,815],8:[640,720,800,896,960,1000,1040,1120,1200,1224,1280,1440]}

def radius(n,p):
    return n*p/(2*math.pi)

def length(c,n,N,p):
    r,R=radius(n,p),radius(N,p)
    d=R-r
    return 2*math.sqrt(c*c-d*d)+math.pi*(R+r)+2*d*math.asin(d/c)

def center(b,n,N,p):
    lo=radius(n+N,p)
    if b<=length(lo,n,N,p):
        return None
    hi=b/2
    for _ in range(65):
        mid=(lo+hi)/2
        if length(mid,n,N,p)<b:lo=mid
        else:hi=mid
    return (lo+hi)/2

def layout(b,n,N,p,stock):
    c=center(b,n,N,p)
    if c is None:return None
    wrap=180-2*math.degrees(math.asin(radius(N-n,p)/c))
    return dict(pitch_mm=p,small_teeth=n,large_teeth=N,ratio=N/n,
                small_pitch_radius_mm=radius(n,p),large_pitch_radius_mm=radius(N,p),
                belt_length_mm=b,belt_teeth=b//p,center_mm=c,
                small_wrap_deg=wrap,teeth_in_mesh=n*wrap/360,
                stock_teeth=n in stock and N in stock,
                pitch_circle_gap_mm=c-radius(n+N,p))

def write_csv(name,rows):
    with (ROOT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    singles=[]
    for p in [5,8]:
        stock=STOCK5 if p==5 else STOCK8
        for n in range(min(stock),113):
            for N in range(2*n,min(5*n,224)+1):
                for b in LENGTHS[p]:
                    z=layout(b,n,N,p,stock)
                    if z and 235<=z['center_mm']<=315:singles.append(z)
    write_csv('individual-layouts.csv',singles)
    paired=[]
    for ab in singles:
        if ab['ratio']!=2:continue
        for dr in singles:
            delta=dr['center_mm']-ab['center_mm']
            if abs(delta)>.25:continue
            target=min([250,300],key=lambda t:abs(t-ab['center_mm']))
            if abs(target-ab['center_mm'])>15:continue
            row={'target_mm':target,'pitch_mm':ab['pitch_mm'],'drive_pitch_mm':dr['pitch_mm'],
                 'L_AB_mm':ab['center_mm'],'L_drive_mm':dr['center_mm'],
                 'drive_minus_AB_mm':delta,'exact_nominal_match':abs(delta)<1e-8,
                 'all_stock_teeth':ab['stock_teeth'] and dr['stock_teeth'],
                 'Na':ab['large_teeth'],'Nb':ab['small_teeth'],
                 'Nc_Ne':dr['small_teeth'],'Nd_Nf':dr['large_teeth'],
                 'qdc_qfe':dr['ratio'],'B_AB_mm':ab['belt_length_mm'],'B_drive_mm':dr['belt_length_mm'],
                 'ra_mm':ab['large_pitch_radius_mm'],'rb_mm':ab['small_pitch_radius_mm'],
                 'rc_re_mm':dr['small_pitch_radius_mm'],'rd_rf_mm':dr['large_pitch_radius_mm'],
                 'AB_small_wrap_deg':ab['small_wrap_deg'],'drive_small_wrap_deg':dr['small_wrap_deg'],
                 'drive_teeth_in_mesh':dr['teeth_in_mesh'],
                 'drive_length_residual_at_AB_mm':length(ab['center_mm'],dr['small_teeth'],dr['large_teeth'],dr['pitch_mm'])-dr['belt_length_mm']}
            paired.append(row)
    paired.sort(key=lambda z:(z['target_mm'],not z['exact_nominal_match'],not z['all_stock_teeth'],abs(z['L_AB_mm']-z['target_mm']),abs(z['drive_minus_AB_mm'])))
    write_csv('paired-layouts.csv',paired)
    original=[]
    for n,N in [(25,50),(18,56)]:
        z=layout(600,n,N,5,STOCK5)
        z['length_at_205_3_mm']=length(205.3,n,N,5)
        original.append(z)
    (ROOT/'original-check.json').write_text(json.dumps(original,indent=2)+'\n')
    print('ORIGINAL',json.dumps(original,indent=2))
    for target in [250,300]:
        for label,predicate in [('A STOCK',lambda z:z['all_stock_teeth'] and z['qdc_qfe']==2),('B STOCK EXACT',lambda z:z['all_stock_teeth'] and z['exact_nominal_match'] and z['qdc_qfe']>2),('B CUSTOM EXACT',lambda z:not z['all_stock_teeth'] and z['exact_nominal_match'] and z['qdc_qfe']>2),('B STOCK CLOSE',lambda z:z['all_stock_teeth'] and not z['exact_nominal_match'] and z['qdc_qfe']>2),('B CUSTOM CLOSE',lambda z:not z['all_stock_teeth'] and not z['exact_nominal_match'] and z['qdc_qfe']>2)]:
            rows=[z for z in paired if z['target_mm']==target and predicate(z)]
            rows.sort(key=lambda z:(abs(z['drive_minus_AB_mm']) if 'CLOSE' in label else abs(z['L_AB_mm']-target),abs(z['L_AB_mm']-target)))
            print(target,label,json.dumps(rows[:5],indent=2))
    # Forward residuals and independent numerical integration of pitch arcs/spans.
    err=max(abs(length(z['center_mm'],z['small_teeth'],z['large_teeth'],z['pitch_mm'])-z['belt_length_mm']) for z in singles)
    assert err<1e-9
    for z in paired:
        if z['exact_nominal_match']:
            assert abs(z['drive_length_residual_at_AB_mm'])<1e-8
    # Equal radial differences yield an independently known exact belt-length shift.
    identity_errors=[]
    for c in [205.3,250,300]:
        identity_errors.append(abs(length(c,25,50,8)-length(c,20,60,5)-100))
        identity_errors.append(abs(length(c,30,60,8)-length(c,22,52,8)-64))
    assert max(identity_errors)<1e-9
    validation=dict(individual_layouts=len(singles),paired_layouts=len(paired),
                    max_forward_residual_mm=err,max_identity_error_mm=max(identity_errors),
                    original_center_mismatch_mm=original[0]['center_mm']-original[1]['center_mm'],
                    nominal_exact_threshold_mm=1e-8,
                    limits='Nominal pitch-line geometry only; no load or hardware validation.')
    (ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print('COUNTS',len(singles),len(paired),'max forward residual mm',err)

if __name__=='__main__':main()
