import React from "react";

interface HoverButtonProps {
  text: string;
  onClick?: () => void;
}

export default function HoverButton({
  text,
  onClick,
}: HoverButtonProps) {
  return (
    <button className="px-6 py-3 text-white bg-blue-600 rounded-lg transition duration-300 ease-in-out transform hover:bg-blue-700 hover:scale-105" onClick={onClick}>
      {text}
    </button>
  );
}