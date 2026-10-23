# Local design profiles

Kinefold stores named project-v3 designs and the exact working copy together in
`library.json`, with an optimistic revision to reject conflicting browser tabs.
Writes replace the complete file atomically after validation. Browser profiles
are migrated on first use; `browser-backup.json` preserves the original raw keys
once, and those browser keys remain unchanged. Later browser recovery copies
older designs into new named profiles without replacing the active working copy.

These generated JSON files are ignored by Git. Keep a copy of this folder and
`exports/` when moving the app to another computer. Do not edit files while the
app is open; reload after external edits. A malformed file fails visibly and is
retained for recovery. This is local storage, not cloud synchronization.
