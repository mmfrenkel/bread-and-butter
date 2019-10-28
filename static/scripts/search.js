/**
 * @summary Javascript component of Bread&Butter Application related to search functionality,
 *          including showing search questions by category, adding new ingredients to the search,
 *          and showing a page loader.
 *
 * @author mmfrenkel <megan.frenkel@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // Open search option when a user clicks on a search category
    document.querySelectorAll('.category').forEach(button => {
        button.onclick = openSearchOption;
        return false;
    })

    // Add another ingredient input box, if user wants it
    document.getElementById('add-another-ingredient').onclick = () => {
        addNewIngredient();
        return false;
    }

    // Search request may take time, so assure user their request is being processed by showing a loader
    document.querySelectorAll('.get-recipes').forEach(button => {
        button.onclick = showLoader;
        return false;
    })
})

/*
 * Prompted when a user clicks on a search button, method "opens" up additional
 * questions in the search page by making them visible.
 */
function openSearchOption() {

    // Make other panels display as none
    const searchInput = document.getElementsByClassName("search-input");
    for (let search of searchInput) {
        search.style.display = "none";
    }
    // the category attribute of the button is equal to the id of the content box to display
    const inputCategory = this.dataset.category;
    const displayBox = document.getElementById(inputCategory);

    if (displayBox) {
        displayBox.style.display = "block";
    }
}

/**
 * Prompted when a user wants to add a new pantry ingredient to the list of ingredients.
 **/
function addNewIngredient() {

    // get all current ingredients added by user as Array
    let entries = Array.from(document.getElementsByName('ingredient'));
    let ingredients = [];
    for (item in entries) {
        ingredients.push(entries[item].value)
    }

    // get the new ingredient template and add new line item to HTML
    const template = Handlebars.compile(document.querySelector('#new-ingredient').innerHTML);
    const content = template();
    document.querySelector('#ingredient-line-items').innerHTML += content;

     // JS removes prior entries when adding new HTML content, so add previous ingredients submitted back to HTML
    let user_items = Array.from(document.getElementsByName('ingredient'))
    for (let i = 0; i < ingredients.length; i++) {
        user_items[i].value = ingredients[i];
    }
}

/*
 * Makes the page loader visible when a user submits a search request to clarify
 * that the request is in progress, even though it may take time to complete and return
 * back search results.
 */
function showLoader(e) {
    const loader = document.querySelector(".loader");
    loader.className = loader.className.replace("hiding", "visible");
}
