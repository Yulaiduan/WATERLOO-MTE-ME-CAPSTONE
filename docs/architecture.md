# Preliminary system architecture

Status: **concept from the Fall 2026 project registration form**, subject to requirements and design review.

## System intent

CAMEL is an all-terrain wheeled quadruped intended to preserve efficient wheeled motion while adapting its chassis to uneven ground. The specific application is still open. The registration form mentions several possible applications as examples, not as commitments.

## Proposed subsystem boundaries

| Area | Concept described in the form | To define before implementation |
| --- | --- | --- |
| Chassis and structure | Motor-carrying chassis with four wheeled legs | Envelope, mass and payload budget, structural interfaces |
| Leg suspension and actuation | Four independently actuated, spring-assisted legs; mechanically coupled upper/lower leg sections with one degree of freedom per leg | Linkage geometry, travel, springs, loads, actuator sizing and stops |
| Wheel drive and transmission | Four-wheel drive; two motors drive the left and right wheel pairs for steering | Power path, gearing/belts, wheel size, traction and braking |
| Electronics and power | Electronics work is assigned, but the form specifies no components | Power source, distribution, sensors, motor drivers, wiring and protection |
| Controls and modelling | Active chassis levelling; kinematic, thermal and other simulation work | Control objectives, sensing, state estimation, model assumptions and interfaces |
| Verification | Calculations, simulations, scaled proof of concept, full-scale prototype and tests | Traceable requirements, pass/fail criteria, test procedures and data storage |

The concept sketch on page 3 shows a side-view suspension linkage and wheel drive, plus a suspension range-of-motion illustration. Treat its dimensions and mechanism details as exploratory until the team records a reviewed design.

## Decisions still needed

1. Select the use case and operating terrain with the partner, then set measurable requirements.
2. Define subsystem ownership and mechanical, electrical, and control interfaces.
3. Record selected components, calculations, CAD/simulation models, and safety constraints.
4. Trace each requirement to a calculation, simulation, or prototype test and keep results with revisions.

No claim about market uniqueness or achieved performance has been independently validated in this documentation.
