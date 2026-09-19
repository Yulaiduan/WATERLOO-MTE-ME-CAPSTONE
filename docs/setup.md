# Setup and reproducibility

Status: **GitHub workspace connected; engineering toolchains not yet selected**. The registration form contains no CAD, simulation, firmware, electronics, or fabrication setup instructions. Do not assume a particular toolchain or publish placeholder commands as if they work.

## Repository access and first checkout

The repository is [Yulaiduan/WATERLOO-MTE-ME-CAPSTONE](https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE) and is **private**. Ask the owner for access before trying to clone it. Install Git and authenticate to GitHub using your normal credential manager or GitHub CLI. Do not place access tokens in commands, files, or repository URLs.

From a directory where you want a **new** checkout, run:

```sh
git clone https://github.com/Yulaiduan/WATERLOO-MTE-ME-CAPSTONE.git
cd WATERLOO-MTE-ME-CAPSTONE
git status --short --branch
git remote -v
```

The status should show a clean `main` branch, and the `origin` remote should point to that repository. These commands are for a new checkout; do not clone over an existing Capstone folder. The original local workspace was connected separately without discarding its documentation.

The root `README.md` is the overview, `docs/README.md` is the documentation map, and `AGENTS.md` records project context for assistants. The registration PDF is not stored in the repository; partner data should only be added after the team agrees on access and sharing rules. No build or test command exists yet because the engineering tools have not been chosen.

## When engineering tooling is selected

Document the following for each mechanical, electrical, controls, and simulation workflow:

- Required software and exact versions, licenses, hardware, and access permissions.
- Where source files and approved shared assets live; how a new member obtains them without exposing partner material or secrets.
- Installation and configuration steps, including a safe example configuration when needed.
- One verified minimal open/build/run procedure and its expected result.
- How to reproduce calculations, simulations, and prototype tests, including inputs, units, model revisions, and output locations.
- Troubleshooting notes, safety prerequisites, and an owner/date for the last successful check.

Add executable commands only after someone on the team has run them from a clean environment. Keep subsystem-specific procedures in separate linked pages once those workflows exist; this page should remain the entry point.
