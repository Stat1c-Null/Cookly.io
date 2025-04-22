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

async function POST(formData, link, image, updateIngredientsCallback) {
  
  try {
    const response = await fetch(link, {
      method: 'POST',
      body: formData,
    });
    
    let data = null;
    if(image) {
      data = await response.json();
      if(updateIngredientsCallback && data["data"]) {
        updateIngredientsCallback(data["data"])
      }

      let loader = document.getElementById("image-loader")
      loader.style.display = "none"
    } else {
      data = await response.text();
      processingIngridients();
      
    }
    console.log("printed out data")
    console.log(data);

    return data;
  } catch (error) {
    console.error('Error sending request to backend:', error);
    return { error: 'Failed to fetch data from backend' }
  }
}

function generateMeal(calorieValue, proteinValue, fatsValue, carbsValue, peopleValue, selectedAllergens, otherAllergen, ingredients) {
  let loader = document.getElementById("recipe-loader")
  loader.style.display = "block"
  
  const formData = new FormData();
  formData.append('calorieInput', calorieValue);
  formData.append('proteinInput', proteinValue);
  formData.append('fatsInput', fatsValue);
  formData.append('carbsInput', carbsValue);
  formData.append('peopleInput', peopleValue);
  formData.append('selectedAllergens', selectedAllergens);
  formData.append('other', otherAllergen);
  formData.append('ingredientsTextBox', ingredients);
  POST(formData, 'http://127.0.0.1:8000/views/submit/', false, null)
}

function analyzeIngredients(selectedFile, updateIngredientsCallback) {
  console.log(selectedFile);

  let loader = document.getElementById("image-loader")
  loader.style.display = "block"

  const formData = new FormData();
  formData.append('file', selectedFile)
  POST(formData, 'http://127.0.0.1:8000/views/submitImage/', true, updateIngredientsCallback)
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

  if(result.title && result.ingredients && result.directions && result.link) {
    displayRecipe(result.title, result.ingredients, result.directions, result.link);
  } else {
    setTimeout(checkRecipe, 1000);

  }
}

