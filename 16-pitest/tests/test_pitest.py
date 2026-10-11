"""
Non-happy-path tests for the PIT equivalent (mutation testing).
"""

import pathlib

import mutator
import runner
import suite

TARGET_FILE = pathlib.Path(__file__).resolve().parent.parent / "target.py"
SOURCE = TARGET_FILE.read_text()


def test_all_expected_mutations_are_generated():
    mutants = mutator.generate_mutants(SOURCE)
    descriptions = [description for description, _ in mutants]

    assert len(mutants) == 8
    assert "flip > to <" in descriptions
    assert "change >= to >" in descriptions
    assert "change and to or" in descriptions
    assert "change 0 to 1" in descriptions
    assert "delete return" in descriptions
    assert "remove if condition" in descriptions
    assert "change 'active' to empty string" in descriptions
    assert "delete raise" in descriptions


def test_strong_suite_kills_every_mutant():
    mutants = mutator.generate_mutants(SOURCE)
    for description, mutated_source in mutants:
        result = runner.classify_mutant(mutated_source, suite.STRONG_SUITE)
        assert result == "killed", f"mutant survived: {description}"


def test_weak_suite_lets_boundary_mutant_survive():
    def weak_test(mod):
        assert mod.is_adult(30) is True

    mutants = mutator.generate_mutants(SOURCE)
    boundary_mutant = next(
        source for description, source in mutants if description == "change >= to >"
    )

    killed, survivors = runner.run_suite(boundary_mutant, [weak_test])
    assert killed == []
    assert survivors == ["weak_test"]
