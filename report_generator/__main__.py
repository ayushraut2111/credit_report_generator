import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent))

from report_generator.utils import render_report, SAMPLE_INPUT_BASE_PATH, OUTPUT_PDF_PATH


def cli():
    default_input  = SAMPLE_INPUT_BASE_PATH
    default_output = OUTPUT_PDF_PATH
    print(default_input,default_output)

    parser = argparse.ArgumentParser(
        description="Generate a credit report PDF from a JSON input file.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help="Path to the input JSON file (default: sample_input.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help="Path for the output PDF (default: sample_output.pdf)",
    )
    args = parser.parse_args()

    result = render_report(args.input, args.output)
    if result is not None:
        print(f"Report saved to: {result}")


if __name__ == "__main__":
    cli()


# python -m report_generator --input /Users/ayushchaurasia/Desktop/credit_manager/credit_report_generator/sample_input.json --output /Users/ayushchaurasia/Desktop/credit_manager/credit_report_generator/sample_output.pdf
