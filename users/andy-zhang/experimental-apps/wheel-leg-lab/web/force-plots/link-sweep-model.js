/** Equal-link sizing study. Import in the browser or node tests.
 * Inputs: mm, degrees, vertical force N; outputs: geometric candidates and
 * hip-equivalent / relative-knee static torque N m. Ideal 2:1 guide, constant
 * net vertical load, no link mass, spring law, dynamics or hardware validation.
 */
export const rad = degrees => degrees * Math.PI / 180;
export const deg = radians => radians * 180 / Math.PI;
const acos = x => Math.acos(Math.max(-1, Math.min(1, x)));
export const height = (L, q) => 2 * L * Math.cos(q);
export const defaultSweep = () => ({ diameter:400, nominal:true, start:{value:20,unit:'mm'},
  rom:{value:200,unit:'mm'}, end:{value:20,unit:'mm'}, previewLink:240,
  minLink:100,maxLink:600,linkStep:5,angleStep:1,load:100,shaft:'hip',
  weighting:'travel',objective:'peak',chassisDepth:200,airGap:20 });

export function validate(c) {
  for (const k of ['diameter','previewLink','minLink','maxLink','linkStep','angleStep','load'])
    if (!Number.isFinite(c[k]) || c[k] <= 0) throw Error(`${k} must be a positive finite number.`);
  for (const k of ['chassisDepth','airGap'])
    if (!Number.isFinite(c[k]) || c[k] < 0) throw Error(`${k} must be a finite nonnegative distance.`);
  for (const k of ['start','rom','end']) {
    if (!c[k] || !['mm','deg'].includes(c[k].unit) || !Number.isFinite(c[k].value) || c[k].value < 0)
      throw Error(`${k}: enter a nonnegative distance or angle.`);
    if (c[k].unit === 'deg' && c[k].value >= 90) throw Error(`${k}: use less than 90°.`);
  }
  if (!c.nominal && c.rom.value <= 0) throw Error('ROM must be greater than zero.');
  if (typeof c.nominal !== 'boolean') throw Error('Nominal ROM must be true or false.');
  if (c.minLink > c.maxLink) throw Error('Minimum link must not exceed maximum link.');
  if (!['hip','knee'].includes(c.shaft) || !['travel','angle'].includes(c.weighting) || !['peak','mean','flat'].includes(c.objective))
    throw Error('Unknown torque coordinate, averaging method or ranking objective.');
  if ((Math.floor((c.maxLink-c.minLink)/c.linkStep)+2)*(Math.ceil(90/c.angleStep)+2)>150000)
    throw Error('Sweep exceeds 150,000 possible candidates. Increase the link or angle step.');
}

export function limits(c,L) {
  const startMM = c.start.unit === 'mm' ? c.start.value : 2*L*(1-Math.cos(rad(c.start.value)));
  const endMM = c.end.unit === 'mm' ? c.end.value : 2*L*Math.sin(rad(c.end.value));
  const clearanceMM = Math.max(0,c.chassisDepth+c.airGap-c.diameter/2);
  if (startMM >= 2*L || Math.max(endMM,clearanceMM) >= 2*L) return null;
  const qMin = acos(1-startMM/(2*L));
  const qMax = acos(Math.max(endMM,clearanceMM)/(2*L));
  return qMax > qMin ? {qMin,qMax,startMM,endMM,clearanceMM} : null;
}

export function endAngle(c,L,qStart) {
  if (!c.nominal && c.rom.unit === 'deg') return qStart+rad(c.rom.value);
  const travel = c.nominal ? c.diameter/2 : c.rom.value;
  const remaining = height(L,qStart)-travel;
  return remaining < -1e-8 ? Infinity : acos(remaining/(2*L));
}

