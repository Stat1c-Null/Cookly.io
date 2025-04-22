import React from "react";

interface InputFieldProps {
  text: string;
  placeholder: string;
  value: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  example: string;
  name: string;
}

export default function InputField({
  text,
  placeholder,
  value,
  onChange,
  example,
  name,
}: InputFieldProps) {
  const inputID = `input-${name}`;
  return (
    <div className="w-full">
      <label htmlFor="calories" className="block text-sm font-medium text-gray-700">
        {text}
      </label>
      <input
        type="text"
        id={inputID}
        name={name}
        value={value}
        onChange={onChange}
        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200 sm:text-sm text-black"
        placeholder={placeholder}
      />
      {example && (
        <label htmlFor="calories" className="block text-sm font-small font-light text-gray-700">
          {example}
        </label>
      )}
      
    </div>
  );
}