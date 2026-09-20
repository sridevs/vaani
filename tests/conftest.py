import pytest


def pytest_collection_modify_items(config, items):
    for item in items:
        if "tests/adapters/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.adapters)
        elif "tests/components/" in str(item.fspath).replace("\\", "/"):
            item.add_marker(pytest.mark.application)
