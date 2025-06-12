//frontend/src/components/ui/Progress.jsx
import React from "react";
import { cn } from "@/lib/utils";

export function Progress({ value = 0, className }) {
  return (
    <div className={cn("w-full bg-gray-200 rounded h-2 overflow-hidden", className)}>
      <div
        className="bg-blue-600 h-full transition-all duration-500"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
