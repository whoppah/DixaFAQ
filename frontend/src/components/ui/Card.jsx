//frotend/src/components/ui/Card.jsx
import React from "react";
import { cn } from "@/lib/utils";

export function Card({ className, children, ...props }) {
  return (
    <div
      className={cn(
        "bg-white border border-gray-200 shadow-sm rounded-xl overflow-hidden transition-all hover:shadow-md",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className, children }) {
  return (
    <div className={cn("px-6 pt-5 pb-3 border-b border-gray-100", className)}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className }) {
  return (
    <h3
      className={cn(
        "text-lg font-semibold tracking-tight text-gray-900",
        className
      )}
    >
      {children}
    </h3>
  );
}

export function CardDescription({ children, className }) {
  return (
    <p
      className={cn("text-sm text-gray-500 mt-1 leading-relaxed", className)}
    >
      {children}
    </p>
  );
}

export function CardContent({ children, className }) {
  return (
    <div className={cn("px-6 py-4 space-y-4", className)}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className }) {
  return (
    <div className={cn("px-6 pb-4 pt-2 border-t border-gray-100", className)}>
      {children}
    </div>
  );
}
