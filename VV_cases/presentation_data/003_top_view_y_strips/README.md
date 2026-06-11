# 003_top_view_y_strips

Top-view 1 mm strip analysis of integrated wall heat transfer.

The method is the same as in `002_Nu_and_vorticity`, but each surface polygon is
assigned to a strip by its centroid `y` coordinate instead of `x`. This asks a
different question: how heat transfer is distributed across the channel/tube width
in the top-view direction.

## Figures

`fig01_y_strip_Q_profiles_by_Re.png`

- absolute `Q_total`, `Q_tube`, and `Q_fins` per 1 mm y-strip.

`fig02_y_local_excess_over_global_gain.png`

- local y-strip gain divided by global gain, minus 1. Values above 0 mean that the
  strip grows faster than the whole exchanger after removing global Re scaling.

`fig03_y_Q_excess_over_steady_model.png`

- difference from a local linear steady trend fitted between Re=100 and Re=150.

`fig04_y_local_share_delta_vs_Re150.png`

- redistribution of each y-strip's share of total heat transfer relative to Re=150.

`fig05_y_local_dQdRe_by_interval.png`

- local heat-transfer sensitivity over Re intervals 100-150, 150-160, and 160-200.

Dashed vertical lines mark approximate tube radius bounds at y = +/-6 mm; the dotted
line marks the tube centerline.
