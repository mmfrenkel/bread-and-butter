
class RecipeDatabaseMock:

    # caller provides one keyword argument per query involved in the test
    def __init__(self, **kwargs):
        self.mocks = kwargs

    def get_user_by_username(self, username):
        return self.mocks['get_user_by_username']

    def get_user_by_id(self, user_id):
        return self.mocks['get_user_by_id']

    def username_exists(self, username):
        return self.mocks['username_exists']

    def create_new_user(self, username, password, first_name, last_name, email):
        pass

    def save_recipe_for_user(self, spoonacular_id, username):
        pass

    def get_saved_recipes_by_user(self, username):
        return self.mocks['recipes_by_user']
