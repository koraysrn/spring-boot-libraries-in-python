"""Runs a test suite against the original or mutated source."""


import types


def apply_source(source):
    namespace = {}
    exec(compile(source, "<mutant>", "exec"), namespace)
    return types.SimpleNamespace(**namespace)


def run_suite(source, suite):
    namespace = apply_source(source)
    killed = []
    survivors = []
    for test in suite:
        try:
            test(namespace)
            survivors.append(test.__name__)
        except Exception:
            killed.append(test.__name__)
    return killed, survivors


def classify_mutant(source, suite):
    killed, _ = run_suite(source, suite)
    return "killed" if killed else "survived"
