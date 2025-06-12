// components/ui/Tooltip.jsx
import React from "react";

export function Tooltip({ content, children }) {
  return (
    <div className="group relative inline-block">
      {children}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition pointer-events-none bg-black text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
        {content}
      </div>
    </div>
  );
}
