import React from "react";

export function NavButton({ icon: Icon, label, active, onClick }) {
  return (
    <button className={`navButton ${active ? "active" : ""}`} onClick={onClick}>
      <Icon size={18} />
      <span>{label}</span>
    </button>
  );
}

export function MetricCard({ label, value, icon: Icon }) {
  return (
    <div className="metricCard">
      <Icon size={20} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function TagRow({ tags = [] }) {
  return (
    <div className="tagRow">
      {tags.filter(Boolean).slice(0, 5).map((tag) => <span key={tag}>{tag}</span>)}
    </div>
  );
}

export function Fact({ label, value }) {
  return (
    <div className="fact">
      <span>{label}</span>
      <strong>{value || "Not set"}</strong>
    </div>
  );
}

export function ScoreRing({ score }) {
  return (
    <div className="scoreRing" style={{ "--score": `${score * 3.6}deg` }}>
      <strong>{score}</strong>
      <span>fit</span>
    </div>
  );
}

export function ScoreBreakdown({ breakdown }) {
  return (
    <div className="breakdown">
      {Object.entries(breakdown || {}).map(([key, value]) => (
        <div className="barRow" key={key}>
          <span>{labelize(key)}</span>
          <div className="barTrack"><div style={{ width: `${Math.min(100, value * 4)}%` }} /></div>
          <b>{value}</b>
        </div>
      ))}
    </div>
  );
}

export function EmptyState({ children }) {
  return <div className="emptyState">{children}</div>;
}

export function labelize(value) {
  return String(value).replaceAll("_", " ");
}
