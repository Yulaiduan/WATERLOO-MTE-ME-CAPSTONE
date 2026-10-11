function result = wheel_leg_ode45(values)
% WHEEL_LEG_ODE45 Independent scalar-energy suspension equation.
% Invocation: r=wheel_leg_ode45(); r=wheel_leg_ode45(configStruct).
% Inputs: SI profile (m, kg, s, N, Nm), theta degrees; optional browser JSON
% config wrapper. Outputs: struct with time, angle, chassis/hub kinematics,
% pin forces, spring/guide torques and energy; jsonencode-compatible.
% This companion supports legacy_tip/captured/direct/hooke only. New spring presets
% are integrated in Python/SciPy; unsupported topologies fail explicitly.
% Requires MATLAB/Octave ode45; neither Pymunk nor a GUI. Verified in MATLAB
% R2025b Update 3; Octave untested. Floating chassis pitch held, bilateral height,
% hub loads only. Travel events terminate before unmodelled stop/contact impact.

if nargin < 1, values = struct(); end
if isfield(values,'config'), values = values.config; end
c = struct('length',.273,'extension',.05,'radius',.2,'theta',45,...
 'theta_min',15,'theta_max',80,'upper_mass',.6,'lower_mass',.65,...
 'wheel_mass',1.5,'chassis_mass',8,'gravity',9.80665,'stiffness',20000,...
 'damping',500,'rest_length',.23,'balance_spring',true,...
 'wheel_drive_locked',false,'knee_kp',0,'knee_kd',0,'torque_limit',80,...
 'target','position','fixture','floating','load_point','hub',...
 'bias_force',0,'bias_force_x',0,'ramp_shape','quintic','wave','step',...
 'position_amplitude',.03,'start',.5,'rise',.25,'fall',.25,...
 'period',1.5,'duty',.5,'pulse_width',.7,'duration',6,'dt',.001);
m = struct('spring_integration','point_force','spring_topology','legacy_tip','spring_mode','captured',...
 'spring_transmission','direct','spring_pulley_radius',.04,'spring_direction',1,...
 'spring_input_ref',.20,'spring_coil_ref',.20,'spring_upper_fraction',.5,...
 'spring_lower_fraction',.5,'spring_bellcrank_radius',.05,...
 'spring_bellcrank_offset_deg',135,'spring_chassis_x',.12,'spring_chassis_y',.05,...
 'spring_force_law','hooke','spring_effective_free_length',0,...
 'aux_spring_enabled',false,'aux_stiffness',8000,'aux_damping',100,...
 'aux_mode','captured','aux_rest_length',.28,'aux_auto_rest',true,...
 'chassis_shape_enabled',false,'guide_pulleys_visible',false,'guide_hip_radius',.028);
mechanism_names=fieldnames(m);
for i=1:numel(mechanism_names), c.(mechanism_names{i})=m.(mechanism_names{i}); end
names = fieldnames(values);
% Legacy diagnostic fields are retained by browser profiles but have no effect.
ignored = {'amplitude','impulse','iterations','preload_force'};
for i=1:numel(names)
 name=names{i};
 if ~isfield(c,name) && ~any(strcmp(name,ignored))
   error('Unknown configuration field: %s',name);
 end
 c.(name)=values.(name);
end
assert(strcmp(c.spring_topology,'legacy_tip') && strcmp(c.spring_mode,'captured') && strcmp(c.spring_transmission,'direct') && strcmp(c.spring_force_law,'hooke'),...
 'MATLAB companion supports legacy_tip/captured/direct/hooke only. Use Python/SciPy for other spring mechanisms or force laws.');
assert(c.spring_effective_free_length>=0,'Effective spring free length must be nonnegative.');
assert(any(strcmp(c.spring_integration,{'point_force','native_legacy'})),...
 'spring_integration is a Pymunk diagnostic selector: point_force or native_legacy; it does not change this ODE.');
assert(~c.aux_spring_enabled,'MATLAB companion does not support the auxiliary ride strut. Use Python/SciPy.');
assert(islogical(c.chassis_shape_enabled) && isscalar(c.chassis_shape_enabled) && islogical(c.guide_pulleys_visible) && isscalar(c.guide_pulleys_visible),...
 'Chassis/guide visibility flags must be scalar logicals.');
assert(c.guide_hip_radius>=.005 && c.guide_hip_radius<=.1,'Guide hip radius must be between 0.005 and 0.1 metre.');
assert(strcmp(c.target,'position') && strcmp(c.fixture,'floating'),...
 'Requires floating chassis and prescribed wheel position.');
