//frotend/src/components/ui/Card.jsx
import React from "react";
import { cn } from "@/lib/utils"; 

export function Card({ className, children, ...props }) {
  return (
    <div
      className={cn("bg-white border shadow-sm rounded-lg p-6", className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, description }) {
  return (
    <div className="mb-4">
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      {description && <p className="text-sm text-muted-foreground">{description}</p>}
    </div>
  );
}

export function CardContent({ children }) {
  return <div className="space-y-4">{children}</div>;
}
