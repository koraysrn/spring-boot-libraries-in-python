"""
Non-happy-path tests for the JaCoCo equivalent (coverage.py).
"""

import ast
import io
import pathlib

import coverage
import pytest

import calculator

CALCULATOR_FILE = pathlib.Path(__file__).resolve().parent.parent / "calculator.py"
SOURCE = CALCULATOR_FILE.read_text()


def analyze(run):
    cov = coverage.Coverage(source=["calculator"], branch=True)
    cov.start()
    run(calculator)
    cov.stop()
    cov.save()

    data = cov.get_data()
    filename = list(data.measured_files())[0]
    _, _, _, missing, _ = cov.analysis2(filename)
    return cov, set(missing)


def line_of(substring):
    for index, line in enumerate(SOURCE.splitlines(), start=1):
        if substring in line:
            return index
    raise AssertionError(f"substring not found: {substring}")


def function_body_lines(func_name):
    tree = ast.parse(SOURCE)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            if not node.body:
                return set()
            return set(range(node.body[0].lineno, node.end_lineno + 1))
    return set()


def check_threshold(percentage, threshold):
    if percentage < threshold:
        raise RuntimeError(
            f"Coverage {percentage:.2f}% is below threshold {threshold}%"
        )


def test_uncovered_else_branch_is_detected():
    _, missing = analyze(lambda c: (c.classify(5), c.classify(-5)))
    assert line_of('return "zero"') in missing


def test_uncovered_except_branch_is_detected():
    _, missing = analyze(lambda c: c.safe_divide(10, 2))
    assert line_of("return None") in missing


def test_all_branches_covered_has_no_missing_branch_lines():
    _, missing = analyze(
        lambda c: (
            c.classify(5),
            c.classify(-5),
            c.classify(0),
            c.safe_divide(10, 2),
            c.safe_divide(1, 0),
        )
    )
    assert line_of('return "zero"') not in missing
    assert line_of("return None") not in missing


def test_dead_code_line_is_reported():
    _, missing = analyze(
        lambda c: (
            c.classify(5),
            c.classify(-5),
            c.classify(0),
            c.safe_divide(10, 2),
            c.safe_divide(1, 0),
            c.is_even(2),
            c.is_even(3),
        )
    )
    assert line_of('return "dead"') in missing


def test_fully_called_function_has_no_missing_body_lines():
    _, missing = analyze(lambda c: c.wrong_average(2, 4))
    body = function_body_lines("wrong_average")
    assert body & missing == set()


def test_coverage_does_not_guarantee_correctness():
    _, missing = analyze(lambda c: c.wrong_average(2, 4))
    body = function_body_lines("wrong_average")
    # Every body line is covered, yet the logic is wrong.
    assert body & missing == set()
    assert calculator.wrong_average(2, 4) == 6


def test_threshold_fails_when_coverage_below_limit():
    cov, _ = analyze(lambda c: c.classify(5))
    percentage = cov.report(file=io.StringIO())
    assert percentage < 100
    with pytest.raises(RuntimeError):
        check_threshold(percentage, 80)
