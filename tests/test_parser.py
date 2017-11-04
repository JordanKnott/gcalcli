from gcalcli3 import gcal
import pytest


def test_color_parser_single_valid_option():
    """Test that a single valid option is parsed correctly"""
    set_color = [("border", "ff2244")]
    colors = gcal.parse_color_options(set_color)
    assert colors == {"border_color": "ff2244"}


def test_color_parser_all_valid_options():
    """Test that all valid options are parsed correctly"""
    set_color = [("owner", "ffffff"), ("writer", "ffffff"),
                 ("reader", "ffffff"), ("freebusy", "ffffff"),
                 ("date", "4422ff"), ("nowmarker", "113322"),
                 ("border", "ff2211")]
    colors = gcal.parse_color_options(set_color)
    assert colors == {
        "owner_color": "ffffff",
        "writer_color": "ffffff",
        "reader_color": "ffffff",
        "freebusy_color": "ffffff",
        "date_color": "4422ff",
        "nowmarker_color": "113322",
        "border_color": "ff2211"
    }


def test_color_parser_no_options():
    """Verify that no options simply returns an empty list"""
    set_color = []
    assert len(gcal.parse_color_options(set_color)) == 0


def test_color_parser_single_invalid_type_option():
    """Test that an invalid type throws an exception"""
    set_color = [("brder", "ffffff")]
    with pytest.raises(ValueError):
        colors = gcal.parse_color_options(set_color)


def test_color_parser_single_invalid_color_option():
    """TODO: Test that an invalid color throws an expression"""
    pass
