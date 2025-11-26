import pytest


class Sample:
    def __init__(self, value: int, name: str) -> None:
        self.value = value
        self.name = name

@pytest.fixture
def default_sample():
    return Sample(11, "Test")

def test_equal_or_not_equal():
    assert 3 == 3
    assert 5 != 10

def test_validate_instances(default_sample):
    assert default_sample.name == "Test"
    assert default_sample.value != 10
    assert isinstance("Hello", str)
    assert not isinstance("10", int)

def test_boolean():
    validated = True
    assert validated is True
    assert ("hello" == "world") is False

if __name__ == "__main__":
    pass