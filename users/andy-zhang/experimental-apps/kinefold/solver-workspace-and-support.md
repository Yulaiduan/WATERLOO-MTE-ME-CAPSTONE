# Solver workspace and V4.5 support check

Andy Zhang with Codex,2026-10-31; experimental member app.
Support audit source87175bd; viewer-first follow-up based on e109b67.
Priority: accurate design numbers and transparent assumptions, rather than a
general reusable framework. No force law or numerical tolerance changed here.

## Viewer-first follow-up

The owner superseded the following layout with a simpler viewer-first page in
tabs01–03. A190px action/mode rail sits beside the main visual at the top; every
detailed form and the categorized result sections span the full page below.
On phones the rail wraps above the visual.01 leads with the existing torque
Plotly chart and Jump/Landing/Principles actions,followed by signed readouts,
full-width inputs,all remaining charts,equations and sample/export data.
02/03 show an exact saved-pose geometry preview before running,clearly labelled
as geometry only; actual captured motion replaces it after a run. The existing
drawing APIs retain finite belt/spring geometry,+x left,+z up and100mm grid.

The dynamic rail runs one/both engines,replays from the first sample or navigates
to Parameters,Results,Compare and Principles below. These navigation buttons
carry down arrows; Principles opens existing assumptions rather than changing
the physics. Repeated runs replace the previous player and retain one set of
IDs/listeners. Exports/desktop actions remain with detailed results. The optional
options.playerHost property in internal Results.mount preserves the old default path
for other read-only views. Energy normalizes display-only negative zero; raw
signed calculations and exports remain unchanged.

Two authorized GPT-6.1 Sol workers implemented isolated patches. Headless Edge
at1440/390px verifies main visual precedes every form,full-width parameters,
four unique Energy charts,Jump/Landing/Principles actions,both playback clocks,
repeat-run unique player IDs,comparison navigation and visible invalid-contact
guards. The UI uses the same isolated in-memory fixtures described below and
exact existing half-step captures; these screenshots add no new trajectories. Live library
hash is preserved during the check. Relevant Energy/Plotly/replay checks pass;
five PNGs and the bounded QA log remain app-local/native Notion. No model,
saved-design default,solver API or physical calibration changed in this follow-up.

## Earlier layout at e109b67 (superseded)

Tabs01–03 put inputs/shared settings on the left and outputs on the right.
01 retains immediate energy readouts, all Plotly charts, equations and signed
data; it is not a time integration and retains its moving-link guard. Its full
landing opening input now allows1, matching the existing validator.02/03 put
animation, playback, exports, categorized results and comparison on the right.
Captured snapshot identity stays visible. Contact notes collapse while invalid
setup guards stay outside the disclosure. Desktop columns are330/350px plus
flexible results; below980px they stack and the inputs can be collapsed.

06 is optional. Detailed setup, filters, numerical assumptions and job-token
controls are collapsed. Saved results and active job status/cancel remain
accessible. Bounded comparisons can also be requested in chat. Existing APIs,
defaults, exact snapshots and the separate quick calculator remain unchanged.
Three authorized GPT-6.1 Sol workers implemented isolated layout patches; parent
integrated, inspected screenshots and checked data/storage behavior.

## Actual support deficit

The owner confirmed V4.5 terrain stability. Captured working settings:8.75kg
chassis,1kg upper link,1kg lower link,.5kg wheel per corner,alpha0,theta135;
springLaw `v4`,K8N/mm,p0=330.869282809N,constant motor torque0,no active controller.
V4.5 deliberately retained the old spring calibration when adding link masses.
This current reference is35kg chassis/45kg gross, distinct from the earlier
45kg-chassis/55kg-gross gearing example.

At135deg, actual cable tension is591.865710N but equivalent upward chassis
support is only85.788885N. For this equal-link grounded-wheel geometry,
`m_eff=m1+0.75*m2+0.25*m3=9.75kg`, requiring95.647500N. The same value follows
from the full finite-body gravity derivative. The floor supports the wheel;
its full mass is not added to this chassis-heave derivative.

Missing support is9.858615N. Grounded dUg/dtheta is−40.579798Nm versus spring
torque−36.397142Nm: another−4.182656Nm would be required at that pose. Negative
is extension in the saved convention. Damping supplies no static force at rest.
Both engines receive the same insufficient support, so both sink.

## Six actual flat-floor checks

Preserve masses/geometry,zero motor,damping1Nms/rad. Isolate a stationary flat
floor by removing the periodic terrain and setting height/speed/delay0. Duration
1.5s,output100Hz,iterations120,dt.0005s. Compare original support against an
explicit initial-pose balance multiplier95.6475/85.788885350=1.114917155174,
applied equally to K/p0:8.919337241392N/mm and368.891839524N. Geometry is unchanged.
This is approximate V4 support over the stroke, not exact constant vertical force.

| Setup | Analytical max drift | Pymunk max drift |
| --- | ---: | ---: |
| Original,0.5ms |268.972642mm|268.646105mm|
| Calibrated at135deg,0.5ms |0.123206mm|0.002451mm|
| Calibrated,0.25ms |0.030748mm|0.000976mm|

Original compression-stop events occur at.762805/.763000s. Post-stop trajectories
differ under native versus analytical rigid stop treatment; those oscillations
are not calibrated hardware behavior. All six runs keep chassis/wheel free and
zero motor. An early progress statement incorrectly said both calibrated drifts
were under.003mm; it was corrected before refinement.

Analytical calibrated energy residual decreases3.04e-5→3.78e-6J. Native combined
constraint/force-splitting residual remains3.433→1.717J: positional agreement does
not certify that ledger, and the residual is not physical absorption. No terrain
tracking,tire/stop impact,full-vehicle,thermal or hardware validation is claimed.

The separate [flat support example](saved-configurations/vsl-v45-flat-support-balanced-alpha0.json)
uses the refined settings and its own identity. It does not replace the original
reference or live working profile. Static balance does not regulate ride height
over the owner's100mm-RMS/20%-grade talus terrain. Other poses,masses,alpha or
geometry require a new balance calculation.

## UI checks and evidence

Headless Edge checks1440px desktop/390px phone,output placement,no page overflow
after asynchronous Plotly resize,both playback clocks,optional06 setup and visible
invalid-contact errors. Profile mutations are intercepted in memory; dynamic UI
payloads match the actual saved half-step captures exactly. Screenshots are UI
checks using saved data,not new physics. Energy uses the valid massless-link
screenshot2b profile; dynamic screenshots use the finite-link flat calibration.
Outside user activity changed the live profile during the task; each headless
check preserved its own initial hash. No old library copy was restored.

Affected Energy,Plotly,motor,pinned,project,automatic-comparison and replay checks
pass. Captures,source-hashed settings,PNGs and small audit helpers remain ignored
app-local/native Notion attachments. No Computer skill/live-tab automation used.
Use [Start Kinefold.cmd](Start%20Kinefold.cmd) and [Stop Kinefold.cmd](Stop%20Kinefold.cmd)
at127.0.0.1:4191; no boot/login automation. Canonical physics is not applicable.
