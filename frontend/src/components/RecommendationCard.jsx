import React from "react";
import { Check, Clock3, RefreshCw, X } from "lucide-react";
import { ScoreBreakdown, ScoreRing, TagRow } from "./ui.jsx";

export function RecommendationCard({ recommendation, rank, setRelationship, refreshRecommendation, refreshing }) {
  const mentor = recommendation.mentor;
  const ai = recommendation.ai || {};
  return (
    <article className="recommendationCard">
      <div className="recommendationTop">
        <div>
          <span className="rankBadge">#{rank}</span>
          <h3>{mentor.name}</h3>
          <p>{mentor.mentoring_style} | {mentor.availability}</p>
        </div>
        <ScoreRing score={recommendation.total_score} />
      </div>
      <TagRow tags={[recommendation.relationship_type, ai.confidence, ...mentor.expertise.slice(0, 3)]} />
      <p className="rationale">{ai.rationale}</p>
      <ScoreBreakdown breakdown={recommendation.score_breakdown} />
      <div className="insightGrid">
        <Insight title="Next action" value={ai.recommended_next_action} />
        <Insight title="Outcome metric" value={ai.outcome_metric} />
        <Insight title="Ethical guardrail" value={ai.ethical_consideration} />
      </div>
      {!!ai.risks?.length && <TagRow tags={ai.risks} />}
      <div className="cardFooter">
        <div className="aiFooter">
          <span className="aiMode">{ai.ai_mode} | {ai.model} | {cacheLabel(recommendation.ai_cache_status)}</span>
          <button
            className="refreshAiButton"
            onClick={() => refreshRecommendation(recommendation.id)}
            disabled={refreshing}
            title="Refresh AI explanation"
          >
            <RefreshCw size={15} />
          </button>
        </div>
        <div className="actionGroup">
          <button className="ghostButton" onClick={() => setRelationship(recommendation, "needs_review")} title="Mark for review">
            <Clock3 size={16} /> Review
          </button>
          <button className="dangerButton" onClick={() => setRelationship(recommendation, "rejected")} title="Reject relationship">
            <X size={16} /> Reject
          </button>
          <button className="successButton" onClick={() => setRelationship(recommendation, "approved")} title="Approve relationship">
            <Check size={16} /> Approve
          </button>
        </div>
      </div>
    </article>
  );
}

function cacheLabel(status) {
  return {
    hit: "cache hit",
    miss: "cache miss",
    refresh: "refreshed",
    disabled: "cache disabled"
  }[status] || "cache pending";
}

function Insight({ title, value }) {
  return (
    <div className="insight">
      <span>{title}</span>
      <strong>{value || "Not generated"}</strong>
    </div>
  );
}