export function convert(c,L,key,toUnit) {
  validate(c);
  const value = c[key].value, from = c[key].unit;
  if (from === toUnit) return value;
  if (!['mm','deg'].includes(toUnit)) throw Error('Unknown conversion unit.');
  if (key==='start') {
    if (from==='mm' && value>2*L) throw Error('Start buffer exceeds full leg height.');
    return from==='mm' ? deg(acos(1-value/(2*L))) : 2*L*(1-Math.cos(rad(value)));
  }
  if (key==='end') {
    if (from==='mm' && value>2*L) throw Error('End buffer exceeds full leg height.');
    return from==='mm' ? deg(Math.asin(value/(2*L))) : 2*L*Math.sin(rad(value));
  }
  const bound=limits(c,L);
  if (!bound) throw Error('Reference link has no usable buffer window.');
  const qStart=bound.qMin;
  if (from==='mm') {
    const qEnd=endAngle({...c,nominal:false},L,qStart);
    if (!Number.isFinite(qEnd) || qEnd>Math.PI/2) throw Error('ROM exceeds reference link travel.');
    return deg(qEnd-qStart);
  }
  if (qStart+rad(value)>Math.PI/2) throw Error('ROM exceeds reference link angle range.');
  return height(L,qStart)-height(L,qStart+rad(value));
}

export function metrics(c,L,a,b) {
  const span=b-a, travel=height(L,a)-height(L,b);
  const scale=c.load*(c.shaft==='hip'?2:1)*L/1000;
  let mean,second;
  if (c.weighting==='angle') {
    mean=scale*(Math.cos(a)-Math.cos(b))/span;
    second=scale**2*(.5-(Math.sin(2*b)-Math.sin(2*a))/(4*span));
  } else {
    // dy = 2L sin(q)dq; integrate tau*dy and tau^2*dy exactly.
    const denominator=Math.cos(a)-Math.cos(b);
    mean=scale*(span/2-(Math.sin(2*b)-Math.sin(2*a))/4)/denominator;
    const primitive=q=>-Math.cos(q)+Math.cos(q)**3/3;
    second=scale**2*(primitive(b)-primitive(a))/denominator;
  }
  const rms=Math.sqrt(Math.max(0,second)),sd=Math.sqrt(Math.max(0,second-mean**2));
  return {link:L,startDeg:deg(a),endDeg:deg(b),thetaStartDeg:90-deg(a),thetaEndDeg:90-deg(b),
    travel,startMM:2*L-height(L,a),endMM:height(L,b),
    groundGap:height(L,b)+c.diameter/2-c.chassisDepth,
    min:scale*Math.sin(a),peak:scale*Math.sin(b),mean,rms,cv:sd/mean,
    peakMean:scale*Math.sin(b)/mean,ratio:L/c.diameter};
}

export function compare(c,a,b) {
  const score=x=>c.objective==='flat'?x.cv:x[c.objective];
  return score(a)-score(b) || a.peak-b.peak || a.link-b.link || a.startDeg-b.startDeg;
}

export function sweep(c) {
  validate(c);
  const rows=[],envelope=[];
  const n=Math.floor((c.maxLink-c.minLink)/c.linkStep+1e-9);
  const lengths=Array.from({length:n+1},(_,i)=>c.minLink+i*c.linkStep);
  if (Math.abs(lengths.at(-1)-c.maxLink)>1e-8) lengths.push(c.maxLink);
  for (const L of lengths) {
    const bound=limits(c,L);if (!bound) continue;
    const {qMin,qMax}=bound;
    // Include both limiting placements, avoiding missed feasible boundary windows.
    let lastStart;
    if (!c.nominal && c.rom.unit==='deg') lastStart=qMax-rad(c.rom.value);
    else {
      const required=(c.nominal?c.diameter/2:c.rom.value)+height(L,qMax);
      if (required>height(L,qMin)+1e-8) continue;
      lastStart=acos(required/(2*L));
    }
    if (lastStart<qMin-1e-10) continue;
    lastStart=Math.max(qMin,lastStart);
    const starts=[];
    for (let i=0;i<=Math.floor((lastStart-qMin)/rad(c.angleStep)+1e-9);i++) starts.push(qMin+i*rad(c.angleStep));
    if (Math.abs(starts.at(-1)-lastStart)>1e-9) starts.push(lastStart);
    let best=null;
    for (const a of starts) {
      const b=endAngle(c,L,a);
      if (!Number.isFinite(b)||b>qMax+1e-9||b<=a+1e-10) continue;
      const row=metrics(c,L,a,b);rows.push(row);
      if (!best || compare(c,row,best)<0) best=row;
    }
    if (best) envelope.push(best);
  }
  rows.sort((a,b)=>compare(c,a,b));
  return {rows,envelope,best:rows[0]??null,boundary:!!rows[0] &&
    (Math.abs(rows[0].link-c.minLink)<1e-8||Math.abs(rows[0].link-c.maxLink)<1e-8)};
}