assert(strcmp(c.load_point,'hub'),'Hub loads only; contact moments unsupported.');
assert(strcmp(c.ramp_shape,'quintic'),'Quintic ramps required; linear joins are impulses.');
assert(any(strcmp(c.wave,{'step','square','pulse'})),'Unsupported position wave.');
num_names = fieldnames(c);
for i=1:numel(num_names)
 v=c.(num_names{i});
 if isnumeric(v), assert(isscalar(v) && isfinite(v),'Numerical fields must be finite scalars.'); end
end
assert(c.length>c.extension && c.extension>0 && c.radius>0,'Invalid geometry.');
assert(all([c.upper_mass,c.lower_mass,c.chassis_mass,c.wheel_mass]>0),'Masses must be positive.');
assert(c.stiffness>=0 && c.damping>=0 && c.knee_kp>=0 && c.knee_kd>=0 && c.torque_limit>0,'Invalid spring/control parameters.');
assert(c.gravity>=0 && c.duration>0 && c.duration<=20 && c.dt>0 && c.duration/c.dt<=30000,'Invalid run bounds.');
assert(c.theta_min>=3 && c.theta_min<c.theta && c.theta<c.theta_max && c.theta_max<=87,'Invalid theta range.');
assert(c.rise>=4*c.dt && c.period>0 && c.duty>0 && c.duty<1,'Invalid input timing.');
if ~strcmp(c.wave,'step')
 assert(c.fall>=4*c.dt,'Finite fall time required.');
 if strcmp(c.wave,'square'), width=c.period*c.duty; else, width=c.pulse_width; end
 assert(c.rise+c.fall<=width+1e-12,'Rise/fall must fit on-time.');
end
L=c.length; e=c.extension; q0=c.theta*pi/180;
S=1.5*L*c.upper_mass+.5*(L+e)*c.lower_mass+2*L*c.chassis_mass;
Iu=c.upper_mass*L^2/12; Il=c.lower_mass*(L+e)^2/12;
Iw=.5*c.wheel_mass*c.radius^2;
s0=sqrt(L^2+e^2+2*L*e*cos(2*q0)); J0=-2*L*e*sin(2*q0)/s0;
rest=c.rest_length;
if c.balance_spring
 assert(c.stiffness>0,'Auto balance requires positive stiffness.');
 rest=s0+S*c.gravity*cos(q0)/(c.stiffness*J0);
 assert(rest>=.005,'Cannot balance selected spring; increase stiffness or choose manual length.');
end
opts=odeset('RelTol',1e-9,'AbsTol',1e-11,'MaxStep',min(.01,4*c.dt),'Events',@stops);
time=unique([0:c.dt:c.duration,c.duration]);
[t,y,te,~,ie]=ode45(@rhs,time,[q0;0],opts);
n=numel(t);
result=struct('backend','matlab-ode45','config',c,'actual_rest_length',rest,...
 't',t,'theta_deg',y(:,1)*180/pi,'theta_speed',y(:,2),...
 'position_command',zeros(n,1),'chassis_displacement_mm',zeros(n,1),...
 'chassis_vy',zeros(n,1),'chassis_ay',zeros(n,1),'hub_vy',zeros(n,1),...
 'hub_ay',zeros(n,1),'driver_force',zeros(n,1),'j1_force',zeros(n,1),...
 'j2_force',zeros(n,1),'j3_force',zeros(n,1),'spring_tension',zeros(n,1),...
 'spring_knee_moment',zeros(n,1),'guide_hip_reaction',zeros(n,1),...
 'actuator_torque',zeros(n,1),'mechanical_energy_J',zeros(n,1),...
 'angular_balance_error_Nm',zeros(n,1),'stop_event_time',te,...
 'stop_event_index',ie,'scope','Legacy hip-to-tip captured direct spring only. Experimental bilateral support; stops terminate before impact. MATLAB R2025b Update 3 tested; Octave untested.');