function displayRecipe(title, recipe, directions, link) {
  localStorage.clear()
  sessionStorage.clear()

  document.getElementById("results").style.display = "block";
  console.log(title)
  console.log(recipe)
  console.log(directions)
  console.log(link)

  const mealName = document.getElementById("meal-name");
  const instructions = document.getElementById("instructions");
  const notes = document.getElementById("notes");
  const ingredientsList = document.getElementById("ingredientsList");
  const results = document.getElementById("results")
  results.style.display = "flex"

  //Place title
  mealName.innerText = title

  //Place ingredients
  const ingredientsText = recipe[0]

  const ingredientLines = ingredientsText.split('\n')

  // Clear previous ingredients
  ingredientsList.innerHTML = '';

  ingredientLines.forEach(line => {
    const li = document.createElement('li');
    li.className = "px-6 py-3 text-gray-700";
    li.textContent = line;
    ingredientsList.appendChild(li);
  })

  const instructionsList = directions[0]

  const instructionsLines = instructionsList.split('\n')

  instructions.innerHTML = ''

  let counter = 1;

  instructionsLines.forEach(line => {
    const p = document.createElement('p');
    p.textContent = counter + ". " + line
    instructions.appendChild(p)
    counter++;
  })

  notes.innerHTML = ""

  const par = document.createElement('p')
  par.textContent = "Link to the website with a recipe"

  const websiteLink = document.createElement('a')
  websiteLink.href = "https://" + link
  websiteLink.textContent = "Visit website by clicking here"
  notes.appendChild(par)
  notes.appendChild(websiteLink)

  let loader = document.getElementById("recipe-loader")
  loader.style.display = "none"
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

      <main className="flex flex-col gap-10 row-start-2 items-center max-w-4xl">
        
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
          <Image
            src="/bluelogo.png" // Route of the image file
            alt="Logo"
            width={150}
            height={100}
            priority={false} // Set to true for above-the-fold images
          />
        </div>

        <h1 className="text-blue-500 text-3xl font-bold">Diet Details Form</h1>
        <p className="text-black font-medium text-lg text-center">Upload photo of your ingredients and fill out the form. Cookly.io will analyze all of the ingredients and generate you a list of meals based on your macros. Leave fields blank if limit is not required</p>
        
        {/*Calories input*/}
        <InputField text="Calorie Limit" placeholder="Enter the limit of calories that you want to have" value={calorieValue} onChange={handleCalorieChange} example="Avg. 300-700 calories" name="calories"/>

        {/*Calories input*/}
        <InputField text="Desired Protein Intake" placeholder="Enter how much protein intake you are aiming to have" value={proteinValue} onChange={handleProteinChange} example="Avg. 15-30 grams" name="protein"/>

        {/*Fats input*/}
        <InputField text="Fats Limit" placeholder="Enter limit for fats" value={fatsValue} onChange={handleFatsChange} example="Avg. 15-25 grams" name="fats"/>

        {/*Carbohydrates input*/}
        <InputField text="Desired Carb Intake" placeholder="Enter limit of carbohydrates" value={carbsValue} onChange={handleCarbsChange} example="Avg. 75-110 grams" name="carbs"/>

        {/*Number of people input*/}
        <InputField text="Number of people" placeholder="Enter how many people will be having the meal" value={peopleValue} onChange={handlePeopleChange} example="Avg. 1-4 people" name="people"/>

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
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200 text-black"
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
            className="w-full border border-gray-300 p-2 rounded-md text-gray-700 hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200"
          />
          {selectedFile && (
            <p className="mt-2 text-sm text-gray-700">Selected: {selectedFile.name}</p>
          )}
        </div>

        {/*Analyze ingredients button*/}

        <HoverButton text="Analyze Ingredients" onClick={() => analyzeIngredients(selectedFile, setIngredientsValue)}/>

        {/*Image Loader */}
        <div className="flex items-center justify-center" id="image-loader" style={{display: 'none'}}>
          <div className="w-6 h-6 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>

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
            className="mt-1 block w-full px-3 py-6 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200 sm:text-sm text-black"
            placeholder="Analyzed Ingredients will go here or you can write out your ingredients."
          />
        </div>

        {/*Generate meal button */}
        <HoverButton text="Generate Meal" onClick={() => generateMeal(calorieValue, proteinValue, fatsValue, carbsValue, peopleValue, selectedAllergens, otherAllergen, ingredientsValue)}/>

        {/*Image Loader */}
        <div className="flex items-center justify-center" id="recipe-loader" style={{display: 'none'}}>
          <div className="w-6 h-6 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>

        {/*Results */}
        <div className="flex justify-center w-full mt-8" id="results" style={{display: 'none'}}>
          <div id="results" className="w-full max-w-2xl bg-white rounded-lg shadow-sm">
            {/* Title */}
            <h5 id="meal-name" className="text-2xl font-bold text-center py-4 text-blue-500">
              Simple Olive Oil and Herb Drizzle
            </h5>
            
            {/* Ingredients */}
            <div className="border rounded-md border-gray-400 mb-6">
              <div className="bg-gray-100 px-6 py-3 text-lg font-medium text-gray-800 rounded-md">
                Ingredients
              </div>
              <ul className="list-group list-group-flush divide-y divide-gray-400" id="ingredientsList">
                {/* Ingredients will be populated here */}
                <li className="px-6 py-3 text-gray-700">2 tablespoons olive oil</li>
                <li className="px-6 py-3 text-gray-700">Salt and pepper to taste</li>
              </ul>
            </div>
            
            {/* Instructions */}
            <div className="border rounded-md border-gray-400 mb-6">
              <div className="bg-gray-100 px-6 py-3 text-lg font-medium text-gray-800 rounded-md">
                Instructions
              </div>
              <div className="px-6 py-4">
                <ol className="list-decimal list-inside space-y-2 text-gray-700 rounded-md" id="instructions">
                  <li>Combine olive oil, salt, and pepper in a small bowl.</li>
                  <li>Whisk to combine.</li>
                </ol>
              </div>
            </div>
            
            {/* Notes */}
            <div className="border rounded-md border-gray-400 mb-6">
              <div className="bg-gray-100 px-6 py-3 text-lg font-medium text-gray-800 rounded-md">
                Notes
              </div>
              <div className="px-6 py-4">
                <p className="text-gray-700" id="notes">
                  This is best used as a condiment, drizzled over cooked vegetables, bread, or a simple grain like rice or quinoa (if you have those available). Consider adding other seasonings or herbs if you have them on hand to enhance the flavor. The nutritional information is highly variable depending on what you use it on.
                </p>
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
