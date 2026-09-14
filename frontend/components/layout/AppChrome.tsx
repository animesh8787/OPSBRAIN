"use client";

import React from "react";
import { usePathname } from "next/navigation";
import NavBar from "./NavBar";
import Container from "./Container";

/**
 * The landing page ("/") owns its own full-bleed nav and section layout,
 * so it renders without the app-wide NavBar/Container chrome used by every
 * other route.
 */
export default function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLanding = pathname === "/";

  if (isLanding) {
    // The landing page renders its own <main id="main-content"> along with
    // its own header/nav, so it isn't wrapped again here.
    return <>{children}</>;
  }

  return (
    <>
      <NavBar />
      <main id="main-content">
        <Container>{children}</Container>
      </main>
    </>
  );
}
