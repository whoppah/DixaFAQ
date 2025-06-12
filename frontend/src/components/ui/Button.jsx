//frontend/src/components/ui/Button.jsx
import React from "react";
import { cn } from "@/lib/utils";

export function Button({ children, variant = "primary", className = "", ...props }) {
  const base = "inline-flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition";

  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200",
    outline: "border border-gray-300 text-gray-700 hover:bg-gray-50",
    destructive: "bg-red-600 text-white hover:bg-red-700",
  };

  return (
    <button className={cn(base, variants[variant], className)} {...props}>
      {children}
    </button>
  );
}
