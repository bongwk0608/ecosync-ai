import React from "react";
import { Sparkles } from "lucide-react";
import { RecommendationCard } from "../components/RecommendationCard.jsx";
import { EmptyState, TagRow } from "../components/ui.jsx";

export function MatchingWorkspace({ startups, selectedStartup, selectedStartupId, setSelectedStartupId, runMatching, running, matchRun, setRelationship }) {
  return (
    <div className="matchingLayout">
      <section className="panel controlPanel">
        <div className="panelHeader">
          <h3>Run Ecosystem Matching</h3>
          <span className="statusBadge">Gemini-ready</span>
        </div>
        <label className="fieldLabel" htmlFor="startup-select">Startup</label>
        <select id="startup-select" value={selectedStartupId} onChange={(event) => setSelectedStartupId(event.target.value)}>
          {startups.map((startup) => (
            <option key={startup.id} value={startup.id}>{startup.name}</option>
          ))}
        </select>
        {selectedStartup && (
          <div className="profileBox">
            <h4>{selectedStartup.name}</h4>
            <p>{selectedStartup.domain} | {selectedStartup.stage} | {selectedStartup.location}</p>
            <TagRow tags={selectedStartup.requested_support} />
          </div>
        )}
        <button className="primaryButton" onClick={runMatching} disabled={running}>
          <Sparkles size={18} />
          {running ? "Running..." : "Generate Relationships"}
        </button>
      </section>

      <section className="resultsColumn">
        {!matchRun ? (
          <EmptyState>Select a cohort startup and generate ranked mentor relationships with risks, gaps, and next actions.</EmptyState>
        ) : (
          matchRun.recommendations.map((recommendation, index) => (
            <RecommendationCard
              key={recommendation.id}
              recommendation={recommendation}
              rank={index + 1}
              setRelationship={setRelationship}
            />
          ))
        )}
      </section>
    </div>
  );
}
