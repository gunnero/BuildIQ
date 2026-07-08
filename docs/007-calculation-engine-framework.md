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

## Calculator Types

V1 calculator types:

- `painting`
- `tile`
- `knauf`
- `flooring`

## Calculation Run Record

Every run should store:

- `company_id`
- `project_id`
- `room_id`
- `calculator_type`
- `calculator_version`
- `input_snapshot`
- `result_snapshot`
- `created_by_employee_id`
- `created_at`

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
