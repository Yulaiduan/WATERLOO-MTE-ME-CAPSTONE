"""Build bounded periodic experimental terrain from a versioned sheet snapshot.

Imported by contact engines/profile validation; no physics engine dependency.
Inputs: terrain-v1/v2 JSON in mm, source ID/revision, seed, variation and grade%.
Outputs: exact piecewise-linear contour/statistics, SI moving collision segments.
Limitations: rigid 2D longitudinal grade proxy; no soil, snow or roll model.
"""
import bisect
import json
import math
from pathlib import Path

CATALOG = json.loads(Path(__file__).with_name('terrain-catalog.json').read_text(encoding='utf-8'))
SEGMENTS = 96
KEYS = {'schema','catalogRevision','profileId','severity','representation','periodMm','heightMm','rmsMm'}
V2_KEYS = KEYS | {'seed','variationPercent','gradePercent'}


def validate_terrain(value):
    v2=isinstance(value,dict) and value.get('schema')=='kinefold/terrain-v2'
    if not isinstance(value, dict) or set(value) != (V2_KEYS if v2 else KEYS):
        raise ValueError('terrainConfig requires exactly ' + ', '.join(sorted(KEYS)))
    if value['schema'] not in ('kinefold/terrain-v1','kinefold/terrain-v2') or value['catalogRevision'] != CATALOG['revision']:
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
    if v2:
        if type(value['seed']) not in (int,float) or not math.isfinite(value['seed']) or not 0<=value['seed']<=0xffffffff or value['seed']!=int(value['seed']):
            raise ValueError('Terrain seed must be a uint32 integer.')
        for key,lo,hi in [('variationPercent',0.,50.),('gradePercent',-100.,100.)]:
            if type(value[key]) not in (int,float) or not math.isfinite(value[key]) or not lo<=value[key]<=hi:
                raise ValueError(key+' is outside its finite terrain range.')
    return dict(value)


def contour(value,cycle=0):
    c=validate_terrain(value);rough=c['representation']=='roughness'
    if c['schema']=='kinefold/terrain-v2':return random_contour(c,cycle)
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
    c=m.c;config=validate_terrain(m.terrain_config)
    if config['schema']=='kinefold/terrain-v2':return varied_spec(m,case,initial)
    wave=contour(config)
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


def random_unit(seed,cycle,channel):
    """Stateless uint32 mixer; signed cycle maps to two's-complement uint32."""
    mask=0xffffffff
    x=(int(seed)^((cycle&mask)*0x9e3779b1&mask)^(channel*0x85ebca77&mask))&mask
    x^=x>>16;x=x*0x7feb352d&mask;x^=x>>15;x=x*0x846ca68b&mask;x^=x>>16
    return x/4294967296.


def moments(points):
    """Exact spatial mean/mean-removed RMS for piecewise-linear ordinates."""
    width=points[-1][0]-points[0][0];mean=second=0.
    for (x,a),(y,b) in zip(points,points[1:]):
        w=(y-x)/width;mean+=(a+b)/2*w;second+=(a*a+a*b+b*b)/3*w
    return mean,math.sqrt(max(0,second-mean*mean))


def random_contour(c,cycle):
    if type(cycle) is not int or not -2147483648<=cycle<=2147483647:raise ValueError('Cycle index must be a signed int32.')
    base={k:v for k,v in c.items() if k in KEYS};base['schema']='kinefold/terrain-v1'
    old=contour(base);variation=c['variationPercent']/100;period=c['periodMm']
    if variation==0:
        heights=[p[1] for p in old['pointsMm']];center=.5;width=1. if c['representation']=='roughness' else .5;asymmetry=.5;amplitude=1.
    else:
        rand=lambda channel:2*random_unit(c['seed'],cycle,channel)-1
        rough=c['representation']=='roughness';guard=2/SEGMENTS
        width=min(1-2*guard,(1-variation*(.4+.2*rand(2))) if rough else .5*(1+variation*.4*rand(2)))
        center=max(width/2+guard,min(1-width/2-guard,.5+.16*variation*rand(1)))
        asymmetry=.5+.25*variation*rand(3);amplitude=1+variation*rand(4)
        heights=[]
        for i in range(SEGMENTS+1):
            t=(i/SEGMENTS-center+width/2)/width
            if t<=0 or t>=1:heights.append(0.);continue
            u=t/(2*asymmetry) if t<=asymmetry else .5+(t-asymmetry)/(2*(1-asymmetry))
            heights.append(.5*(1-math.cos(2*math.pi*u)))
        unit_points=[[i*period/SEGMENTS,y] for i,y in enumerate(heights)]
        scale=(c['rmsMm']/moments(unit_points)[1] if rough else c['heightMm']/max(heights))*amplitude
        heights=[y*scale for y in heights]
    rough_points=[[i*period/SEGMENTS,y] for i,y in enumerate(heights)]
    grade=c['gradePercent']/100
    baseline=[[x,grade*(cycle*period+x)] for x,_ in rough_points]
    points=[[x,y+baseline[i][1]] for i,(x,y) in enumerate(rough_points)]
    mean,rms=moments(rough_points)
    return dict(pointsMm=points,roughnessPointsMm=rough_points,baselinePointsMm=baseline,
        peakMm=max(heights),meanMm=mean,rmsMm=rms,periodMm=period,segmentsPerPeriod=SEGMENTS,
        maxLocalGradePercent=max(abs(b[1]-a[1])/(b[0]-a[0])*100 for a,b in zip(points,points[1:])),
        gradePercent=c['gradePercent'],gradeDegrees=math.degrees(math.atan(grade)),cycleIndex=cycle,
        seed=c['seed'],variationPercent=c['variationPercent'],shape=dict(centerFraction=center,widthFraction=width,peakFraction=asymmetry,amplitudeFactor=amplitude))


