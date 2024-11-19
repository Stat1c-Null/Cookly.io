document.getElementById("submitButton").addEventListener("click", function () {
  const form = document.getElementById("dietForm");
  const formData = new FormData(form);

  fetch("/views/submit", {
      method: "POST",
      body: formData,
  })
  .then((response) => response.text())
  .then((data) => {
      // Show confirmation message
      document.getElementById("confirmationMessage").style.display = "block";

      processingIngridients();

      // Clear the form inputs
      form.reset();
  })
  .catch((error) => {
      console.error("Error submitting form:", error);
  });
});

async function processingIngridients() {
  //Wait for data to reach Gemini
  await fetch("/views/submit");

  checkRecipe();
}

async function checkRecipe() {
  //Wait for Gemini to return data back
  const response = await fetch("/views/fetch_data");
  const result = await response.json();
  if(result.data) {
    displayRecipe(result.data);
  } else {
    setTimeout(checkRecipe, 1000);
  }
}

function displayRecipe(recipe) {
  //Display data on the screen
  const recipeDiv = document.getElementById("results");
  const result = recipe.replace(/\*/g, "<br>");
  console.log(result);
  recipeDiv.innerHTML = `<p>${result}</p>`;
}

