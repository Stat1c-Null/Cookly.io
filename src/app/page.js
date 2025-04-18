'use client'

import Image from "next/image";
import { useState } from "react";
import HoverButton from "@/components/HoverButton";
import InputField from "@/components/InputField";

const allergensList = [
  "Dairy",
  "Eggs",
  "Fish",
  "Shellfish",
  "Peanuts",
  "Soy",
  "Wheat",
  "Tree Nuts",
  "Sesame",
  "Gluten-Free",
];

async function POST(formData, link, image) {
  try {
    const response = await fetch(link, {
      method: 'POST',
      body: formData,
    });
    console.log("I work")
    
    let data = null;
    if(image) {
      data = await response.json();
      const ingredientsTextBox = document.getElementById("ingredients");
      ingredientsTextBox.value = data["data"];
    } else {
      data = await response.text();
      processingIngridients();
    }
    console.log(data);
    console.log("printed out data")
    return data;
  } catch (error) {
    console.error('Error sending request to backend:', error);
    return { error: 'Failed to fetch data from backend' }
  }
}

function generateMeal(calorieValue, proteinValue, fatsValue, carbsValue, peopleValue, selectedAllergens, otherAllergen, ingredients) {
  console.log(calorieValue, proteinValue, fatsValue, carbsValue, peopleValue, selectedAllergens, otherAllergen, ingredients)

  const formData = new FormData();
  formData.append('calorieInput', calorieValue);
  formData.append('proteinInput', proteinValue);
  formData.append('fatsInput', fatsValue);
  formData.append('carbsInput', carbsValue);
  formData.append('peopleInput', peopleValue);
  formData.append('selectedAllergens', selectedAllergens);
  formData.append('other', otherAllergen);
  formData.append('ingredientsTextBox', ingredients);
  POST(formData, 'http://127.0.0.1:8000/views/submit/', false)
}

function analyzeIngredients(selectedFile) {
  console.log(selectedFile);
  const formData = new FormData();
  formData.append('file', selectedFile)
  POST(formData, 'http://127.0.0.1:8000/views/submitImage/', true)
}

async function processingIngridients() {
  //Wait for data to reach Gemini
  await fetch("http://127.0.0.1:8000/views/submit/");

  checkRecipe();
}

async function checkRecipe() {
  //Wait for Gemini to return data back
  const response = await fetch("http://127.0.0.1:8000/views/fetch_data/");
  console.log(response);
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

  //mealLoader.style.display = "none";
}

