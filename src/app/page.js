'use client'

import Image from "next/image";
import { useState } from "react";

export default function Home() {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  return (
    <div className="bg-white grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      
      <main className="flex flex-col gap-10 row-start-2 items-center sm:items-start max-w-4xl">
        <h1 className="text-sky-600 text-3xl font-bold">Diet Details Form</h1>
        <p className="text-black font-medium text-lg">Upload photo of your ingredients and fill out the form. Cookly.io will analyze all of the ingredients and generate you a list of meals based on your macros. Leave fields blank if limit is not required</p>
        
        {/*Calories input*/}
        <div className="w-full">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
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
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
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
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
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
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
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
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
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

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          
        </div>

      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        <p className="text-black">Tsunami Surfers &copy; 2025</p>
      </footer>
    </div>
  );
}
