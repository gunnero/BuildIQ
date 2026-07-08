import argparse
import json
from pathlib import Path

from app.main import create_app


DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parents[3] / "docs" / "api" / "openapi.json"


def export_openapi_json(output_path: Path = DEFAULT_OUTPUT_PATH) -> None:
    app = create_app()
    schema = app.openapi()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export BuildIQ OpenAPI JSON.")
    parser.add_argument(
        "output",
        nargs="?",
        default=str(DEFAULT_OUTPUT_PATH),
        help="OpenAPI JSON output path.",
    )
    args = parser.parse_args()
    export_openapi_json(Path(args.output))


if __name__ == "__main__":
    main()