export default function Home() {
  //Form values input
  const [proteinValue, setProteinValue] = useState("");
  const [calorieValue, setCalorieValue] = useState("");
  const [carbsValue, setCarbsValue] = useState("");
  const [fatsValue, setFatsValue] = useState("");
  const [peopleValue, setPeopleValue] = useState("");
  const [ingredientsValue, setIngredientsValue] = useState("");

  const handleProteinChange = (e) => {
    setProteinValue(e.target.value);
  };

  const handleCalorieChange = (e) => {
    setCalorieValue(e.target.value);
  };

  const handleCarbsChange = (e) => {
    setCarbsValue(e.target.value);
  };

  const handleFatsChange = (e) => {
    setFatsValue(e.target.value);
  };

  const handlePeopleChange = (e) => {
    setPeopleValue(e.target.value);
  };

  const handleIngredientsChange = (e) => {
    setIngredientsValue(e.target.value);
  };

  //Allergies selector
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [otherAllergen, setOtherAllergen] = useState(null);

  const handleCheckboxChange = (allergen) => {
    setSelectedAllergens((prev) =>
      prev.includes(allergen)
        ? prev.filter((item) => item !== allergen)
        : [...prev, allergen]
    );
  };

  //Ingredients Upload
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  return (
    <div className="bg-white grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      
      <main className="flex flex-col gap-10 row-start-2 items-center sm:items-start max-w-4xl">
        <h1 className="text-sky-400 text-3xl font-bold">Diet Details Form</h1>
        <p className="text-black font-medium text-lg">Upload photo of your ingredients and fill out the form. Cookly.io will analyze all of the ingredients and generate you a list of meals based on your macros. Leave fields blank if limit is not required</p>
        
        {/*Calories input*/}
        <InputField text="Calorie Limit" placeholder="Enter the limit of calories that you want to have" value={calorieValue} onChange={handleCalorieChange} example="Avg. 300-700 calories"/>

        {/*Calories input*/}
        <InputField text="Desired Protein Intake" placeholder="Enter how much protein intake you are aiming to have" value={proteinValue} onChange={handleProteinChange} example="Avg. 15-30 grams"/>

        {/*Fats input*/}
        <InputField text="Fats Limit" placeholder="Enter limit for fats" value={fatsValue} onChange={handleFatsChange} example="Avg. 15-25 grams"/>

        {/*Carbohydrates input*/}
        <InputField text="Desired Carb Intake" placeholder="Enter limit of carbohydrates" value={carbsValue} onChange={handleCarbsChange} example="Avg. 75-110 grams"/>

        {/*Number of people input*/}
        <InputField text="Number of people" placeholder="Enter how many people will be having the meal" value={peopleValue} onChange={handlePeopleChange} />

        {/*Allergens*/}
        <div className="w-full">
          <fieldset>
            <legend className="text-sm font-medium mb-2 text-gray-700">Allergens</legend>
            <div className="grid grid-cols-2 gap-2">
              {allergensList.map((allergen) => (
                <label key={allergen} className="flex items-center text-black">
                  <input
                    type="checkbox"
                    value={allergen}
                    checked={selectedAllergens.includes(allergen)}
                    onChange={() => handleCheckboxChange(allergen)}
                    className="mr-2"
                  />
                  {allergen}
                </label>
              ))}
            </div>
          </fieldset>

          <label className="flex items-center mt-3 text-black">
            <input
              type="checkbox"
              checked={otherAllergen !== null}
              onChange={(e) => setOtherAllergen(e.target.checked ? "" : null)}
              className="mr-2"
            />
            Other
          </label>
          {otherAllergen !== null && (
            <input
              type="text"
              placeholder="Specify other allergens"
              value={otherAllergen}
              onChange={(e) => setOtherAllergen(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            />
          )}
        </div>

        {/*Ingredients upload */}

        <div className="w-full">
          <label className="block text-sm font-semibold mb-2 text-gray-700">
            Upload photo of your ingredients
          </label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full border border-gray-300 p-2 rounded-md text-gray-700"
          />
          {selectedFile && (
            <p className="mt-2 text-sm text-gray-700">Selected: {selectedFile.name}</p>
          )}
        </div>

        {/*Analyze ingredients button*/}

        <HoverButton text="Analyze Ingredients" onClick={() => analyzeIngredients(selectedFile)}/>

        {/*Analyzed ingredients input*/}
        <div className="w-full">
          <label htmlFor="ingredients" className="block text-sm font-medium text-gray-700">
            Ingredients
          </label>
          <textarea
            type="text"
            id="ingredients"
            name="ingredients"
            value={ingredientsValue}
            onChange={handleIngredientsChange}
            className="mt-1 block w-full px-3 py-6 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Analyzed Ingredients will go here or you can write out your ingredients."
          />
        </div>

        {/*Generate meal button */}
        <HoverButton text="Generate Meal" onClick={() => generateMeal(calorieValue, proteinValue, fatsValue, carbsValue, peopleValue, selectedAllergens, otherAllergen, ingredientsValue)}/>


        {/*Results */}
        <div className="flex gap-4 items-center flex-col sm:flex-row">
        <div id="results">
          <h5 id="meal-name"></h5>
          {/*Ingridients*/}
          <div className="card">
            <div className="card-header">Ingredients</div>
            <ul className="list-group list-group-flush" id="ingredientsList">

            </ul>
          </div>
          {/*Instructions*/}
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Instructions</h5>
              <p className="card-text" id="instructions"></p>
            </div>
          </div>
          {/*Notes*/}
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Notes</h5>
              <p className="card-text" id="notes"></p>
            </div>
          </div>
        </div>
        </div>

      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        <p className="text-black">Tsunami Surfers &copy; 2025</p>
      </footer>
    </div>
  );
}
