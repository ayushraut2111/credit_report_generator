from pathlib import Path
from pydantic import ValidationError
from settings import BASE_DIR
from utils import load_input_json
from pdf_generator import generate_pdf


SAMPLE_INPUT_BASE_PATH = BASE_DIR / "sample_input.json"
OUTPUT_PDF_PATH = BASE_DIR / "sample_output.pdf"


def render_report(input_json_path= SAMPLE_INPUT_BASE_PATH,output_pdf_path= OUTPUT_PDF_PATH):
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


if __name__ == "__main__":
    result = render_report()
    if result is not None:
        print(f"Report saved to: {result}")
