/** Design-field dictionary used by both controls and searchable conventions.
 * Loaded as a browser script before app.js. Values use mm/deg/kg/N/Nm; UI only.
 * Definitions describe this experimental fixed-hip planar model, not hardware.
 */
globalThis.KinefoldFields = [
  {id:'geometry',title:'Geometry',note:'Links, pulleys & working range',sections:[
    ['Links & wheel',[
      ['L2','L₂','Upper link','mm',300,1,5000,'Hip A to knee B centre distance; Link 2 (femur).'],
      ['L3','L₃','Lower link','mm',300,1,5000,'Knee B to wheel centre C; Link 3 (tibia).'],
      ['rw','r_w','Wheel radius','mm',200,1,2000,'Wheel outer radius. Contact patch P is r_w from C.']]],
    ['Pulley pitch radii',[
      ['ra','r_a','Guide · hip','mm',50,.1,1000,'Guide pulley a at A, fixed to the chassis; shares the a–b belt with b.'],
      ['rb','r_b','Guide · knee','mm',25,.1,1000,'Guide pulley b at B, fixed to the tibia. q_ab = r_a/r_b.'],
      ['rc','r_c','Drive · hip','mm',35,.1,1000,'Independently driven pulley c at A; input of belt c–d.'],
      ['rd','r_d','Drive · knee','mm',35,.1,1000,'Pulley d at B, rigidly coaxial with e and independent of the links. q_dc = r_d/r_c.'],
      ['re','r_e','Output · knee','mm',25,.1,1000,'Pulley e at B, rigidly attached to d; input of belt e–f.'],
      ['rf','r_f','Output · wheel','mm',25,.1,1000,'Pulley f at C, fixed to the wheel. q_fe = r_f/r_e.']]],
    ['Mounting & motion',[
      ['alpha','α','Chassis pitch','°',0,0,45,'Clockwise mounting pitch in the original u/v plane; local +v tilts toward −x as α increases.'],
      ['phi0','φ₀','Lower-link phase','°',0,0,30,'Fixed lower-link phase in θ₃ = φ₀ + (180°−θ₂)(q_ab−1).'],
      ['te','θ₂ᵉ','Extension stop','°',100,90,270,'Lower working θ₂ endpoint and zero for displacement and drive/wheel angle changes.'],
      ['tc','θ₂ᶜ','Compression stop','°',165,90,270,'Upper working θ₂ endpoint. Names do not guarantee monotonic height in arbitrary geometry.']]]]},
  {id:'suspension',title:'Suspension',note:'Constant support & cable routing',sections:[
    ['Spring & attachment',[
      ['springK','k','Spring rate','N/mm',8,0,1000,'V4 linear coil rate. F_s = max(0, p₀ + k[c−c₀]); ignored by the ideal constant-force law.'],
      ['p0','p₀','Reference force','N',330.8692828089511,0,100000,'V4 cable force at θ₂ = 90°; a force, not extra predeflection. For the ideal constant-force law this is the cable force at every pose.'],
      ['hornR','r_h','Horn radius','mm',62.22694951186731,.1,2000,'Distance A to cable pin D, rotating rigidly with the femur.'],
      ['nu','ν','Horn offset','°',0,-360,360,'Angular offset of A→D from the B→A vector. D = r_h[cos(θ₂+ν), sin(θ₂+ν)] in u/v.'],
      ['Su','S_u','Idler · local u','mm',9.387776728149294,-2000,2000,'Fixed idler centre S coordinate along local +u (rearward at α = 0).'],
      ['Sv','S_v','Idler · local v','mm',100,-2000,2000,'Fixed idler centre S coordinate along local +v (up at α = 0).'],
      ['rs','r_s','Idler radius','mm',10,0,1000,'Finite idler pitch radius; exact tangent span plus clockwise wrap. Zero is an ideal point limit.']]]]},
  {id:'loading',title:'Loadings & preloads',note:'Mass, gravity & prescribed forces',sections:[
    ['Mass & gravity',[
      ['m1','m₁','Chassis / corner','kg',8.75,0,10000,'Mass supported by this single leg at fixed hip A. This is a corner mass, not a full vehicle mass.'],
      ['m2','m₂','Upper link','kg',0,0,1000,'Uniform upper-link mass acting at the midpoint of A–B.'],
      ['m3','m₃','Lower link','kg',0,0,1000,'Uniform lower-link mass acting at the midpoint of B–C.'],
      ['m5','m₅','Knee compound','kg',0,0,1000,'Compound pulley assembly mass at B. There is no separate m₄ in this model.'],
      ['m6','m₆','Wheel assembly','kg',0,0,1000,'Wheel assembly mass at C. Masses are static loads; no inertia is integrated.'],
      ['g','g','Gravity','m/s²',9.81,0,100,'Gravity magnitude; gravitational force is [0, 0, −m g].']]],
    ['Applied wheel load',[
      ['Fx','F_x','Forward force','N',0,-100000,100000,'Signed global +x wheel-contact force. Only active in Global components mode.'],
      ['Fz','F_z','Upward force','N',85.8375,-100000,100000,'Signed global +z wheel-contact force; prescribed independently of weight in Global mode.'],
      ['Fn','F_n','Normal force','N',85.8375,-100000,100000,'Signed inward contact normal. Positive points from P toward C. Active in Contact components mode.'],
      ['Ft','F_t','Tangential force','N',0,-100000,100000,'Signed tangent force chosen so positive F_t applies a +y wheel moment. At β = 0, positive F_t points toward −x.'],
      ['beta','β','Contact angle','°',0,0,90,'Patch direction from −z toward +x; P = C + r_w[sin β, 0, −cos β]. This sets a load application point, not terrain contact.']]],
    ['Slack-side belt preloads',[
      ['Tab0','T_ab,0','Guide belt','N',0,0,100000,'Minimum slack-side tension of belt a–b. Tight side adds the torque-transmitting difference.'],
      ['Tcd0','T_cd,0','Drive belt','N',0,0,100000,'Minimum slack-side tension of belt c–d. Changes bearing loads, not ideal motor torque.'],
      ['Tef0','T_ef,0','Wheel belt','N',0,0,100000,'Minimum slack-side tension of belt e–f. All belts are ideal, open and nonslipping.']]]]}
];
