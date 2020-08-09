import pytest
import modules.utils as utils


def test_is_text():
    content_type = "text/html"
    assert utils.is_text(content_type)
