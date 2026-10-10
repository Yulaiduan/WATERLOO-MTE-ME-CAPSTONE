# Split ZIP payload

Concatenate the ordered `.part` files from the adjacent archive-manifest.json
to reconstruct one ZIP. Prefer `../restore_archive.py`, which verifies chunk,
ZIP and per-file SHA-256 and refuses to overwrite any destination.

Parts are binary archive data, not scripts. The split respects the repository's
1 MiB file ceiling. Original file paths/bytes, including large PDFs, GIFs and
CSV outputs, are preserved inside the package; no canonical robot claims follow.
