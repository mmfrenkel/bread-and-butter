from flask import Flask, render_template, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os

from database import RecipeDatabase
from spoonacular_api import SpoonacularAPI


app = Flask(__name__)

# Configure flask
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# --- setup database
db = RecipeDatabase()
db.initiate_session()

# --- setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -- setup spoonacular API
spoonacular_api = SpoonacularAPI()


@login_manager.user_loader
def load_user(user_id):
    return db.get_user_by_id(user_id)


@app.route("/")
def index():
    """
    Default route; determines whether to send user to login or search based on if their session exists yet.
    """

    if current_user.is_authenticated:
        return redirect(url_for('search'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for exposing login page and handling login requests. Note that passwords are
    hashed before comparison with database passwords.
    """

    if request.method == 'POST':
        user = db.get_user_by_username(request.form.get('username'))

        if user:
            if check_password_hash(user.password, request.form.get('password')):
                login_user(user)
                return redirect(url_for('search'))

        return render_template('login.html', message="Credentials Invalid.")

    return render_template('login.html', message="")


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows user to get the webpage to provide their information (GET request) and ultimately
    register an account (POST request).
    """

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        # Cases where user input is insufficient
        if first_name in ["", " "]:
            return render_template('register.html', message='Please provide a first name.')
        elif last_name in ["", " "]:
            return render_template('register.html', message="Please provide a last name.")
        elif username in ["", " "]:
            return render_template('register.html', message="Please provide a username.")
        elif password in ["", " "]:
            return render_template('register.html', message="Please provide a password.")
        elif '@' not in email or email in ["", " "]:
            return render_template('register.html', message="Please provide a valid email.")
        elif db.username_exists(username):
            return render_template('register.html', registration_message='Sorry, this username already exists.')

        # If input is OK, add a new user to the database
        db.create_new_user(
            username=username,
            password=generate_password_hash(request.form.get('password'), method='sha256'),
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        return render_template('login.html', message='Successful Registration! Please Sign In.')

    return render_template('register.html', message="Please provide your information.")


@app.route('/search', methods=['GET'])
@login_required
def search():
    """
    Exposes the search page for users, once they've logged in.
    """
    return render_template('search.html', name=current_user.username)


@app.route('/recipes', methods=['POST'])
@login_required
def search_recipes():
    """
    Route that takes user search request and returns the results from the search to user, by category.
    """

    query_type = request.form.get('query_type')  # By item, ingredient, dietary restriction, random
    search_based_on = None

    # For any query type, find recipes by category and find if the item is saved by user.
    if query_type == 'item':
        recipe_list = spoonacular_api.get_recipes_by_meal_item(
            request.form.getlist('item'),
            number_of_results=10  # Results limited to 10 due to turn-around time.
        )
        recipe_list = assign_saved_by_user(recipe_list, current_user.username)   # Is the recipe saved by the user?
        search_based_on = request.form.getlist('item')                           # What user submitted for the search

    elif query_type == 'ingredients':
        recipe_list = spoonacular_api.get_recipes_by_ingredients(
            request.form.getlist('ingredient'),
            number_of_results=10
        )
        recipe_list = assign_saved_by_user(recipe_list, current_user.username)
        search_based_on = request.form.getlist('ingredient')

    elif query_type == 'allergies':
        recipe_list = spoonacular_api.get_recipes_by_allergy(
            request.form.getlist('allergies'),
            number_of_results=10
        )
        recipe_list = assign_saved_by_user(recipe_list, current_user.username)
        search_based_on = request.form.getlist('allergies')

    elif query_type == 'random':
        spoonacular_id = spoonacular_api.get_random_recipe()
        return redirect(url_for('details', spoonacular_id=spoonacular_id))

    else:
        recipe_list = None

    return render_template(
        'recipes.html',
        recipes=recipe_list,
        based_on=format_query(search_based_on),
        title="Recipes"
    )


@app.route('/recipe', methods=['GET', 'POST'])
@login_required
def recipe():
    """
    Handle the POST request, where user is interested in a specific recipe, otherwise, redirects
    user to the search page.
    """

    if request.method == 'GET':
        return redirect(url_for('search'))

    spoonacular_id = request.form.get('recipe_spoonacular_id')
    return redirect(url_for('details', spoonacular_id=spoonacular_id))


@app.route('/recipe/<int:spoonacular_id>', methods=['GET'])
@login_required
def details(spoonacular_id):
    """
    Given a spoonacular_id (ID of recipe from Spoonacular API) selected, get the recipe from the API
    and return individual recipe page to user.
    """

    single_recipe = spoonacular_api.get_recipe_by_id(spoonacular_id)
    single_recipe = assign_saved_by_user([single_recipe], current_user.username)[0]  # Is the recipe saved by the user?
    print(single_recipe)
    return render_template("single_recipe.html", recipe=single_recipe)


@app.route('/save_recipe', methods=['POST'])
@login_required
def save_recipe():
    """
    Allows user to store a recipe to keep under their 'saved recipes' tab.
    """

    try:
        spoonacular_id = request.values.get('spoonacular_id')

        # Add the new recipe only if not already saved for that user
        if spoonacular_id not in db.get_saved_recipes_by_user(current_user.username):
            db.save_recipe_for_user(
                spoonacular_id=spoonacular_id,
                username=current_user.username
            )

        return jsonify(
            {
                "success": True,
                "spoonacular_id": spoonacular_id
            }
        )
    except Exception as e:
        print(e)
        return jsonify({"success": False})


@app.route('/saved_recipes', methods=['GET'])
@login_required
def saved_recipes():
    """
    Invoked when user asks to see their saved recipes in the UI, gets all saved recipes from
    the database and returns them.
    """

    saved_recipes_ids = db.get_saved_recipes_by_user(current_user.username)
    recipe_list = [spoonacular_api.get_recipe_by_id(id) for id in saved_recipes_ids]
    recipe_list = assign_saved_by_user(recipe_list, current_user.username)

    return render_template(
        'recipes.html',
        recipes=recipe_list,
        title="Saved Recipes"
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("login.html", message="Logged Out!")


def format_query(list_query_items):
    """
    Formats the 'query items' (i.e., input provided by user in search page) into a formatted string
    (lowercase, comma delimited) that can easily by added to the recipe results page (lowercase,
    comma delimited).

    :param list_query_items: List of items submitted by user (e.g., ['Chicken', 'Apples']
    :return: String, a formatted version of the list (e.g., 'chicken, apples')
    """

    lowercase_items = [item.lower() for item in list_query_items]
    return str(lowercase_items). replace("[", "").replace("]", "").replace("'", "")


def assign_saved_by_user(recipe_list, username, database=db):
    """
    Takes a list of recipe dictionary and determines whether each recipe in the list is saved by the
    user already by adding a new key:value pair ('is_saved_by_user': boolean) to each dictionary object.

    :param recipe_list: List containing dictionaries, each representing one recipe
    :param database: The database to use for the query
    :param username: String, username of user
    :return: List containing dictionaries, now with 'is_saved_by_user' (boolean) field.
    """

    # Get all currently saved recipes...
    saved_recipes_ids = database.get_saved_recipes_by_user(username)
    new_recipe_list = []

    for recipe_dict in recipe_list:

        # ... Then determine if each one has already been saved by user.
        recipe_dict['is_saved_by_user'] = True if recipe_dict['spoonacular_id'] in saved_recipes_ids else False
        new_recipe_list.append(recipe_dict)

    return new_recipe_list


if __name__ == '__main__':
    app.run(debug=True)
