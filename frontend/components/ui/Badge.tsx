import React from "react";
import { cn } from "@/lib/cn";

type Variant = "neutral" | "accent" | "success" | "warning";

const variants: Record<Variant, string> = {
  neutral: "border-border-default bg-surface text-text-secondary",
  accent: "border-accent/30 bg-accent-subtle text-accent",
  success: "border-success/30 bg-success/10 text-success",
  warning: "border-warning/30 bg-warning/10 text-warning",
};

export default function Badge({
  children,
  variant = "neutral",
  className,
}: {
  children: React.ReactNode;
  variant?: Variant;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[12px] font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
