# Firmware

**Status: scaffold; board and toolchain not selected.** Embedded control, sensors, actuator drivers, board initialization, command validation, watchdogs and hardware tests belong here.

Add `src/`, `include/`, `boards/` and `tests/` as appropriate to the selected toolchain. Keep dependency/build definitions and verified build, flash and test instructions here. Generated output goes in ignored `build/`.

Implement language-neutral [shared contracts](../shared/README.md), including command/telemetry formats, units, timing and limits. Firmware builds independently of Python simulation/training and cloud tooling. The policy inference runtime is a separate design choice; firmware remains responsible for safe handling of stale, invalid or absent commands.

[Repository architecture](../README.md#repository-architecture)
