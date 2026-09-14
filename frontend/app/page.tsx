"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  CheckCircle2,
  FileSearch,
  FileStack,
  KeyRound,
  Menu,
  Network,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  Workflow,
  X,
  Zap,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import ThemeToggle from "@/components/theme/ThemeToggle";
import Reveal from "@/components/ui/Reveal";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

const REPO_URL = "https://github.com/animesh8787/AI-powered-Industrial-Knowledge-Intelligence-Platform";

function GithubMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56 0-.28-.01-1.02-.02-2-3.2.7-3.87-1.54-3.87-1.54-.53-1.33-1.29-1.69-1.29-1.69-1.05-.72.08-.7.08-.7 1.16.08 1.78 1.19 1.78 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.18 1.18a11 11 0 0 1 5.8 0c2.2-1.49 3.17-1.18 3.17-1.18.64 1.59.24 2.76.12 3.05.74.8 1.19 1.83 1.19 3.09 0 4.42-2.69 5.4-5.25 5.68.41.36.78 1.06.78 2.14 0 1.55-.01 2.79-.01 3.17 0 .31.21.67.8.56A10.52 10.52 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
    </svg>
  );
}

const STACK = ["Next.js", "FastAPI", "LangGraph", "Groq", "ChromaDB", "PostgreSQL"];

const FEATURES = [
  {
    icon: FileSearch,
    title: "Cited, source-grounded answers",
    body: "Every answer is generated from retrieved document chunks and comes back with a citation pointing to the exact filename and page it was pulled from.",
  },
  {
    icon: Network,
    title: "Entities and relationships, not just text",
    body: "Equipment, failures and procedures are extracted automatically and linked into a knowledge graph you can query and explore.",
  },
  {
    icon: FileStack,
    title: "Multi-format ingestion",
    body: "PDFs, P&IDs, spreadsheets, emails and forms are OCR'd, parsed and chunked through one pipeline — no manual reformatting.",
  },
  {
    icon: Zap,
    title: "Resilient two-tier inference",
    body: "Response generation runs primarily through the Groq API and automatically falls back to a local Ollama model, so a provider outage never stalls an answer.",
  },
  {
    icon: ShieldCheck,
    title: "Built-in compliance agent",
    body: "An agent scans ingested documents against policy and regulatory requirements and surfaces gaps directly, with evidence.",
  },
  {
    icon: KeyRound,
    title: "Versioned, JWT-secured APIs",
    body: "Every capability — auth, documents, search, chat, conversations, the graph — is exposed through a typed, versioned REST API.",
  },
];

const STEPS = [
  {
    icon: UploadCloud,
    title: "Upload",
    body: "Drop in manuals, inspection reports, P&IDs, spreadsheets and emails. OCR, parsing and chunking run automatically.",
  },
  {
    icon: Sparkles,
    title: "Ask",
    body: "Ask a question in plain language. The system retrieves the relevant chunks and reasons over them, not just keyword matches.",
  },
  {
    icon: CheckCircle2,
    title: "Verify",
    body: "Every answer ships with citations back to the source page, so you can check it yourself before you act on it.",
  },
];