for i=1:n
 q=y(i,1); v=y(i,2); sn=sin(q); cs=cos(q);
 state_dot=rhs(t(i),y(i,:)'); a=state_dot(2);
 [z,zv,za]=base(t(i)); [~,~,s,J,elastic,damper,tau]=terms(q,v);
 A=[0;z+2*L*sn]; B=[L*cs;z+L*sn]; C=[0;z]; E=[(L+e)*cs;z+(L+e)*sn];
 U=[L/2*cs;z+1.5*L*sn]; D=[(L+e)/2*cs;z+(L+e)/2*sn];
 va=[0;zv+2*L*cs*v]; aa=[0;za+2*L*(cs*a-sn*v^2)];
 vu=[-L/2*sn*v;zv+1.5*L*cs*v]; au=[-L/2*(cs*v^2+sn*a);za+1.5*L*(cs*a-sn*v^2)];
 vd=[-(L+e)/2*sn*v;zv+(L+e)/2*cs*v]; ad=[-(L+e)/2*(cs*v^2+sn*a);za+(L+e)/2*(cs*a-sn*v^2)];
 gravity=[0;-c.gravity]; fs=-(elastic+damper)*(E-A)/s;
 f1=-(c.chassis_mass*(aa-gravity)+fs); f2=f1-c.upper_mass*(au-gravity);
 f3=f2+fs-c.lower_mass*(ad-gravity);
 driver=c.wheel_mass*([0;za]-gravity)-[c.bias_force_x;c.bias_force]-f3;
 wheel_reaction=-Iw*a*c.wheel_drive_locked;
 guide_u=-Iu*a-cross2(A-U,f1)-cross2(B-U,-f2)+tau;
 guide_l=Il*a-cross2(B-D,f2)-cross2(C-D,-f3)-cross2(E-D,fs)-tau-wheel_reaction;
 result.position_command(i)=z; result.chassis_displacement_mm(i)=1000*(A(2)-2*L*sin(q0));
 result.chassis_vy(i)=va(2); result.chassis_ay(i)=aa(2); result.hub_vy(i)=zv; result.hub_ay(i)=za;
 result.driver_force(i)=driver(2); result.j1_force(i)=norm(f1); result.j2_force(i)=norm(f2); result.j3_force(i)=norm(f3);
 result.spring_tension(i)=elastic+damper; result.spring_knee_moment(i)=cross2(E-B,fs);
 result.guide_hip_reaction(i)=-(guide_u+guide_l); result.actuator_torque(i)=tau;
 result.angular_balance_error_Nm(i)=guide_u-guide_l;
 kinetic=.5*(c.chassis_mass*(va'*va)+c.upper_mass*(vu'*vu)+c.lower_mass*(vd'*vd)+c.wheel_mass*zv^2);
 kinetic=kinetic+.5*(Iu+Il+Iw*c.wheel_drive_locked)*v^2;
 result.mechanical_energy_J(i)=kinetic+c.gravity*(c.chassis_mass*A(2)+c.upper_mass*U(2)+c.lower_mass*D(2)+c.wheel_mass*z)+.5*c.stiffness*(s-rest)^2;
end

 function dy=rhs(t,state)
  q=state(1); v=state(2); [M,Mp,~,J,elastic,damper,tau]=terms(q,v);
  [~,~,za]=base(t);
  a=(-(elastic+damper)*J+2*tau-S*cos(q)*(c.gravity+za)-.5*Mp*v^2)/M;
  dy=[v;a];
 end
 function [M,Mp,s,J,elastic,damper,tau]=terms(q,v)
  M=Iu+Il+Iw*c.wheel_drive_locked+c.upper_mass*((L/2)^2*sin(q)^2+(1.5*L)^2*cos(q)^2)+c.lower_mass*((L+e)/2)^2+4*c.chassis_mass*L^2*cos(q)^2;
  Mp=(c.upper_mass*((L/2)^2-(1.5*L)^2)-4*c.chassis_mass*L^2)*sin(2*q);
  s=sqrt(L^2+e^2+2*L*e*cos(2*q)); J=-2*L*e*sin(2*q)/s;
  elastic=c.stiffness*(s-rest); damper=c.damping*J*v;
  raw=c.knee_kp*(2*q0-2*q)-c.knee_kd*2*v; tau=min(c.torque_limit,max(-c.torque_limit,raw));
 end
 function [z,v,a]=base(t)
  elapsed=t-c.start; A=c.position_amplitude;
  if elapsed<0, z=0;v=0;a=0;return;end
  if strcmp(c.wave,'step'), [z,v,a]=ramp(elapsed,c.rise); z=A*z;v=A*v;a=A*a;return;end
  if strcmp(c.wave,'square'), width=c.period*c.duty;elapsed=mod(elapsed,c.period);else,width=c.pulse_width;end
  if elapsed>=width,z=0;v=0;a=0;return;end
  if elapsed<c.rise,[z,v,a]=ramp(elapsed,c.rise);z=A*z;v=A*v;a=A*a;
  elseif elapsed<=width-c.fall,z=A;v=0;a=0;
  else,[z,v,a]=ramp(elapsed-(width-c.fall),c.fall);z=A*(1-z);v=-A*v;a=-A*a;end
 end
 function [z,v,a]=ramp(t,duration)
  if t<=0,z=0;v=0;a=0;return;end
  if t>=duration,z=1;v=0;a=0;return;end
  u=t/duration;z=10*u^3-15*u^4+6*u^5;
  v=(30*u^2-60*u^3+30*u^4)/duration;a=(60*u-180*u^2+120*u^3)/duration^2;
 end
 function [value,isterminal,direction]=stops(~,state)
  value=[state(1)-c.theta_min*pi/180;c.theta_max*pi/180-state(1)];
  isterminal=[1;1];direction=[-1;-1];
 end
 function v=cross2(a,b),v=a(1)*b(2)-a(2)*b(1);end
end
