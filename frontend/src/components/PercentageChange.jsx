// components/PercentageChange.jsx
import React from "react";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

export default function PercentageChange({ change }) {
  const isPositive = change >= 0;

  return (
    <div className={`flex items-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
      {isPositive ? <FaArrowUp className="w-3 h-3" /> : <FaArrowDown className="w-3 h-3" />}
      <span>{Math.abs(change)}%</span>
    </div>
  );
}
