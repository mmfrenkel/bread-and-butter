/**
 * @summary Javascript component of Bread&Butter Application
 * @file    Provides features required to save recipe items to the database.
 *
 * @author mmfrenkel <megan.frenkel@gmail.com>
 */

document.addEventListener('DOMContentLoaded', () => {

    // For every 'save recipe' button in the UI
    document.querySelectorAll('.save').forEach(button => {
        button.onclick = saveRecipe;
        return false;
    })
})

/*
 * Prompted when a user clicks on a 'save recipe' button in the UI, this method sends the
 * spoonacular api identifier (spoonacular_id) to the server to save and re-formats the
 * clicked button to be 'inactive' if request successful.
 *
 * @param Event; the 'onsubmit' event when user clicks 'Enter' button
 */
function saveRecipe(e) {

    // Get the identifier of the recipe to save in the db
    const spoonacular_id = e.target.id.split("-")[1];

    const request = new XMLHttpRequest();
    request.open('POST', '/save_recipe');

    // Callback function for when request completes
    request.onload = () => {

        debugger;
        const data = JSON.parse(request.responseText);

        // If the request was successful, then change the button's appearance to make it clear that
        // the recipe has been saved.
        if (data.success) {

            // Get the button of interest
            var buttonId = 'button-'.concat(data.spoonacular_id);
            var buttonClicked = document.getElementById(buttonId);

            // Change all aspects of the button to reflect the saving of recipe
            buttonClicked.innerHTML = '<i class="fa fa-check-circle" aria-hidden="true"></i>' + ' Saved Recipe!';
            buttonClicked.style.backgroundColor = "lightgrey";
            buttonClicked.disabled = true;
            buttonClicked.className = tab.className.replace(" save", " checked");
        }
    }

    // Ask server to get all messages stored for the channel
    const data = new FormData();
    data.append('spoonacular_id', spoonacular_id);
    request.send(data);
    return false;
}
