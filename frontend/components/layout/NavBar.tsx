"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileStack, MessageSquare, Network } from "lucide-react";
import Container from "./Container";
import ThemeToggle from "@/components/theme/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";

type NavLink = { label: string; href: string; icon: React.ComponentType<{ className?: string }> };

const navLinks: NavLink[] = [
  { label: "Documents", href: "/documents", icon: FileStack },
  { label: "Chat", href: "/chat", icon: MessageSquare },
];

function isActive(href: string, pathname: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function NavBar() {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 h-14 bg-surface border-b border-border-subtle">
      <Container>
        <div className="flex h-full items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-md bg-accent text-surface">
              <Network className="h-3.5 w-3.5" />
            </span>
            <span className="font-display text-[15px] font-medium tracking-tight text-text-primary">
              OpsBrain
            </span>
          </Link>
          <div className="flex items-center gap-3 sm:gap-6">
            {isAuthenticated && (
              <nav className="flex items-center gap-3 sm:gap-6">
                {navLinks.map((link) => {
                  const active = isActive(link.href, pathname);
                  return (
                    <Link
                      key={link.href}
                      href={link.href}
                      className={[
                        "flex items-center gap-1.5 text-[14px] font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm",
                        active
                          ? "text-text-primary border-b-2 border-accent pb-[2px]"
                          : "text-text-secondary hover:text-text-primary",
                      ].join(" ")}
                    >
                      <link.icon className="h-3.5 w-3.5" />
                      <span className="hidden sm:inline">{link.label}</span>
                    </Link>
                  );
                })}
              </nav>
            )}
            <ThemeToggle />
            {isAuthenticated ? (
              <button
                type="button"
                onClick={logout}
                className="text-[14px] font-medium text-text-secondary hover:text-text-primary transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm"
              >
                Log out
              </button>
            ) : (
              <Link
                href="/login"
                className="text-[14px] font-medium text-text-secondary hover:text-text-primary transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-sm"
              >
                Log in
              </Link>
            )}
          </div>
        </div>
      </Container>
    </header>
  );
}
