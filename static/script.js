var mealLoader = document.getElementById("mealLoader");
var imageLoader = document.getElementById("imageLoader")
//Analyze Image Button
document.getElementById("analyzeImageButton").addEventListener("click", function () {
    const fileInput = document.getElementById("ingredientsImage");
    const file = fileInput.files[0];
    imageLoader.style.display = "block";


    if (!file) {
        alert("Please select an image to analyze.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("/views/submitImage", {
        method: "POST",
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Error:", data.error);
        }
        //console.log(data["data"])
        const ingredientsTextBox = document.getElementById("ingredientsTextBox");
        ingredientsTextBox.value = data["data"];
        imageLoader.style.display = "none";
    })
    .catch(error => {
        console.error("Error:", error);
    });

});


//Submit Meal Button
document.getElementById("submitButton").addEventListener("click", function () {
  const form = document.getElementById("dietForm");
  const formData = new FormData(form);

  mealLoader.style.display = "block";

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
  localStorage.clear()
  sessionStorage.clear()

  document.getElementById("results").style.display = "block";
    // Ensure recipe is a string

  console.log(recipe)

  //Display data on the screen
  const mealName = document.getElementById("meal-name");
  //const ingredients = document.getElementById("meal-name");
  const instructions = document.getElementById("instructions");
  const notes = document.getElementById("notes");
  let keywords = ["Meal Name", "Ingredients", "Instructions", "Notes"];
  let extractedText = {};

  //Loop through each keyword and extract data between them
  keywords.forEach((word, index) => {
    if (index < keywords.length - 1) {
      // For all keywords except the last one
      let regex = new RegExp(`\\*\\*${word}:\\*\\*(.*?)\\*\\*${keywords[index + 1]}`, "gs");
      let match = regex.exec(recipe);
      if (match) {
        extractedText[word] = match[1].trim();
      }
    } else {
      // For the last keyword, capture everything after it
      let regex = new RegExp(`\\*\\*${word}:\\*\\*(.*)`, "gs");
      let match = regex.exec(recipe);
      if (match) {
        extractedText[word] = match[1].trim();
      }
    }
  });
  
  Object.keys(extractedText).forEach(key => {
    console.log(`\n${key}:\n${extractedText[key]}`);
  });

  //Display data
  mealName.innerText = extractedText["Meal Name"];

  //Loop through every ingridient and make <li> for it
  const ingredientsText = extractedText["Ingredients"];
  const ingredientsArray = ingredientsText
            .trim()                     
            .split("\n")                
            .map(line => line.trim())   
            .filter(line => line.startsWith("*")) 

  const listItemsHTML = ingredientsArray.map(ingredient => `<li class="list-group-item">${ingredient.slice(1).trim()}</li>`).join("");

  document.getElementById("ingredientsList").innerHTML = listItemsHTML;

  instructions.innerText = extractedText["Instructions"];
  notes.innerText = extractedText["Notes"];

  mealLoader.style.display = "none";
}

