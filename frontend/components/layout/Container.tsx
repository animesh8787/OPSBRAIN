import React from "react";

interface ContainerProps {
  children: React.ReactNode;
}

export default function Container({ children }: ContainerProps) {
  return (
    <div className="mx-auto max-w-[1200px] px-4 sm:px-6 md:px-8">
      {children}
    </div>
  );
}
