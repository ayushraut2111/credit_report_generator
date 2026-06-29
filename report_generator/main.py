from pathlib import Path
from pydantic import ValidationError
from settings import BASE_DIR
from utils import load_input_json


SAMPLE_INPUT_BASE_PATH = BASE_DIR / "sample_input.json"


def render_report(input_json_path: Path = SAMPLE_INPUT_BASE_PATH):
    try:
        validated_input = load_input_json(input_json_path)
    except FileNotFoundError as exc:
        print(exc)
        return None
    except ValidationError as exc:
        print("JSON validation failed:")
        print(exc)
        return None

    return validated_input


if __name__ == "__main__":
    result = render_report()
    if result is not None:
        print("JSON validated successfully")
