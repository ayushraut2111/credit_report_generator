import json
from pathlib import Path
from pydantic import ValidationError
from report_generator.schemas import SampleInputModel
from report_generator.settings import BASE_DIR
from report_generator.pdf_generator import generate_pdf

SAMPLE_INPUT_BASE_PATH = BASE_DIR / "sample_input.json"
OUTPUT_PDF_PATH = BASE_DIR / "sample_output.pdf"


def load_input_json(input_json_path: Path) -> SampleInputModel:
    input_path = Path(input_json_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    return SampleInputModel.model_validate(raw_data)


def render_report(
    input_json_path=SAMPLE_INPUT_BASE_PATH,
    output_pdf_path=OUTPUT_PDF_PATH,
):
    try:
        validated_input = load_input_json(input_json_path)
    except FileNotFoundError as exc:
        print(exc)
        return None
    except ValidationError as exc:
        print("JSON validation failed:")
        print(exc)
        return None

    generate_pdf(validated_input, output_pdf_path)
    return output_pdf_path