def sequence(value,count=3,start_cycle=0):
    c=validate_terrain(value)
    if type(count) is not int or not 1<=count<=52:raise ValueError('Sequence count must be 1–52 cells.')
    if type(start_cycle) is not int or not -2147483648<=start_cycle<=2147483647-count+1:raise ValueError('Sequence start must keep all cycle indices within int32.')
    cells=[contour(c,i) for i in range(start_cycle,start_cycle+count)];points=[];rough=[];baseline=[]
    for n,cell in enumerate(cells):
        cycle=start_cycle+n
        for i,(x,y) in enumerate(cell['pointsMm']):
            if n and i==0:continue
            absolute=cycle*c['periodMm']+x;points.append([absolute,y])
            rough.append([absolute,cell.get('roughnessPointsMm',cell['pointsMm'])[i][1]])
            baseline.append([absolute,cell['baselinePointsMm'][i][1] if 'baselinePointsMm' in cell else 0.])
    mean,rms=moments(rough)
    return dict(pointsMm=points,roughnessPointsMm=rough,baselinePointsMm=baseline,cells=cells,cellCount=count,startCycle=start_cycle,spanMm=count*c['periodMm'],
        peakMm=max(p[1] for p in rough),meanMm=mean,rmsMm=rms,detrendedRmsMm=rms,
        minHeightMm=min(p[1] for p in points),maxHeightMm=max(p[1] for p in points),
        gradePercent=c.get('gradePercent',0.),gradeDegrees=math.degrees(math.atan(c.get('gradePercent',0)/100)),
        seed=c.get('seed'),variationPercent=c.get('variationPercent',0.),periodMm=c['periodMm'])


def varied_spec(m,case,initial):
    c=m.c;config=validate_terrain(m.terrain_config);q,h,x,z=initial
    r=m.p['rw']/1000;speed=c['inputSpeedMmS']/1000;period=config['periodMm']/1000;grade=config['gradePercent']/100
    front=x-r-speed*c['inputDelayS'];count=math.ceil((speed*c['duration']+4*r)/period)+2
    if count*SEGMENTS>5000:raise ValueError('Periodic terrain exceeds 5000 segments; increase period or shorten the run.')
    realized=sequence(config,count);points=[]
    for n,cell in enumerate(realized['cells']):
        for d,height in cell['roughnessPointsMm'][:-1]:
            u=front-n*period-d/1000;points.append((u,-grade*(u-x)+height/1000))
    last=front-count*period;points.append((last,-grade*(last-x)));points.reverse()
    extent=abs(x)+speed*c['duration']+count*period+10.
    points=[(-extent,-grade*(-extent-x))]+points+[(extent,-grade*(extent-x))]
    segments=list(zip(points,points[1:]));xs=[p[0] for p in points]
    stats={key:realized[key] for key in ('peakMm','meanMm','rmsMm','detrendedRmsMm','gradePercent','gradeDegrees','seed','variationPercent','periodMm')}
    stats.update(cellCount=count,startCycle=0,spanMm=count*config['periodMm'],statisticsWindow='Complete generated roughness cells, excluding straight supporting tails and initial lead; not the wheel-sampled path window.')
    stats['cells']=[{key:cell[key] for key in ('cycleIndex','peakMm','meanMm','rmsMm','maxLocalGradePercent','shape')} for cell in realized['cells']]
    public=dict(polygonsMm=[],baseSegmentMm=[[-u*1000,0,-grade*(u-x)*1000] for u in (-extent,extent)],
        contourMm=[[-u*1000,0,height*1000] for u,height in points],translationVelocityMmS=[-speed*1000,0,0],
        cornerRadiusMm=0,firstContactClearanceMm=r*1000,initialPossibleContactTimeS=c['inputDelayS'],
        heightMm=realized['peakMm'],periodMm=config['periodMm'],profile=config,statistics=stats,
        gradePercent=config['gradePercent'],gradeDegrees=realized['gradeDegrees'],referenceWheelWorldXMm=-x*1000,
        seed=config['seed'],variationPercent=config['variationPercent'],coordinates='Kinefold +x left / +z up, mm',
        meaning='Seeded rigid 2D terrain with signed longitudinal grade. Positive grade rises toward world +x; cross-slope/soil/snow/water/corridor not simulated.')
    return dict(boxes=[],base=[points[0],points[-1]],speed=speed,height=realized['peakMm']/1000,
        segments=segments,contour=points,xs=xs,terrain=public,grade=grade,referenceWheelSourceX=x)


def raised_contact(spec,time,point):
    """A roughness contact above its inclined baseline, preserving v1 meaning."""
    baseline=-spec.get('grade',0)*(point[0]-spec['speed']*time-spec.get('referenceWheelSourceX',0))
    return point[1]>baseline+1e-7
