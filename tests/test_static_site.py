from pathlib import Path

from security.validate_static_site import validate


def test_release_artifact_references_are_publishable() -> None:
    assert validate(Path(__file__).parents[1]) == []