const GRAPH_NODES = [
  { id: "pump", label: "Pump P-101A", x: 50, y: 18 },
  { id: "manual", label: "Equipment Manual", x: 12, y: 55 },
  { id: "inspection", label: "Inspection 2025", x: 50, y: 78 },
  { id: "compressor", label: "Compressor C-200", x: 88, y: 55 },
];
const GRAPH_EDGES: [string, string][] = [
  ["pump", "manual"],
  ["pump", "inspection"],
  ["pump", "compressor"],
];

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/documents");
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen bg-bg">
      <header
        className={[
          "sticky top-0 z-40 transition-colors duration-200",
          scrolled ? "border-b border-border-subtle bg-bg/85 backdrop-blur-md" : "border-b border-transparent",
        ].join(" ")}
      >
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-4 px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-accent text-surface">
              <Network className="h-4 w-4" />
            </span>
            <span className="font-display text-[16px] font-medium tracking-tight text-text-primary">
              OpsBrain
            </span>
          </Link>

          <nav className="ml-6 hidden items-center gap-6 md:flex" aria-label="Page sections">
            <a href="#features" className="text-[14px] font-medium text-text-secondary transition-colors hover:text-text-primary">
              Features
            </a>
            <a href="#how-it-works" className="text-[14px] font-medium text-text-secondary transition-colors hover:text-text-primary">
              How it works
            </a>
            <a
              href={REPO_URL}
              target="_blank"
              rel="noreferrer noopener"
              className="flex items-center gap-1.5 text-[14px] font-medium text-text-secondary transition-colors hover:text-text-primary"
            >
              <GithubMark className="h-3.5 w-3.5" />
              GitHub
            </a>
          </nav>

          <div className="ml-auto hidden items-center gap-3 md:flex">
            <ThemeToggle />
            <Button href="/login" variant="secondary">
              Log in
            </Button>
          </div>

          <button
            type="button"
            className="ml-auto flex h-9 w-9 items-center justify-center rounded-md text-text-secondary hover:bg-accent-subtle md:hidden"
            onClick={() => setMobileOpen((v) => !v)}
            aria-expanded={mobileOpen}
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {mobileOpen && (
          <div className="border-t border-border-subtle bg-bg px-6 py-4 md:hidden">
            <nav className="flex flex-col gap-1" aria-label="Page sections">
              <a
                href="#features"
                onClick={() => setMobileOpen(false)}
                className="rounded-md px-3 py-2.5 text-[14px] font-medium text-text-secondary hover:bg-accent-subtle hover:text-text-primary"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                onClick={() => setMobileOpen(false)}
                className="rounded-md px-3 py-2.5 text-[14px] font-medium text-text-secondary hover:bg-accent-subtle hover:text-text-primary"
              >
                How it works
              </a>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer noopener"
                className="flex items-center gap-1.5 rounded-md px-3 py-2.5 text-[14px] font-medium text-text-secondary hover:bg-accent-subtle hover:text-text-primary"
              >
                <GithubMark className="h-3.5 w-3.5" />
                GitHub
              </a>
            </nav>
            <div className="mt-3 flex items-center justify-between border-t border-border-subtle pt-3">
              <ThemeToggle />
              <Button href="/login" variant="secondary">
                Log in
              </Button>
            </div>
          </div>
        )}
      </header>

      <main id="main-content">
        <Hero />
        <StackStrip />
        <Features />
        <SpotlightExplainability />
        <SpotlightKnowledgeGraph />
        <HowItWorks />
        <FinalCta />
      </main>

      <Footer />
    </div>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 left-1/2 h-[520px] w-[900px] -translate-x-1/2 rounded-full bg-accent-subtle opacity-70 blur-3xl"
      />
      <div className="relative mx-auto max-w-6xl px-6 pb-20 pt-16 sm:pt-24">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <Reveal>
            <Badge variant="accent">
              <Sparkles className="h-3 w-3" />
              Retrieval-Augmented Industrial Intelligence
            </Badge>
            <h1 className="font-display mt-6 text-[40px] leading-[48px] font-medium tracking-tight text-text-primary sm:text-[52px] sm:leading-[60px]">
              Every answer, traced back to <span className="text-accent">the exact page it came from.</span>
            </h1>
            <p className="mt-6 max-w-xl text-[16px] leading-[26px] text-text-secondary">
              OpsBrain turns manuals, inspection reports, P&amp;IDs, spreadsheets and maintenance
              logs into a searchable knowledge base. Ask a question in plain language and get a
              cited, source-grounded answer in seconds — not a guess.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Button href="/login" size="lg">
                Sign in to the console
                <ArrowRight className="h-4 w-4" />
              </Button>
              <Button href="#how-it-works" variant="secondary" size="lg">
                See how it works
              </Button>
            </div>
          </Reveal>

          <Reveal delay={150}>
            <HeroVisual />
          </Reveal>
        </div>
      </div>
    </section>
  );
}

