# Calculation Rules

BuildIQ V1 calculations must be deterministic and auditable. V1 must not use AI to calculate construction quantities.

## General Rules

- Store inputs and outputs for every calculation run.
- Use metric units.
- Store areas in square meters.
- Store lengths in meters.
- Store currency amounts in MKD.
- Apply configurable waste percentages where relevant.
- Round display values for users, but keep stored numeric values precise enough for recalculation.
- Generated material list rows must identify the calculation source.

## Room Measurements

Common inputs:

- `length_m`
- `width_m`
- `height_m`
- `area_m2`
- `perimeter_m`
- `opening_area_m2`
- `quantity`

Derived values:

- Floor area: `length_m * width_m`
- Ceiling area: `length_m * width_m`
- Wall gross area: `2 * (length_m + width_m) * height_m`
- Wall net area: `wall_gross_area_m2 - opening_area_m2`

## Painting Calculator

Suggested outputs:

- Wall paint area
- Ceiling paint area
- Primer quantity
- Paint quantity
- Labor quantity
- Material list rows

Base formulas:

- `paint_area_m2 = wall_net_area_m2 + ceiling_area_m2`
- `paint_liters = paint_area_m2 / coverage_m2_per_liter`
- `primer_liters = primer_area_m2 / primer_coverage_m2_per_liter`

## Tile Calculator

Suggested outputs:

- Tile area
- Tile quantity
- Adhesive quantity
- Grout quantity
- Waste quantity
- Labor quantity
- Material list rows

Base formulas:

- `tile_area_m2 = selected_surface_area_m2`
- `tile_area_with_waste_m2 = tile_area_m2 * (1 + waste_percent / 100)`
- `tile_count = tile_area_with_waste_m2 / single_tile_area_m2`

## Knauf Calculator

Suggested outputs:

- Gypsum board quantity
- Profile quantity
- Screw quantity
- Jointing material
- Insulation quantity
- Labor quantity
- Material list rows

Base formulas depend on wall or ceiling system type and must store the selected system in the calculation input snapshot.

## Flooring Calculator

Suggested outputs:

- Floor material quantity
- Underlay quantity
- Skirting length
- Waste quantity
- Labor quantity
- Material list rows

Base formulas:

- `floor_area_m2 = length_m * width_m`
- `flooring_area_with_waste_m2 = floor_area_m2 * (1 + waste_percent / 100)`
- `skirting_length_m = perimeter_m - excluded_opening_width_m`

## Estimate Inputs

Estimate generation may use:

- Approved material list rows
- Labor quantities
- Unit prices
- Discounts
- Taxes
- Notes
- Payment terms

## Auditability

Each calculation run must preserve:

- User inputs
- Formula version or calculator type
- Result snapshot
- User who created the run
- Creation date
