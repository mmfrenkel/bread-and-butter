import pytest
from application import format_query, assign_saved_by_user
from spoonacular_api import SpoonacularAPI
from tests.mock_db import RecipeDatabaseMock


@pytest.fixture()
def api():
    return SpoonacularAPI()


def test_application_format_query():

    list_query_elements = ['apples', 'peanuts', 'bananas']
    expected = 'apples, peanuts, bananas'
    result = format_query(list_query_elements)

    assert expected == result


def test_api_format_query(api):

    list_query_elements = ['apples', 'peanuts', 'bananas']
    expected = 'apples%2Cpeanuts%2Cbananas'
    result = api._format_list_for_query(list_query_elements)

    assert expected == result


def test_api_format_recipe(api):

    from tests.example_recipe import example_recipe, formatted_recipe

    expected = formatted_recipe
    result = api._format_recipe(example_recipe)

    assert result == expected


def test_assign_saved():

    recipes = [
        {'spoonacular_id': 2345},
        {'spoonacular_id': 7820},
        {'spoonacular_id': 5323},
        {'spoonacular_id': 1231}
    ]

    mock_saved_recipes = [2345, 5323]
    mock = RecipeDatabaseMock(recipes_by_user=mock_saved_recipes)

    result = assign_saved_by_user(recipe_list=recipes, username='test_user', database=mock)
    expected = [
        {'spoonacular_id': 2345, 'is_saved_by_user': True},
        {'spoonacular_id': 7820, 'is_saved_by_user': False},
        {'spoonacular_id': 5323, 'is_saved_by_user': True},
        {'spoonacular_id': 1231, 'is_saved_by_user': False}
    ]

    assert result == expected