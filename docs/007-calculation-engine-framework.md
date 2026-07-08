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

The backend exposes a calculation engine framework before concrete formulas are implemented.

Sprint 6 registers placeholder engines only. Placeholder engines are deterministic and return a stored `engine_not_implemented` result instead of running construction formulas.

Registered engine types:

- `painting`
- `tiles`
- `knauf`
- `flooring`
- `concrete`
- `facade`

Concrete formulas for these engines must be implemented in later calculator sprints.

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

Common inputs:

- Room length
- Room width
- Room height
- Opening area
- Ceiling inclusion
- Paint coverage
- Primer coverage
- Waste percentage

Common outputs:

- Wall gross area
- Wall net area
- Ceiling area
- Paint area
- Paint liters
- Primer liters
- Labor quantity
- Material list rows

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
