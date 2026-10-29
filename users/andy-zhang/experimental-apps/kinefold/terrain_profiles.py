"""Build bounded periodic experimental terrain from a versioned sheet snapshot.

Imported by contact engines/profile validation; no physics engine dependency.
Inputs: terrain-v1 JSON in mm, source ID/revision, severity, obstacle/RMS mode.
Outputs: exact piecewise-linear contour/statistics, SI moving collision segments.
Limitations: rigid 2D flat-average-grade proxy; no soil, snow, grade or roll model.
"""
import bisect
import json
import math
from pathlib import Path

CATALOG = json.loads(Path(__file__).with_name('terrain-catalog.json').read_text(encoding='utf-8'))
SEGMENTS = 96
KEYS = {'schema','catalogRevision','profileId','severity','representation','periodMm','heightMm','rmsMm'}


def validate_terrain(value):
    if not isinstance(value, dict) or set(value) != KEYS:
        raise ValueError('terrainConfig requires exactly ' + ', '.join(sorted(KEYS)))
    if value['schema'] != 'kinefold/terrain-v1' or value['catalogRevision'] != CATALOG['revision']:
        raise ValueError('Unknown terrain schema/catalog revision; retain its matching catalog.')
    if value['profileId'] not in {p['id'] for p in CATALOG['profiles']} or value['severity'] not in ('typical','difficult','extreme') or value['representation'] not in ('obstacles','roughness'):
        raise ValueError('Choose a known terrain, severity and representation.')
    for key,lo,hi in [('periodMm',100.,100000.),('heightMm',0.,1000.),('rmsMm',0.,1000.)]:
        n=value[key]
        if key != 'periodMm' and n is None: continue
        if type(n) not in (int,float) or not math.isfinite(n) or not lo <= n <= hi:
            raise ValueError(key+' must be finite within '+str((lo,hi)))
    required='heightMm' if value['representation']=='obstacles' else 'rmsMm'
    if value[required] is None: raise ValueError('Source '+required+' is unresolved for this terrain/severity.')
    return dict(value)


def contour(value):
    c=validate_terrain(value);rough=c['representation']=='roughness'
    ys=[]
    for i in range(SEGMENTS+1):
        p=i/SEGMENTS
        ys.append(1-math.cos(2*math.pi*p) if rough else (.5*(1-math.cos(4*math.pi*(p-.25))) if .25<p<.75 else 0.))
    def moments(values):
        return (sum((a+b)/2 for a,b in zip(values,values[1:]))/SEGMENTS,
                sum((a*a+a*b+b*b)/3 for a,b in zip(values,values[1:]))/SEGMENTS)
    mean,second=moments(ys)
    scale=c['rmsMm']/math.sqrt(second-mean*mean) if rough else c['heightMm']
    ys=[y*scale for y in ys];mean,second=moments(ys)
    return dict(pointsMm=[[i*c['periodMm']/SEGMENTS,y] for i,y in enumerate(ys)],
                peakMm=max(ys),meanMm=mean,rmsMm=math.sqrt(max(0,second-mean*mean)),
                periodMm=c['periodMm'],segmentsPerPeriod=SEGMENTS,
                maxLocalGradePercent=max(abs(b-a)/(c['periodMm']/SEGMENTS)*100 for a,b in zip(ys,ys[1:])))


def periodic_spec(m, case, initial):
    """Use the same connected top contour in both independent contact engines."""
    c=m.c;config=validate_terrain(m.terrain_config);wave=contour(config)
    q,h,x,z=initial;r=m.p['rw']/1000;speed=c['inputSpeedMmS']/1000
    period=config['periodMm']/1000
    # A full radius lead is conservative for every positive feature, including
    # H>=R. Delay means the leading support contour approaches the circular rim.
    front=x-r-speed*c['inputDelayS']
    count=math.ceil((speed*c['duration']+4*r)/period)+2
    if count*SEGMENTS>5000: raise ValueError('Periodic terrain exceeds 5000 segments; increase period or shorten the run.')
    points=[]
    for n in range(count):
        for d,height in wave['pointsMm'][:-1]: points.append((front-n*period-d/1000,height/1000))
    points.append((front-count*period,0.));points.reverse()
    # Finite flat tails join smoothly and cover all possible bounded wheel travel.
    extent=abs(x)+speed*c['duration']+count*period+10.
    points=[(-extent,0.)]+points+[(extent,0.)]
    segments=list(zip(points,points[1:]));xs=[p[0] for p in points]
    public=dict(polygonsMm=[],baseSegmentMm=[[-a*1000,0,0] for a in (-extent,extent)],
        contourMm=[[-a*1000,0,b*1000] for a,b in points],
        translationVelocityMmS=[-speed*1000,0,0],cornerRadiusMm=0,
        firstContactClearanceMm=r*1000,initialPossibleContactTimeS=c['inputDelayS'],
        heightMm=wave['peakMm'],periodMm=config['periodMm'],profile=config,
        statistics=wave,coordinates='Kinefold +x left / +z up, mm',
        meaning='Rigid 2D periodic proxy; average grade 0; source grade/cross-slope/soil/corridor not simulated.')
    return dict(boxes=[],base=[(-extent,0),(extent,0)],speed=speed,height=wave['peakMm']/1000,
        segments=segments,contour=points,xs=xs,terrain=public)


def surface_height(spec,time,x=0.):
    if 'segments' not in spec:
        return max([0.]+[b[2][1] for b in spec['boxes'] if b[0][0]+spec['speed']*time<=x<=b[1][0]+spec['speed']*time])
    local=x-spec['speed']*time;i=max(0,min(len(spec['segments'])-1,bisect.bisect_right(spec['xs'],local)-1))
    a,b=spec['segments'][i];u=max(0,min(1,(local-a[0])/(b[0]-a[0])))
    return a[1]+u*(b[1]-a[1])


def circle_contacts(spec,time,x,z,r):
    """Connected contour closest-point normals; cull by x, deduplicate vertices."""
    offset=spec['speed']*time;local=x-offset;xs=spec['xs']
    lo=max(0,bisect.bisect_left(xs,local-r)-1);hi=min(len(xs)-1,bisect.bisect_right(xs,local+r))
    out=[];seen=set()
    for a,b in spec['segments'][lo:hi]:
        dx,dz=b[0]-a[0],b[1]-a[1];length2=dx*dx+dz*dz
        t=max(0.,min(1.,((local-a[0])*dx+(z-a[1])*dz)/length2))
        px,pz=a[0]+t*dx,a[1]+t*dz;vx,vz=local-px,z-pz;distance=math.hypot(vx,vz)
        normal=(-dz/math.sqrt(length2),dx/math.sqrt(length2))
        signed=vx*normal[0]+vz*normal[1]
        if signed<0 and 0<t<1:gap=signed-r;n=normal
        elif distance>1e-14:gap=distance-r;n=(vx/distance,vz/distance)
        else:gap=-r;n=normal
        key=(round(px,12),round(pz,12))
        if key not in seen:out.append((gap,n,(px+offset,pz)));seen.add(key)
    return out
