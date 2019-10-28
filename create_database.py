"""Creates the database tables, if not already existing."""

from database import RecipeDatabase

if __name__ == "__main__":
    db = RecipeDatabase()
    db.initialize()
