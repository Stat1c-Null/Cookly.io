import React from "react";

interface InputFieldProps {
  text: string;
  placeholder: string;
  value: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function InputField({
  text,
  placeholder,
  value,
  onChange,
}: InputFieldProps) {
  return (
    <div className="w-full">
      <label htmlFor="calories" className="block text-sm font-medium text-gray-700">
        {text}
      </label>
      <input
        type="text"
        id="calories"
        name="calories"
        value={value}
        onChange={onChange}
        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-black"
        placeholder={placeholder}
      />
    </div>
  );
}