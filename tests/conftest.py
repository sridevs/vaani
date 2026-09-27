import pytest


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "tests/adapters/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.adapters)
        elif "tests/application/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.application)
