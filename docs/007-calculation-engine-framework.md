# Calculation Engine Framework

The Calculation Engine performs deterministic construction calculations in the backend.

## Rules

- Backend owns all calculation logic.
- Frontend must never calculate construction quantities or prices.
- V1 has no AI.
- Calculations must not call LLM providers.
- Inputs and outputs must be snapshotted.
- Calculator versions must be recorded.
- All quantities use metric units.

## Engine Inputs

Calculation inputs may include:

- Company
- Project
- Room
- Measurement records
- Material configuration
- Waste percentage
- Labor configuration
- Calculator type
- Calculator version

## Engine Outputs

Calculation outputs may include:

- Surface areas
- Material quantities
- Waste-adjusted quantities
- Labor quantities
- Material list rows
- Calculation warnings
- Result snapshot

## Engine Framework

The backend exposes a calculation engine framework for deterministic calculators.

Sprint 6 registered placeholder engines only. Sprint 9 implements the Painting Engine. Remaining placeholder engines are deterministic and return a stored `engine_not_implemented` result instead of running construction formulas.

Registered engine types:

- `painting` - implemented in Sprint 9
- `tiles` - placeholder
- `knauf` - placeholder
- `flooring` - placeholder
- `concrete` - placeholder
- `facade` - placeholder

Concrete formulas for the remaining placeholder engines must be implemented in later calculator sprints.

## Calculation Run Statuses

Supported calculation run statuses:

- `draft`
- `completed`
- `failed`
- `archived`

## Calculation Run Record

Every run should store:

- `company_id`
- `project_id`
- `project_task_id`
- `room_id`
- `measurement_set_id`
- `engine_type`
- `engine_version`
- `status`
- `created_by_user_id`
- `created_at`

Inputs, outputs, and line items are stored as separate auditable records linked to the calculation run:

- `calculation_inputs`
- `calculation_outputs`
- `calculation_line_items`

New inputs must create a new calculation run. Existing calculation run inputs and outputs must not be overwritten. The archive endpoint changes only the run status to `archived`.

## Painting Calculator

Implementation status: implemented in Sprint 9.

Supported inputs:

- `project_id`
- Optional `project_task_id`
- Optional `room_id`
- Optional `measurement_set_id`
- `include_ceiling`
- `include_walls`
- `coats`
- `primer_coats`
- Optional `paint_material_id`
- Optional `primer_material_id`
- Optional `waste_percentage`
- Optional `labor_rate_per_m2`
- Optional `notes`

Area source priority:

1. Backend-computed room values when `room_id` is provided.
2. Measurement items named `wall_area`, `ceiling_area`, or `paintable_area` in `m2` when `measurement_set_id` is provided and no room is provided.

Formula summary:

- `selected_area_m2` is wall area, ceiling area, or both depending on inclusion flags.
- Paint liters use selected area, coats, waste percentage, and material coverage in `m2/liter`.
- Primer liters use selected area, primer coats, waste percentage, and primer material coverage in `m2/liter`.
- Labor cost uses `selected_area_m2 * labor_rate_per_m2`.
- Material costs use Procurement Engine resolved prices when material IDs are supplied.

Stored outputs:

- `selected_area_m2`
- `wall_area_net_m2`
- `ceiling_area_m2`
- `coats`
- `primer_coats`
- `waste_percentage`
- `paint_required_liters`
- `primer_required_liters`
- `paint_material_cost`
- `primer_material_cost`
- `labor_cost`
- `total_cost`
- `assumptions`
- `warnings`

Calculation line items are stored for paint material, primer material, and labor when those inputs are provided.

## Tile Calculator

Common inputs:

- Surface area
- Tile dimensions
- Waste percentage
- Adhesive coverage
- Grout coverage

Common outputs:

- Tile area
- Waste-adjusted tile area
- Tile count
- Adhesive quantity
- Grout quantity
- Labor quantity
- Material list rows

## Knauf Calculator

Common inputs:

- System type
- Wall or ceiling dimensions
- Board dimensions
- Profile spacing
- Screw rules
- Insulation inclusion
- Waste percentage

Common outputs:

- Gypsum board quantity
- Profile quantity
- Screw quantity
- Jointing material
- Insulation quantity
- Labor quantity
- Material list rows

## Flooring Calculator

Common inputs:

- Room length
- Room width
- Perimeter
- Excluded opening width
- Waste percentage
- Underlay inclusion
- Skirting inclusion

Common outputs:

- Floor area
- Waste-adjusted flooring area
- Underlay quantity
- Skirting length
- Labor quantity
- Material list rows

## Pricing Boundary

The Calculation Engine may output material quantities.

The backend must resolve prices through the Procurement Engine and Estimate Engine. The frontend must not multiply quantities by prices to produce business totals.

## Auditability

Calculation result screens and PDFs should be traceable back to stored calculation run snapshots.
