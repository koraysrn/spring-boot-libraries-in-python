"""Architecture rule checker, the equivalent of ArchUnit's layered tests.

ArchUnit verifies that code follows architecture rules such as
"controller -> service -> repository". This module provides the same check
for Python modules by parsing their imports.

The standard Python tool for this is import-linter. This checker reimplements
the same layering concept by hand for learning purposes.
"""

import ast

DEFAULT_LAYERS = {
    "controllers": {"services"},
    "services": {"repositories"},
    "repositories": set(),
    "utils": set(),
}

# Layers that every other layer may import.
ALWAYS_ALLOWED = {"utils"}


class ArchitectureRules:
    def __init__(self, layers=None, always_allowed=None):
        self.layers = layers if layers is not None else DEFAULT_LAYERS
        self.always_allowed = (
            always_allowed if always_allowed is not None else ALWAYS_ALLOWED
        )

    def layer_of(self, module_name: str) -> str | None:
        for part in module_name.split("."):
            if part in self.layers:
                return part
        return None

    def check_imports(self, module_name: str, imported_modules) -> list[str]:
        importer_layer = self.layer_of(module_name)
        if importer_layer is None:
            return []

        allowed = self.layers[importer_layer] | self.always_allowed
        violations = []
        for imported in imported_modules:
            imported_layer = self.layer_of(imported)
            if imported_layer is None or imported_layer == importer_layer:
                continue
            if imported_layer not in allowed:
                violations.append(
                    f"{module_name} imports {imported} (layer {imported_layer}); "
                    f"layer {importer_layer} may only import {sorted(allowed)}"
                )
        return violations

    def check_source(self, module_name: str, source: str) -> list[str]:
        return self.check_imports(module_name, extract_imported_modules(source))


def extract_imported_modules(source: str) -> list[str]:
    tree = ast.parse(source)
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                imported.append(node.module)
    return imported
