import React, { useState } from "react";
import { Plus, Search } from "lucide-react";
import { TagRow } from "../components/ui.jsx";

export function Directory({ title, items, kind, onCreate, canAdd = false }) {
  const [query, setQuery] = useState("");
  const [showForm, setShowForm] = useState(false);
  const filtered = items.filter((item) => JSON.stringify(item).toLowerCase().includes(query.toLowerCase()));
  return (
    <section className="panel">
      <div className="panelHeader">
        <h3>{title}</h3>
        <div className="directoryTools">
          {canAdd && <button className="ghostButton" onClick={() => setShowForm((current) => !current)}><Plus size={16} /> Add</button>}
          <div className="searchBox"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search" /></div>
        </div>
      </div>
      {showForm && <DatasetForm kind={kind} onCreate={onCreate} onDone={() => setShowForm(false)} />}
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

function DatasetForm({ kind, onCreate, onDone }) {
  const [form, setForm] = useState(initialForm(kind));
  if (!["startup", "mentor"].includes(kind)) return null;

  async function submit(event) {
    event.preventDefault();
    await onCreate(normalizePayload(kind, form));
    setForm(initialForm(kind));
    onDone();
  }

  return (
    <form className="datasetForm" onSubmit={submit}>
      {Object.keys(form).map((field) => (
        <label key={field}>
          {field.replaceAll("_", " ")}
          <input required value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} />
        </label>
      ))}
      <button className="primaryButton"><Plus size={16} />Add {kind}</button>
    </form>
  );
}

function initialForm(kind) {
  if (kind === "startup") {
    return {
      name: "",
      domain: "",
      location: "",
      stage: "",
      pain_points: "",
      goals: "",
      requested_support: "",
      founder_notes: ""
    };
  }
  return {
    name: "",
    expertise: "",
    industries: "",
    location: "",
    languages: "",
    availability: "",
    past_roles: "",
    mentoring_style: "",
    preferred_stage: ""
  };
}

function normalizePayload(kind, form) {
  const listFields = kind === "startup"
    ? ["pain_points", "goals", "requested_support"]
    : ["expertise", "industries", "languages", "past_roles", "preferred_stage"];
  return Object.fromEntries(
    Object.entries(form).map(([key, value]) => [
      key,
      listFields.includes(key) ? value.split(",").map((item) => item.trim()).filter(Boolean) : value
    ])
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
