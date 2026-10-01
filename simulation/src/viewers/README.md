# Viewers

Optional visualization, UI and debugging belong here. No viewer is implemented
in this branch. Rendering must not change the physics timestep, seeding or control
behavior. Import viewer libraries only on the interactive path; headless checks
must work without a display, GUI libraries or macOS `mjpython`.
