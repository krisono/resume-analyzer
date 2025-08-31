import React from "react";

export function MissingList({ items }: { items: string[] }) {
  if (!items?.length) return null;
  return (
    <div style={{ marginTop: "1rem" }}>
      <strong>Top Missing Keywords</strong>
      <ul>
        {items.slice(0, 20).map((kw, i) => (
          <li key={i}>{kw}</li>
        ))}
      </ul>
    </div>
  );
}
