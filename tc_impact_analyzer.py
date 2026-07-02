"""Entry point: run the built-in cases, reports go to a file, audit logs stream to the terminal.
Needs a .env with ANTHROPIC_API_KEY. Run: python tc_impact_analyzer.py"""

import logging
import sys

from tc_analyzer import TEST_CASES, AgentError, print_report, run_pipeline

DEFAULT_OUTPUT_FILE = "output.txt"


def run_cases() -> None:
    for case in TEST_CASES:
        print("\n" + "#" * 78, file=sys.stderr)
        print(f"# {case['title']}", file=sys.stderr)
        print("#" * 78, file=sys.stderr)

        try:
            result = run_pipeline(
                clause=case["clause"],
                change=case["change"],
                source_country=case["source_country"],
                target_country=case["target_country"],
            )
            print_report(result)
        except AgentError as exc:
            # failed case: record it in the audit trail (terminal), not in the lawyer-facing report file
            logging.error(f"analysis could not be completed: {exc}")
        print()


def main() -> None:
    output_file = DEFAULT_OUTPUT_FILE
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)

    with open(output_file, "w", encoding="utf-8") as out:
        real_stdout = sys.stdout

        sys.stdout = out
        try:
            run_cases()
        finally:
            sys.stdout = real_stdout

    print(f"\nReport written to {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
