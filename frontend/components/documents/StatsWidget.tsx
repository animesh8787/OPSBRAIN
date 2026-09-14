"use client";

import React from "react";
import { useDocuments } from "@/contexts/DocumentsContext";
import { useTheme } from "@/components/theme/ThemeProvider";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const COLORS_LIGHT = {
  Ready: "#16A34A",
  Processing: "#D97706",
  Failed: "#DC2626",
};

const COLORS_DARK = {
  Ready: "#22C55E",
  Processing: "#F59E0B",
  Failed: "#EF4444",
};

const HEX_LIGHT = { tick: "#71717A", surface: "#FFFFFF", borderSubtle: "#E7E5E2", textPrimary: "#18181B" };
const HEX_DARK = { tick: "#A1A1AA", surface: "#18181B", borderSubtle: "#27272A", textPrimary: "#FAFAFA" };

export default function StatsWidget() {
  const { documents } = useDocuments();
  const { theme } = useTheme();
  const COLORS = theme === "dark" ? COLORS_DARK : COLORS_LIGHT;
  const HEX = theme === "dark" ? HEX_DARK : HEX_LIGHT;

  const total = documents.length;
  if (total === 0) return null;

  const ready = documents.filter((d) => d.status === "ready").length;
  const processing = documents.filter(
    (d) => d.status === "uploading" || d.status === "processing"
  ).length;
  const failed = documents.filter((d) => d.status === "error").length;

  const data = [
    { name: "Ready", count: ready },
    { name: "Processing", count: processing },
    { name: "Failed", count: failed },
  ];

  return (
    <div className="mb-6">
      <ResponsiveContainer width="100%" height={120}>
        <BarChart layout="vertical" data={data} margin={{ top: 0, right: 16, bottom: 0, left: 0 }}>
          <XAxis
            type="number"
            tick={{ fontSize: 12, fill: HEX.tick }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={70}
            tick={{ fontSize: 12, fill: HEX.tick }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: "transparent" }}
            contentStyle={{
              fontSize: 12,
              borderRadius: "6px",
              backgroundColor: HEX.surface,
              border: `1px solid ${HEX.borderSubtle}`,
              boxShadow: "0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)",
              color: HEX.textPrimary,
            }}
            labelStyle={{ color: HEX.textPrimary }}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={16}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
