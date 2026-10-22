# Kinefold app instructions

Follow the repository root protocol. Read README.md and context/README.md before
editing. Keep this isolated experimental member app separate from canonical
robot assets, shared simulation and the three source apps.

Preserve the front-left right-handed x-forward/y-left/z-up frame. Source VSL's
y/z plane maps to Kinefold x/z with x = -source_y, z = source_z; source +x maps
to new +y. Preserve physical force and axial torque signs. Explain every input
in the conventions dictionary. Keep the V4 coil and ideal constant-force laws
distinct. Do not introduce a contact/dynamics claim into the geometry builder.

Record actual numerical/browser/start-restart checks. Use the project-local
Start/Stop Kinefold.cmd launchers at 127.0.0.1:4191. No boot/login automation.
Changes remain workspace scope until explicitly promoted into shared engineering.
