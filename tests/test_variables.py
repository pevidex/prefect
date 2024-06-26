import pytest

from prefect import flow
from prefect.variables import Variable


@pytest.fixture
async def variable():
    await Variable.set(name="my_variable", value="my-value", tags=["123", "456"])
    model = await Variable.get("my_variable", as_object=True)
    return model


async def test_set_sync(variable):
    @flow
    def test_flow():
        # confirm variable doesn't exist
        variable_doesnt_exist = Variable.get("my_new_variable")
        assert variable_doesnt_exist is None

        # create new
        Variable.set(name="my_new_variable", value="my_value", tags=["123", "456"])
        created = Variable.get("my_new_variable", as_object=True)
        assert created.value == "my_value"
        assert created.tags == ["123", "456"]

        # try to overwrite
        with pytest.raises(
            ValueError,
            match="You are attempting to set a variable with a name that is already in use. "
            "If you would like to overwrite it, pass `overwrite=True`.",
        ):
            Variable.set(name="my_new_variable", value="other_value")

        # actually overwrite
        Variable.set(
            name="my_new_variable",
            value="other_value",
            tags=["new", "tags"],
            overwrite=True,
        )
        updated = Variable.get("my_new_variable", as_object=True)
        assert updated.value == "other_value"
        assert updated.tags == ["new", "tags"]

    test_flow()


async def test_set_async(variable):
    # confirm variable doesn't exist
    variable_doesnt_exist = await Variable.get("my_new_variable")
    assert variable_doesnt_exist is None

    # create new
    await Variable.set(name="my_new_variable", value="my_value", tags=["123", "456"])
    created = await Variable.get("my_new_variable", as_object=True)
    assert created.value == "my_value"
    assert created.tags == ["123", "456"]

    # try to overwrite
    with pytest.raises(
        ValueError,
        match="You are attempting to set a variable with a name that is already in use. "
        "If you would like to overwrite it, pass `overwrite=True`.",
    ):
        await Variable.set(name="my_new_variable", value="other_value")

    # actually overwrite
    await Variable.set(
        name="my_new_variable",
        value="other_value",
        tags=["new", "tags"],
        overwrite=True,
    )
    updated = await Variable.get("my_new_variable", as_object=True)
    assert updated.value == "other_value"
    assert updated.tags == ["new", "tags"]


@pytest.mark.parametrize(
    "value",
    [
        "string-value",
        '"string-value"',
        123,
        12.3,
        True,
        False,
        None,
        {"key": "value"},
        ["value1", "value2"],
        {"key": ["value1", "value2"]},
    ],
)
async def test_json_types(value):
    await Variable.set("json_variable", value=value)
    assert await Variable.get("json_variable") == value


async def test_get(variable):
    # get value
    value = await Variable.get(variable.name)
    assert value == variable.value

    # as_object=True returns the full variable object
    obj = await Variable.get(variable.name, as_object=True)
    assert obj
    assert obj.id == variable.id
    assert obj.name == variable.name
    assert obj.value == variable.value

    # get value of a variable that doesn't exist
    doesnt_exist = await Variable.get("doesnt_exist")
    assert doesnt_exist is None

    # default is respected if it doesn't exist
    doesnt_exist_default = await Variable.get("doesnt_exist", 42)
    assert doesnt_exist_default == 42


async def test_get_async(variable):
    # get value
    value = await Variable.get(variable.name)
    assert value == variable.value

    # as_object=True returns the full variable object
    obj = await Variable.get(variable.name, as_object=True)
    assert obj
    assert obj.id == variable.id
    assert obj.name == variable.name
    assert obj.value == variable.value

    # get value of a variable that doesn't exist
    doesnt_exist = await Variable.get("doesnt_exist")
    assert doesnt_exist is None

    # default is respected if it doesn't exist
    doesnt_exist_default = await Variable.get("doesnt_exist", 42)
    assert doesnt_exist_default == 42


async def test_unset(variable):
    # unset a variable
    unset = await Variable.unset(variable.name)
    assert unset

    # confirm it's gone
    doesnt_exist = await Variable.get(variable.name)
    assert doesnt_exist is None

    # unset a variable that doesn't exist
    unset_doesnt_exist = await Variable.unset("doesnt_exist")
    assert not unset_doesnt_exist


async def test_unset_async(variable):
    # unset a variable
    unset = await Variable.unset(variable.name)
    assert unset

    # confirm it's gone
    doesnt_exist = await Variable.get(variable.name)
    assert doesnt_exist is None

    # unset a variable that doesn't exist
    unset_doesnt_exist = await Variable.unset("doesnt_exist")
    assert not unset_doesnt_exist


def test_get_in_sync_flow(variable):
    @flow
    def foo():
        var = Variable.get("my_variable")
        return var

    value = foo()
    assert value == variable.value


async def test_get_in_async_flow(variable):
    @flow
    async def foo():
        var = await Variable.get("my_variable")
        return var

    value = await foo()
    assert value == variable.value


def test_set_in_sync_flow():
    @flow
    def foo():
        Variable.set("my_variable", value="my-value")

    foo()
    value = Variable.get("my_variable")
    assert value


async def test_set_in_async_flow():
    @flow
    async def foo():
        await Variable.set("my_variable", value="my-value")

    await foo()
    value = await Variable.get("my_variable")
    assert value


async def test_unset_in_sync_flow(variable):
    @flow
    def foo():
        Variable.unset(variable.name)

    foo()
    value = await Variable.get(variable.name)
    assert value is None


async def test_unset_in_async_flow(variable):
    @flow
    async def foo():
        await Variable.unset(variable.name)

    await foo()
    value = await Variable.get(variable.name)
    assert value is None
