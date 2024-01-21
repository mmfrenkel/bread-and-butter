from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from dictalchemy import DictableModel
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base(cls=DictableModel)


class User(Base, UserMixin):
    """Represents a single application user."""

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(15), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(200)) # long enough to hold scrypt hash

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'


class UserSavedRecipes(Base):
    """Saves a recipe id and user id in order to store recipes for later viewing."""

    __tablename__ = 'user_saved_recipes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    spoonacular_recipe_id = Column(Integer)

    def __repr__(self):
        return 'UserSavedRecipes({})'.format(str(self.asdict(exclude_pk=True))[1:-1])

