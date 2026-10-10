# Independent suspension mathematics

Owner: Andy Zhang. Updated: 2026-10-10. Status: experimental.

The browser Mathematical Model tab runs [Python/SciPy](../math_model.py), independent of Pymunk. [wheel_leg_ode45.m](wheel_leg_ode45.m) provides the same scalar energy equation, automatic spring equilibrium and smooth wheel-position input for MATLAB/Octave. MATLAB R2025b Update 3, the Python implementation and Pymunk refinement comparison have been tested. Octave is untested.

The shape coordinate is theta from horizontal, in radians internally. The knee opening is twice theta. World y points up: wheel hub `C=(0,z)`, knee `B=(L cos(theta),z+L sin(theta))`, chassis `A=(0,z+2L sin(theta))`, and the 50 mm default extension tip `E=((L+e)cos(theta),z+(L+e)sin(theta))`. The spring runs from A to E. The default wheel radius is 200 mm. Chassis pitch is held, while vertical motion responds through the spring and optional knee impedance.

Write `s²=L²+e²+2Le cos(2theta)` and `J=ds/dtheta=-2Le sin(2theta)/s`. The independent ODE is

```text
M(theta) theta_ddot + 0.5 M'(theta) theta_dot²
  + S cos(theta) (g + z_ddot)
  = -[k(s-rest) + c J theta_dot] J + 2 tau_knee

S = 1.5 m_upper L + 0.5 m_lower (L+e) + 2 m_chassis L
M = I_upper + I_lower [+ I_wheel when wheel locked]
  + m_upper [(L/2)² sin²(theta)+(3L/2)² cos²(theta)]
  + m_lower [(L+e)/2]² + 4 m_chassis L² cos²(theta)
```

Automatic free length is calculated from static equilibrium without building a rigid-body fixture. The wheel mass contributes to required moving-support force and energy, while prescribed wheel translation contributes no additional shape inertia. A free wheel has no applied moment and stays at zero spin. Locking it to the lower link adds its rotational inertia to M. Hub force biases change moving-support reaction but do no shape-coordinate work.

Joint loads are reconstructed from each body's translational balance. Upper and lower angular balances independently recover the guide torque; their difference checks the scalar ODE. Python exports instantaneous force/torque, joint/chassis/wheel velocity and acceleration, mechanical energy and power. Its energy-work diagnostic uses trapezoidal quadrature of output samples, so it also depends on output resolution. Exact zero positional/phase drift follows from prescribed analytical geometry and is not a rigid-body solver impulse check.

From the app root:

```sh
.venv/Scripts/python.exe math_model.py --output .preview/math-run.json
.venv/Scripts/python.exe math_model.py --config profile.json --output .preview/math-run.json
.venv/Scripts/python.exe -m unittest -v test_math_model
```

In MATLAB/Octave, with this folder on the path:

```matlab
r = wheel_leg_ode45();
plot(r.t, r.chassis_displacement_mm);
% Optional: use an exported browser profile (raw config or config wrapper).
p = jsondecode(fileread('profile.json'));
if isfield(p,'config'), p = p.config; end
r = wheel_leg_ode45(p);
fid = fopen('math-run.json','w');
fprintf(fid,'%s',jsonencode(r)); fclose(fid);
```

Both models require a floating chassis, hub loading and smooth quintic position step/square/pulse inputs. Linear-ramp velocity jumps, fixed fixtures and force excitation are rejected. Travel-limit events end the mathematical run before an unmodelled impact; no stop-contact force is invented. The position fixture is bilateral: a negative driver reaction means real ground could lose contact. There is no unilateral tire contact, belt elasticity, structural stress or hardware calibration. Defaults are editable illustrations, not accepted requirements.

Python verification includes equilibrium, geometry-based preload, energy conservation/damping, actuator clipping, wheel-lock inertia, stop termination, JSON finiteness and independent import. At the mild default 30 mm / 250 ms step, theta at 1.2 s is 48.02864444 degrees. Pymunk final-angle errors decrease from 0.19835049 to 0.09010603 to 0.04297798 degrees at 1 / 0.5 / 0.25 ms. MATLAB `ode45` agrees with SciPy `DOP853` to a maximum 8.40e-8 degree and 1.18e-6 N knee-load difference for the 1.2 s default step. A 1.5 s square input with wheel locking and clipped knee impedance agrees to 6.86e-8 degree and 9.59e-7 N knee-load difference. Both runtimes terminate an aggressive 250 mm / 40 ms step at the 15-degree lower bound near 0.1337167 s. This tests ideal numerical agreement, not physical hardware performance.
