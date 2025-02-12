'use client'

import Image from "next/image";
import { useState } from "react";
import HoverButton from "@/components/HoverButton";

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

export default function Home() {
  //Form values input
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  //Allergies selector
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [otherAllergen, setOtherAllergen] = useState("");

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
        <div className="w-full">
          <label htmlFor="calories" className="block text-sm font-medium text-gray-700">
            Calorie Limit
          </label>
          <input
            type="text"
            id="calories"
            name="calories"
            value={inputValue}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Enter the limit of calories that you want to have"
          />
        </div>

        {/*Calories input*/}
        <div className="w-full">
          <label htmlFor="protein" className="block text-sm font-medium text-gray-700">
            Desired Protein Intake
          </label>
          <input
            type="text"
            id="protein"
            name="protein"
            value={inputValue}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Enter how much protein intake you are aiming to have"
          />
        </div>

        {/*Fats input*/}
        <div className="w-full">
          <label htmlFor="fats" className="block text-sm font-medium text-gray-700">
            Fats Limit
          </label>
          <input
            type="text"
            id="fats"
            name="fats"
            value={inputValue}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Enter limit for fats"
          />
        </div>

        {/*Carbohydrates input*/}
        <div className="w-full">
          <label htmlFor="carbs" className="block text-sm font-medium text-gray-700">
            Desired Carbs Intake
          </label>
          <input
            type="text"
            id="carbs"
            name="carbs"
            value={inputValue}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Enter limit for carbohydrates"
          />
        </div>

        {/*Number of people input*/}
        <div className="w-full">
          <label htmlFor="people" className="block text-sm font-medium text-gray-700">
            Number of people
          </label>
          <input
            type="text"
            id="people"
            name="people"
            value={inputValue}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Enter how many people will be having the meal"
          />
        </div>

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
              checked={!!otherAllergen}
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
              className="w-full p-2 border border-gray-300 rounded-md mt-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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

        <HoverButton text="Analyze Ingredients" onClick={() => alert("test")}/>

        {/*Analyzed ingredients input*/}
        <div className="w-full">
          <label htmlFor="ingredients" className="block text-sm font-medium text-gray-700">
            Ingredients
          </label>
          <textarea
            type="text"
            id="ingredients"
            name="ingredients"
            value={inputValue}
            onChange={handleInputChange}
            className="mt-1 block w-full px-3 py-6 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
            placeholder="Analyzed Ingredients will go here or you can write out your ingredients."
          />
        </div>

        {/*Generate meal button */}
        <HoverButton text="Generate Meal" onClick={() => alert("test")}/>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          
        </div>

      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        <p className="text-black">Tsunami Surfers &copy; 2025</p>
      </footer>
    </div>
  );
}
