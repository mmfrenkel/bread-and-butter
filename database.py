import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *


class RecipeDatabase:
    def __init__(self):
        self.engine = None
        self.session = None

    def initiate_session(self):
        """Creates the SQLAlchemy Session to be used whenever a class method is used."""

        # Check for environment variable, warn if not available
        if not os.getenv("DATABASE_URL"):
            raise RuntimeError("DATABASE_URL is not set")

        try:
            self.engine = create_engine(os.getenv("DATABASE_URL"))
            self.session = scoped_session(sessionmaker(bind=self.engine))
        except Exception as e:
            print(f"Failed to create session, See more: {e}")

    def initialize(self):
        """Initializes the recipe database, if not existing, by creating all database tables."""

        self.initiate_session()
        Base.metadata.create_all(self.engine)

    def get_user_by_username(self, username):
        """
        Gets the User() object in the database for a given username.

        :param username: String, username of user
        :return: User() object
        """
        return self.session.query(User).filter_by(username=username).first()

    def get_user_by_id(self, user_id):
        """
        Gets the User() object in the database for a given user id.

        :param user_id: integer representing user_id in the Users table
        :return: User() object
        """

        return self.session.query(User).get(int(user_id))

    def username_exists(self, username):
        """
        Determines if the username is unavailable because it is already taken by
        another user.

        :param username: string, username submitted by user
        :return: boolean, if the username already exists
        """

        count = self.session.query(User).filter_by(username=username).count()
        return False if count == 0 else True

    def create_new_user(self, username, password, first_name, last_name, email):
        """
        Creates a new user in the database.

        :param username: string, submitted by user in UI
        :param password: string, submitted by user in UI
        :param first_name: string, submitted by user in UI
        :param last_name: string, submitted by user in UI
        :param email: string, submitted by user in UI
        """

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )

        self.session.add(new_user)
        self.session.commit()

    def save_recipe_for_user(self, spoonacular_id, username):
        """
        Saves a recipe for a given user, based on the spoonacular identifier in order to fetch
        again from the API on later requests.

        :param spoonacular_id: the identifier of the recipe from the spoonacular API
        :param username: string, the username of the user
        """

        user = self.get_user_by_username(username)
        new_saved_recipe = UserSavedRecipes(
            user_id=user.id, spoonacular_recipe_id=spoonacular_id
        )

        self.session.add(new_saved_recipe)
        self.session.commit()

    def get_saved_recipes_by_user(self, username):
        """
        Find all of the recipes already saved by a given user.

        :param username, string representing username of user
        :return: list of spoonacular database recipe ids saved by user already
        """

        user = self.get_user_by_username(username)
        saved_recipes = (
            self.session.query(UserSavedRecipes).filter_by(user_id=user.id).all()
        )
        return [recipe.spoonacular_recipe_id for recipe in saved_recipes]