function HeroVisual() {
  return (
    <div className="relative mx-auto max-w-md lg:max-w-none">
      <div className="rounded-xl border border-border-subtle bg-surface p-5 shadow-raised">
        <div className="mb-4 flex items-center gap-2 border-b border-border-subtle pb-3">
          <span className="h-2 w-2 rounded-full bg-success" />
          <p className="text-[12px] font-medium text-text-secondary">OpsBrain · Chat</p>
        </div>
        <p className="text-[13px] font-medium text-text-tertiary">
          What maintenance procedure should be followed for Pump P-101A?
        </p>
        <p className="mt-3 text-[14px] leading-[22px] text-text-primary">
          Perform a vibration check and inspect the mechanical seal every 90 days
          <CiteChip index={1} /> following a lockout-tagout procedure. The last inspection flagged
          elevated bearing temperature
          <CiteChip index={2} />, so check bearing lubrication first.
        </p>
        <div className="mt-4 flex flex-col gap-2 rounded-md border border-border-subtle bg-bg p-3">
          <SourceRow index={1} filename="P-101A_Manual.pdf" page={14} score={0.86} />
          <SourceRow index={2} filename="Inspection_2025.pdf" page={3} score={0.74} />
        </div>
      </div>

      <div className="absolute -bottom-8 -right-4 w-56 rotate-2 rounded-xl border border-border-subtle bg-surface p-3.5 shadow-raised sm:-right-10 sm:w-60">
        <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-text-tertiary">
          Linked in the knowledge graph
        </p>
        <div className="flex items-center gap-2 text-[12px] text-text-secondary">
          <Network className="h-3.5 w-3.5 text-accent" />
          Pump P-101A → Compressor C-200
        </div>
        <div className="mt-1.5 flex items-center gap-2 text-[12px] text-text-secondary">
          <Workflow className="h-3.5 w-3.5 text-accent" />
          3 related documents
        </div>
      </div>
    </div>
  );
}

function CiteChip({ index }: { index: number }) {
  return (
    <span className="mx-0.5 inline-flex items-center rounded-sm bg-accent-subtle px-1.5 py-0.5 font-mono text-[11px] font-medium text-accent">
      [{index}]
    </span>
  );
}

function SourceRow({
  index,
  filename,
  page,
  score,
}: {
  index: number;
  filename: string;
  page: number;
  score: number;
}) {
  return (
    <div className="flex items-center gap-2 text-[12px]">
      <span className="font-mono text-accent">[{index}]</span>
      <span className="truncate text-text-secondary">
        {filename} · p.{page}
      </span>
      <span className="ml-auto flex items-center gap-1 text-text-tertiary">
        <span className="h-1.5 w-1.5 rounded-full bg-success" />
        {Math.round(score * 100)}%
      </span>
    </div>
  );
}

