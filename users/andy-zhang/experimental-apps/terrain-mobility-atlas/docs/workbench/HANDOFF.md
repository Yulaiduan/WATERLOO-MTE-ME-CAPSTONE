# Terrain Workbench handoff

## Durable manual restart

Double-click [Start Capstone.cmd](../../Start%20Capstone.cmd) in this app folder after a reboot or server shutdown. It starts the saved production atlas and workbench together at their existing URLs: `http://127.0.0.1:4175/` and `http://127.0.0.1:4175/workbench/`. Wait for the Ready message; the browser opens only after both pages respond. Repeated launches reuse the verified app. [Stop Capstone.cmd](../../Stop%20Capstone.cmd) stops only its tracked server after checking PID, creation time and command line. Launch failures remain readable; server logs/state live in `.preview/`. Helpers use the durable Node.js installation in `C:\Program Files\nodejs`, local Vite dependencies and `dist` build. If prerequisites are missing, the error explains `npm ci` / `npm run build`; launch does not reinstall dependencies. No boot or login task is added.

Lifecycle verified October 4, 2026 using the actual batch launcher with `-NoBrowser` from unrelated working directory `C:\Windows`. Both routes and their JS/CSS assets returned HTTP 200. Repeated start reused PID 48376; scoped stop freed port 4175; restart created PID 31428 and restored both original routes. The server persisted after the calling tool/terminal exited. Installed runtime is Node.js 22.20.0; no Codex runtime is required.

Development: `npm ci`, then `npm run dev`; open `http://127.0.0.1:5173/workbench/`. Vite uses a strict 5173 port, so reuse the running project server or stop another copy before starting one.

Checks: `npm test`, then `npm run build`. Production preview: `npm run preview -- --port 4175 --strictPort`; open `http://127.0.0.1:4175/workbench/`. Vite builds both the atlas `/` and workbench `/workbench/`. `dist` is local output, with no hosting configured.

The atlas has also been simplified following the user's later instruction; its historical documentation is retained with a superseding current-iteration note. Workbench-specific records live in this subdirectory. Terrain source records and the earlier simulation/data plans remain the evidence reference.

The combined test suite passes 25/25, the multi-entry production build succeeds, and audit reports zero vulnerabilities. Targeted production-browser review at [http://127.0.0.1:4175/workbench/](http://127.0.0.1:4175/workbench/) verifies terrain modes, observed/imported data, default calculation, cancellation snapshot retention, graph selection and readable compact plots. Actual views: [terrain workspace](../../evidence/workbench-ui/workbench-terrain.jpg) and [node graph](../../evidence/workbench-ui/workbench-graph.jpg).

Export payloads and serialized content are verified; native blob download-to-disk completion remains unverified after an in-app browser event timeout. Consult [validation](VALIDATION.md) for exact observations and [architecture](ARCHITECTURE.md) before interpreting numerical loads as hardware sizing. A completed run is not motor approval: the default candidate exceeds the chosen continuous torque assumption and retains unresolved thermal/electrical/structural requirements.
