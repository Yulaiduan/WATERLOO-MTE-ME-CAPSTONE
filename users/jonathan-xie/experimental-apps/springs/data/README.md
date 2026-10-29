# Catalogue data

The three gzip files contain JSON arrays, one record per part. MC/ME use
`k_N_per_mm`, `travel_mm`, `f_max_N`, `l_min_mm`, `l_max_mm` and
`initial_tension_N`. MT uses `torque_max_N_mm`, `deflection_deg`,
`k_torsion_N_mm_per_rad`, `wind_direction`, `shaft_dia_mm`, `leg_length_mm`,
`coils` and `body_at_max_torque_mm`. Other dimensions have explicit `_mm` keys.

Imperial numeric fields use `_in`, `_lbf`, `_lbf_per_in`, `_in_lbf` and
`_in_lbf_per_deg`. USD prices are per supplier package/order unit and per piece
for individually specified springs. Assortments retain their order-unit price.

`attributes` preserves all individual specification fields. `metric_attributes`
contains additional converted properties as `{unit, values}`. A two-element
values array represents the source minimum and maximum. `listing` preserves the
original table fields, including their original unit text. No null is zero.

Derived coil dimensions are nominal geometry, not loaded clearances.
`selection_status`, `force_rating_difference_pct` and `notes` identify records
that need review or a different spring/installation model. `detail_fetched`
records individual specification-page coverage.

Retain `id-registry.json` during refreshes. Coverage is reconciled to the three
linked categories; the standard compression-family URL does not include other
compression subcategories. See the app README for the VSL v5 mapping.
