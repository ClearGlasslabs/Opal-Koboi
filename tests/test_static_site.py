from pathlib import Path

from security.validate_static_site import PageParser, validate


def test_release_artifact_references_are_publishable() -> None:
    assert validate(Path(__file__).parents[1]) == []


def test_page_parser_reports_duplicate_ids() -> None:
    parser = PageParser()
    parser.feed('<main id="content"></main><footer id="content"></footer>')

    assert parser.duplicate_ids == {"content"}


def test_page_parser_keeps_empty_references_for_validation() -> None:
    parser = PageParser()
    parser.feed('<a href="#">Broken link</a><img src="" alt="Broken image">')

    assert parser.references == [("href", "#"), ("src", "")]