function StackStrip() {
  return (
    <section className="border-y border-border-subtle bg-surface py-8">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal>
          <p className="mb-4 text-center text-[11px] font-semibold uppercase tracking-wide text-text-tertiary">
            Built on
          </p>
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
            {STACK.map((name) => (
              <span key={name} className="text-[14px] font-medium text-text-secondary">
                {name}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}

function Features() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-6 py-20 sm:py-28">
      <Reveal className="mx-auto max-w-2xl text-center">
        <h2 className="font-display text-[32px] font-medium tracking-tight text-text-primary sm:text-[38px]">
          Everything a knowledge base should have from the start
        </h2>
        <p className="mt-4 text-[16px] leading-[26px] text-text-secondary">
          Ingestion, retrieval, reasoning and citation mapping run as one pipeline — not
          bolted-on afterthoughts.
        </p>
      </Reveal>

      <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map((feature, index) => (
          <Reveal key={feature.title} delay={index * 60}>
            <div className="h-full rounded-xl border border-border-subtle bg-surface p-6 transition-colors hover:border-accent/40">
              <span className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-accent-subtle text-accent">
                <feature.icon className="h-5 w-5" />
              </span>
              <h3 className="text-[15px] font-semibold text-text-primary">{feature.title}</h3>
              <p className="mt-2 text-[14px] leading-[22px] text-text-secondary">{feature.body}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

function SpotlightExplainability() {
  const matched = ["vibration check", "seal inspection", "lockout-tagout"];

  return (
    <section className="border-t border-border-subtle bg-surface py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <Reveal>
            <Badge variant="accent">Explainability</Badge>
            <h2 className="font-display mt-4 text-[30px] font-medium tracking-tight text-text-primary sm:text-[36px]">
              See exactly where the answer came from
            </h2>
            <p className="mt-4 text-[16px] leading-[26px] text-text-secondary">
              Every generated answer is mapped back to the exact chunk that produced it — filename,
              page number, and a relevance score. No black box, and nothing to take on faith.
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "Click any citation to open the source document at the exact page",
                "A relevance score ships with every source, not just the answer",
                "Entity and relationship extraction runs on the same grounded context",
              ].map((text) => (
                <li key={text} className="flex items-start gap-2.5 text-[14px] text-text-primary">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                  <span>{text}</span>
                </li>
              ))}
            </ul>
          </Reveal>

          <Reveal delay={150}>
            <div className="rounded-xl border border-border-subtle bg-bg p-6 shadow-raised">
              <p className="mb-4 rounded-md border border-border-subtle bg-surface px-3 py-2 text-[13px] text-text-secondary">
                Strong match. Retrieved from 2 sources, 86% and 74% relevance.
              </p>
              <div className="space-y-2.5">
                <SourceRow index={1} filename="P-101A_Manual.pdf" page={14} score={0.86} />
                <SourceRow index={2} filename="Inspection_2025.pdf" page={3} score={0.74} />
              </div>
              <div className="mt-5">
                <p className="mb-1.5 text-[12px] font-semibold text-success">Grounded on</p>
                <div className="flex flex-wrap gap-1.5">
                  {matched.map((term) => (
                    <span
                      key={term}
                      className="inline-flex items-center gap-1 rounded-md border border-success/30 bg-success/10 px-2 py-0.5 text-[12px] font-medium text-success"
                    >
                      <CheckCircle2 className="h-3 w-3" />
                      {term}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

function SpotlightKnowledgeGraph() {
  return (
    <section className="py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <Reveal className="order-2 lg:order-1">
            <KnowledgeGraphMockup />
          </Reveal>

          <Reveal delay={150} className="order-1 lg:order-2">
            <Badge variant="accent">Knowledge graph</Badge>
            <h2 className="font-display mt-4 text-[30px] font-medium tracking-tight text-text-primary sm:text-[36px]">
              Equipment, failures and procedures — linked
            </h2>
            <p className="mt-4 text-[16px] leading-[26px] text-text-secondary">
              Entity and relationship extraction runs on every ingested document, connecting
              equipment to the manuals, inspection reports and incidents that mention it — so
              root-cause analysis stops meaning &ldquo;read everything and hope.&rdquo;
            </p>
            <ul className="mt-6 space-y-3">
              {[
                "Extraction runs automatically during ingestion, no manual tagging",
                "Traverse from one piece of equipment to every document that references it",
                "The same graph backs both search and conversational answers",
              ].map((text) => (
                <li key={text} className="flex items-start gap-2.5 text-[14px] text-text-primary">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                  <span>{text}</span>
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

function KnowledgeGraphMockup() {
  return (
    <div className="rounded-xl border border-border-subtle bg-surface p-6 shadow-raised">
      <svg viewBox="0 0 100 100" className="h-64 w-full" aria-hidden="true">
        {GRAPH_EDGES.map(([from, to]) => {
          const a = GRAPH_NODES.find((n) => n.id === from)!;
          const b = GRAPH_NODES.find((n) => n.id === to)!;
          return (
            <line
              key={`${from}-${to}`}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke="var(--color-border-default)"
              strokeWidth={0.6}
            />
          );
        })}
        {GRAPH_NODES.map((node) => (
          <circle
            key={node.id}
            cx={node.x}
            cy={node.y}
            r={node.id === "pump" ? 4 : 3}
            fill={node.id === "pump" ? "var(--color-accent)" : "var(--color-accent-subtle)"}
            stroke="var(--color-accent)"
            strokeWidth={0.6}
          />
        ))}
      </svg>
      <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1.5">
        {GRAPH_NODES.map((node) => (
          <div key={node.id} className="flex items-center gap-1.5 text-[12px] text-text-secondary">
            <span
              className={[
                "h-1.5 w-1.5 shrink-0 rounded-full",
                node.id === "pump" ? "bg-accent" : "bg-accent-subtle border border-accent/40",
              ].join(" ")}
            />
            {node.label}
          </div>
        ))}
      </div>
    </div>
  );
}

function HowItWorks() {
  return (
    <section id="how-it-works" className="border-t border-border-subtle bg-surface py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-[32px] font-medium tracking-tight text-text-primary sm:text-[38px]">
            From document pile to verified answer
          </h2>
          <p className="mt-4 text-[16px] text-text-secondary">Three steps, one pipeline.</p>
        </Reveal>

        <div className="relative mt-14 grid gap-8 sm:grid-cols-3">
          <div
            aria-hidden
            className="pointer-events-none absolute left-0 right-0 top-8 hidden h-px bg-border-subtle sm:block"
          />
          {STEPS.map((step, index) => (
            <Reveal key={step.title} delay={index * 100} className="relative text-center">
              <div className="relative mx-auto flex h-16 w-16 items-center justify-center rounded-full border border-border-subtle bg-bg shadow-raised">
                <step.icon className="h-6 w-6 text-accent" />
                <span className="absolute -right-1 -top-1 flex h-6 w-6 items-center justify-center rounded-full bg-accent text-[11px] font-bold text-surface">
                  {index + 1}
                </span>
              </div>
              <h3 className="mt-4 text-[15px] font-semibold text-text-primary">{step.title}</h3>
              <p className="mx-auto mt-2 max-w-[26ch] text-[14px] leading-[22px] text-text-secondary">
                {step.body}
              </p>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCta() {
  return (
    <section className="relative overflow-hidden py-20 sm:py-28">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 h-full bg-accent-subtle"
      />
      <Reveal className="relative mx-auto max-w-2xl px-6 text-center">
        <h2 className="font-display text-[32px] font-medium tracking-tight text-text-primary sm:text-[38px]">
          See it resolve a real question
        </h2>
        <p className="mt-4 text-[16px] leading-[26px] text-text-secondary">
          Sign in to the console to walk through document ingestion, a cited answer, and the
          knowledge graph behind it, end to end.
        </p>
        <div className="mt-8">
          <Button href="/login" size="lg">
            Sign in to the console
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </Reveal>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-border-subtle py-12">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <Link href="/" className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-md bg-accent text-surface">
                <Network className="h-3.5 w-3.5" />
              </span>
              <span className="font-display text-[14px] font-medium text-text-primary">OpsBrain</span>
            </Link>
            <p className="mt-3 max-w-xs text-[13px] leading-[20px] text-text-secondary">
              Unified Asset &amp; Operations Brain — cited, source-grounded answers over your
              industrial documents.
            </p>
          </div>

          <FooterColumn
            title="Product"
            links={[
              { label: "Features", href: "#features" },
              { label: "How it works", href: "#how-it-works" },
              { label: "Log in", to: "/login" },
            ]}
          />

          <FooterColumn
            title="Resources"
            links={[{ label: "GitHub repository", href: REPO_URL, external: true }]}
          />

          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-text-tertiary">
              Open source
            </p>
            <p className="mt-3 text-[13px] leading-[20px] text-text-secondary">
              MIT licensed. Built for the ET AI Hackathon 2026, Problem Statement 8.
            </p>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-4 border-t border-border-subtle pt-6 sm:flex-row">
          <p className="text-[12px] text-text-tertiary">
            © {new Date().getFullYear()} OpsBrain.
          </p>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer noopener"
            className="flex items-center gap-1.5 text-[12px] font-medium text-text-tertiary hover:text-text-primary"
          >
            <GithubMark className="h-3.5 w-3.5" />
            Star on GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: { label: string; href?: string; to?: string; external?: boolean }[];
}) {
  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-wide text-text-tertiary">{title}</p>
      <ul className="mt-3 space-y-2.5">
        {links.map((link) => (
          <li key={link.label}>
            {link.to ? (
              <Link href={link.to} className="text-[13px] text-text-secondary hover:text-text-primary">
                {link.label}
              </Link>
            ) : (
              <a
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noreferrer noopener" : undefined}
                className="text-[13px] text-text-secondary hover:text-text-primary"
              >
                {link.label}
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
