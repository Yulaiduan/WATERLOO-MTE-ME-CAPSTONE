/** Map Jonathan parameter exports into the existing SI bench profile.
 * Import from app.js/library.js; inputs v1/v2 mm/deg/kg/N/Nm JSON.
 * Outputs explicit existing/generalized solver fields; base spring/input stays intact.
 * Limits: zero-mass statics imports remain zero and require positive dynamic masses
 * before Run; fixed-A loads do not become an automatically solved ground contact.
 */
export function fromJon(data){
 if(!['general-vsl/v1-kinematics','general-vsl/v2-quasi-static'].includes(data?.schema)||!data.parameters)throw Error('Unsupported Jonathan parameter file.');
 const p=data.parameters,out={linkage_design:'general',fixture:'floating',target:'position',ramp_shape:'quintic',wave:'step',load_point:'contact',wheel_drive_locked:false,extension:0};
 const dimensions={L2:'length',L3:'lower_length',ra:'guide_hip_radius',rb:'guide_knee_radius',rc:'drive_hip_radius',rd:'drive_knee_radius',re:'drive_output_radius',rf:'wheel_pulley_radius',rw:'radius',r5I:'compound_inertia_radius'};
 for(const [source,target] of Object.entries(dimensions))if(p[source]!==undefined){if(typeof p[source]!=='number'||!Number.isFinite(p[source])||p[source]<=0)throw Error('Jonathan '+source+' must be positive millimetres.');out[target]=p[source]/1000;}
 for(const [source,target] of Object.entries({alpha:'mount_angle',phi0:'link_phase',m1:'chassis_mass',m2:'upper_mass',m3:'lower_mass',m5:'compound_mass',m6:'wheel_mass',g:'gravity',beta:'contact_beta',Fn:'contact_normal_force',Ft:'contact_tangent_force',Fy:'bias_force_x',Fz:'bias_force',Tab0:'belt_preload_ab',Tcd0:'belt_preload_cd',Tef0:'belt_preload_ef'}))if(p[source]!==undefined)out[target]=p[source];
 out.contact_force_mode=p.loadMode??'nt';out.theta_min=180-p.tc;out.theta_max=180-p.te;out.theta=180-(data.theta2??((p.te+p.tc)/2));
 if(data.ranges?.beta){out.contact_beta_min=data.ranges.beta.min;out.contact_beta_max=data.ranges.beta.max;}
 for(const [id,q,a,b] of [['lengths','q23','L2','L3'],['guide','qab','ra','rb'],['cd','qcd','rc','rd'],['ef','qef','re','rf']]){
  const selected=data.driven?.[q]??q;if(![q,a,b].includes(selected))throw Error('Invalid Jonathan driven dimension.');out['linkage_driven_'+id]=selected===q?'ratio':selected===a?'first':'second';
 }
 return out;
}
