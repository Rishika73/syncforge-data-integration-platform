
import pytest

from syncforge.connectors.base import SourceConnector


def test_source_connector_cannot_be_instantiated():
    with pytest.raises(TypeError):
        SourceConnector()


def test_incomplete_connector_cannot_be_instantiated():
    class IncompleteConnector(SourceConnector):
        def connect(self):
            pass

    with pytest.raises(TypeError):
        IncompleteConnector()
