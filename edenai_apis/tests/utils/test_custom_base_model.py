"""
Test our custom implementation of pydantic.BaseModel
"""
from edenai_apis.utils.parsing import NoRaiseBaseModel


class TestModel(NoRaiseBaseModel):
    expect_string: str
    expect_float: float
    expect_int: int


class TestModelWithNestedType(NoRaiseBaseModel):
    expect_dict: dict
    expect_list: list
    expect_model: TestModel


def test_validation_error_all_wrong_should_not_raise_exception():
    """should not raise exception, should set all values to None"""
    test_model = TestModel(expect_int="1", expect_float="1.0", expect_string=1)
    assert any(val is None for val in test_model.model_dump().values())


def test_validation_all_valid():
    test_model = TestModel(expect_int=1, expect_float=1.0, expect_string="one")
    assert test_model.expect_int == 1
    assert test_model.expect_float == 1.0
    assert test_model.expect_string == "one"


def test_validation_error_some_wrong_should_not_raise_exception():
    """
    should not raise exception,
    should set all wrong values to None
    should set valid values
    """
    test_model = TestModel(expect_int=1, expect_float="one", expect_string="1")
    assert test_model.expect_int == 1
    assert test_model.expect_float is None
    assert test_model.expect_string == "1"


def test_extra_field_should_not_be_present_in_result():
    test_model = TestModel(
        expect_int=1,
        expect_float=1.0,
        expect_string="",
        extra_field="this field should not appear in test_model",
    )
    assert not hasattr(test_model, "extra_field")


def test_with_nested_types():
    test_model = TestModel(
        expect_int=1,
        expect_float=1.0,
        expect_string="",
        extra_field="this field should not appear in test_model",
    )
    # no exception should be raised
    nest_model = TestModelWithNestedType(
        expect_dict=[], expect_list={}, expect_model=test_model
    )

    assert nest_model.expect_model.expect_int == 1
    assert nest_model.expect_model.expect_float == 1.0
    assert nest_model.expect_model.expect_string == ""
    assert nest_model.expect_dict is None
    assert nest_model.expect_list is None
