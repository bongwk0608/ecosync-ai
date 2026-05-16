import React, { useState } from "react";
import { Search } from "lucide-react";
import { TagRow } from "../components/ui.jsx";

export function Directory({ title, items, kind }) {
  const [query, setQuery] = useState("");
  const filtered = items.filter((item) => JSON.stringify(item).toLowerCase().includes(query.toLowerCase()));
  return (
    <section className="panel">
      <div className="panelHeader">
        <h3>{title}</h3>
        <div className="searchBox"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search" /></div>
      </div>
      <div className="tableList">
        {filtered.map((item) => (
          <div className="tableRow" key={item.id}>
            <div>
              <strong>{item.name}</strong>
              <p>{subtitle(item, kind)}</p>
            </div>
            <span>{item.location || item.type || item.owner}</span>
            <TagRow tags={tags(item, kind)} />
          </div>
        ))}
      </div>
    </section>
  );
}

function subtitle(item, kind) {
  if (kind === "startup") return `${item.domain} | ${item.stage}`;
  if (kind === "mentor") return item.expertise?.slice(0, 3).join(", ");
  if (kind === "partner") return item.type;
  return item.owner;
}

function tags(item, kind) {
  if (kind === "startup") return item.requested_support;
  if (kind === "mentor") return item.industries;
  if (kind === "partner") return item.capabilities;
  return item.relationship_goals;
}
