import json
from pathlib import Path

from schemas import SampleInputModel


def load_input_json(input_json_path: Path) -> SampleInputModel:
    input_path = Path(input_json_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    return SampleInputModel.model_validate(raw_data)
