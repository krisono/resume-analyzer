import React from "react";

export function SectionAlignment({
  items,
}: {
  items: Array<{ section: string; similarity: number }>;
}) {
  if (!items?.length) return null;
  return (
    <div style={{ marginTop: "1rem" }}>
      <strong>Section Alignment</strong>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left" }}>Section</th>
            <th style={{ textAlign: "left" }}>Similarity %</th>
          </tr>
        </thead>
        <tbody>
          {items.map((s, i) => (
            <tr key={i}>
              <td>{s.section}</td>
              <td>{s.similarity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
