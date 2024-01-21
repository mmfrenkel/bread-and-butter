import os
import requests


class SpoonacularAPI:

    def __init__(self):
        self.base_url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com",
            "X-RapidAPI-Key": self._get_api_key(),
        }

    @staticmethod
    def _get_api_key():
        """Fetches the api key from environmental variables."""
        if not os.getenv("SPOON_API_KEY"):
            raise RuntimeError("SPOON_API_KEY is not set")
        return os.getenv("SPOON_API_KEY")

    def get_recipes_by_ingredients(self, ingredients_list, number_of_results):
        """
        Finds recipes, based on a list of user-submitted ingredients.

        :param ingredients_list: list of ingredients as strings provided by user (e.g., ['chicken', 'apples', 'quinoa']
        :param number_of_results: int representing requested number of recipes
        :return: list of recipes (as individual dictionaries)
        """

        # Make sure that query is in the right format
        ingredients_formatted = self._format_list_for_query(ingredients_list)
        url = "{}/recipes/findByIngredients?number={}&ranking=1&ignorePantry=false&ingredients={}".format(
            self.base_url, number_of_results, ingredients_formatted
        )

        recipe_ids = self._get_recipe_ids(url, search_by_ingredients=True)
        return [self.get_recipe_by_id(recipe_id) for recipe_id in recipe_ids]

    def get_recipes_by_meal_item(self, item_type, number_of_results):
        """
        Finds recipes, based on the user-submitted item-type.

        :param item_type: strings representing item-type (e.g., 'main meal')
        :param number_of_results: int representing requested number of recipes
        :return: list of recipes (as individual dictionaries)
        """

        # Make sure that query is in the right format
        item_type_formatted = item_type[0].replace(" ", "+")
        url = "{}/recipes/search?number={}&offset=0&type={}".format(
            self.base_url, number_of_results, item_type_formatted
        )

        recipe_ids = self._get_recipe_ids(url)
        return [self.get_recipe_by_id(recipe_id) for recipe_id in recipe_ids]

    def get_recipes_by_allergy(self, allergies_list, number_of_results):
        """
        Finds recipes, based on a list of user-submitted dietary restrictions.

        :param allergies_list: list of ingredients as strings provided by user (e.g., ['gluten-free', 'dairy-free']
        :param number_of_results: int representing requested number of recipes
        :return: list of recipes (as individual dictionaries)
        """

        # Make sure that query is in the right format
        allergies_formatted = self._format_list_for_query(allergies_list)
        url = "{}/recipes/search?intolerances={}&number={}&offset=0".format(
            self.base_url, allergies_formatted, number_of_results
        )

        recipe_ids = self._get_recipe_ids(url)
        return [self.get_recipe_by_id(recipe_id) for recipe_id in recipe_ids]

    def get_random_recipe(self):
        """
        Get a random recipe, with nothing specified by user.
        :return: single recipe identifier (Spoonacular API recipe id)
        """

        url = "{}/recipes/random?number=1".format(self.base_url)
        return self._get_recipe_ids(url, random_recipe=True)[0]

    def _get_recipe_ids(self, url, random_recipe=False, search_by_ingredients=False):
        """
        Gets spoonacular API recipe ids based on search parameters.

        :param url: Formatted request url for Spoonacular API
        :param random_recipe: boolean, representing the question 'is the request for a random recipe?'
        :param search_by_ingredients: boolean, representing the question 'is the request a search by ingredients?'
        :return: list of recipe ids from the Spoonacular API
        """

        # Make the request
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise RuntimeError(
                f"Woah there, something went wrong with the Spoonacular API! "
                f'{response.status_code}: {response.json()["message"]}'
            )

        # Responses from API differ very slightly based on post request/category, but all provide ids
        if search_by_ingredients:
            return [recipe["id"] for recipe in response.json()]
        elif random_recipe:
            return [response.json()["recipes"][0]["id"]]
        else:
            return [recipe["id"] for recipe in response.json()["results"]]

    def get_recipe_by_id(self, recipe_id):
        """
        Gets a individual recipe as a formatted dictionary from the Spoonacular recipe/information endpoint.
        :param recipe_id: integer, representing Spoonacular API recipe id
        :return: dictionary containing information for one recipe
        """

        url = f"{self.base_url}/recipes/{recipe_id}/information"
        response = requests.get(url, headers=self.headers)
        return (
            self._format_recipe(response.json())
            if response.status_code == 200
            else None
        )

    @staticmethod
    def _format_recipe(recipe):
        """
        Formats a recipe returned from the Spoonacular API into a uniform format.
        :param recipe: json object returned from Spoonacular API for a single recipe
        :return: new dictionary object representing recipe
        """
        # Some fields are not consistently returned from the API, make sure they exist first.
        if "analyzedInstructions" in recipe.keys() and len(
            recipe["analyzedInstructions"]
        ):
            step_instructions = recipe["analyzedInstructions"][0]["steps"]
        else:
            step_instructions = None

        print(recipe)

        return {
            "spoonacular_id": recipe["id"],
            "dish_name": recipe["title"],
            "servings": recipe.get("servings", None),
            "image": recipe.get("image", None),
            "is_vegetarian": recipe["vegetarian"],
            "is_vegan": recipe["vegan"],
            "is_gluten_free": recipe["glutenFree"],
            "is_dairy_free": recipe["dairyFree"],
            "cook_time_min": SpoonacularAPI._get_execution_time_minutes(recipe, "cookingMinutes"),
            "prep_time_min": SpoonacularAPI._get_execution_time_minutes(recipe, "preparationMinutes"),
            "spoonacular_score": round(recipe["spoonacularScore"]),
            "ingredients": [
                ingredient["originalName"]
                for ingredient in recipe["extendedIngredients"]
            ],
            "instructions": recipe.get("instructions", None),
            "step_instructions": step_instructions,
        }

    @staticmethod
    def _get_execution_time_minutes(recipe_payload, key):
        value = recipe_payload.get(key, None)
        return value if value and value > 0 else None

    @staticmethod
    def _format_list_for_query(input_list):
        """
        Formats a list of items to be used in a HTTP POST request.
        :param input_list: a list of items to format (e.g., ['apples', 'chicken', 'quinoa']
        :return: formatted string, ready to be interested into request url (e.g., 'apples%2Cchicken%2Cquinoa')
        """
        return (
            ", ".join(input_list).replace(" ", "").replace("'", "").replace(",", "%2C")
        )
