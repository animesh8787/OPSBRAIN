"use client";

import React, { useState, FormEvent } from "react";
import ReactFlow, { Background, Controls, Node, Edge } from "reactflow";
import "reactflow/dist/style.css";
import { Network } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/components/theme/ThemeProvider";

const HEX_LIGHT = {
  accentSubtle: "#FEF3E2",
  accent: "#B45309",
  surface: "#FFFFFF",
  borderDefault: "#D8D6D2",
  textPrimary: "#18181B",
};

const HEX_DARK = {
  accentSubtle: "#2A1F0D",
  accent: "#D97706",
  surface: "#18181B",
  borderDefault: "#3F3F46",
  textPrimary: "#FAFAFA",
};

type Equipment = {
  tag_number: string;
  failures: string[];
  regulations: string[];
};

type Connection = {
  from_tag: string;
  to_tag: string;
};

type GraphData = {
  equipment: Equipment[];
  connections: Connection[];
};

function buildLabel(equipment: Equipment): string {
  let label = equipment.tag_number;
  if (equipment.failures.length > 0) {
    label += ` \u26A0${equipment.failures.length}`;
  }
  if (equipment.regulations.length > 0) {
    label += ` \u00A7${equipment.regulations.length}`;
  }
  return label;
}

function bfsDistance(
  start: string,
  connections: Connection[]
): Map<string, number> {
  const adj = new Map<string, string[]>();
  for (const c of connections) {
    if (!adj.has(c.from_tag)) adj.set(c.from_tag, []);
    if (!adj.has(c.to_tag)) adj.set(c.to_tag, []);
    adj.get(c.from_tag)!.push(c.to_tag);
    adj.get(c.to_tag)!.push(c.from_tag);
  }

  const dist = new Map<string, number>();
  const queue: string[] = [start];
  dist.set(start, 0);

  while (queue.length > 0) {
    const curr = queue.shift()!;
    const d = dist.get(curr)!;
    if (d >= 2) continue;
    for (const neighbor of adj.get(curr) ?? []) {
      if (!dist.has(neighbor)) {
        dist.set(neighbor, d + 1);
        queue.push(neighbor);
      }
    }
  }

  return dist;
}

export default function KnowledgeGraphView() {
  const { token } = useAuth();
  const { theme } = useTheme();
  const HEX = theme === "dark" ? HEX_DARK : HEX_LIGHT;
  const [tagInput, setTagInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [queriedTag, setQueriedTag] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = tagInput.trim().toUpperCase();
    if (!trimmed) return;

    setLoading(true);
    setError(null);
    setGraphData(null);

    try {
      const response = await fetch("http://localhost:8000/api/v1/graph/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ tag: trimmed, max_depth: 2 }),
      });

      if (!response.ok) {
        setError("Could not load the equipment graph. Please try again.");
        setLoading(false);
        return;
      }

      const data: GraphData = await response.json();
      setGraphData(data);
      setQueriedTag(trimmed);
      setLoading(false);
    } catch {
      setError("Could not load the equipment graph. Please try again.");
      setLoading(false);
    }
  }

  const nodes: Node[] = [];
  const edges: Edge[] = [];

  if (graphData && queriedTag) {
    const distMap = bfsDistance(queriedTag, graphData.connections);
    const ring0: Equipment[] = [];
    const ring1: Equipment[] = [];
    const ring2: Equipment[] = [];

    for (const eq of graphData.equipment) {
      const d = distMap.get(eq.tag_number);
      if (d === 0) {
        ring0.push(eq);
      } else if (d === 1) {
        ring1.push(eq);
      } else {
        ring2.push(eq);
      }
    }

    const addNode = (eq: Equipment, x: number, y: number) => {
      const isCenter = eq.tag_number === queriedTag;
      nodes.push({
        id: eq.tag_number,
        position: { x, y },
        data: { label: buildLabel(eq) },
        style: {
          background: isCenter ? HEX.accentSubtle : HEX.surface,
          border: isCenter
            ? `2px solid ${HEX.accent}`
            : `1px solid ${HEX.borderDefault}`,
          borderRadius: 6,
          fontSize: 12,
          padding: 8,
          color: HEX.textPrimary,
        },
      });
    };

    // Center
    if (ring0.length > 0) {
      addNode(ring0[0], 400, 300);
    }

    // Ring 1 (radius 150)
    if (ring1.length > 0) {
      ring1.forEach((eq, i) => {
        const angle = (2 * Math.PI * i) / ring1.length;
        const x = 400 + 150 * Math.cos(angle);
        const y = 300 + 150 * Math.sin(angle);
        addNode(eq, x, y);
      });
    }

    // Ring 2 (radius 300)
    if (ring2.length > 0) {
      ring2.forEach((eq, i) => {
        const angle = (2 * Math.PI * i) / ring2.length;
        const x = 400 + 300 * Math.cos(angle);
        const y = 300 + 300 * Math.sin(angle);
        addNode(eq, x, y);
      });
    }

    for (const c of graphData.connections) {
      edges.push({
        id: `${c.from_tag}-${c.to_tag}`,
        source: c.from_tag,
        target: c.to_tag,
        style: { stroke: HEX.borderDefault },
      });
    }
  }

  return (
    <section>
      <h2 className="flex items-center gap-2 text-[18px] leading-[26px] font-semibold text-text-primary mb-4">
        <Network className="h-4 w-4 text-accent" />
        Equipment Relationships
      </h2>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 mb-4">
        <input
          type="text"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
          placeholder="Enter equipment tag, e.g. P-101A"
          className="flex-1 rounded-md border border-border-default bg-surface px-3 py-2 text-[14px] text-text-primary placeholder:text-text-tertiary focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-accent px-4 py-2 text-[14px] font-medium text-surface hover:opacity-90 transition-opacity disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
        >
          Query
        </button>
      </form>

      {loading && (
        <p className="text-[15px] text-text-secondary">Loading graph...</p>
      )}

      {error && <p className="text-[15px] text-error">{error}</p>}

      {graphData && graphData.equipment.length === 0 && !loading && !error && (
        <p className="text-[15px] text-text-secondary">
          No connected equipment found for that tag.
        </p>
      )}

      {graphData && graphData.equipment.length > 0 && !loading && !error && (
        <div style={{ height: 400 }}>
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      )}
    </section>
  );
}
