import React from "react";
import { BarChart3, Building2, Handshake, Network, Sparkles, UserRoundCheck } from "lucide-react";
import { Fact, MetricCard } from "../components/ui.jsx";

export function Dashboard({ dashboard, cohorts, programs, partners, evaluation }) {
  const entities = dashboard?.entities || {};
  const relationships = dashboard?.relationships || {};
  const stats = [
    { label: "Startups", value: entities.startups || 0, icon: Building2 },
    { label: "Mentors", value: entities.mentors || 0, icon: UserRoundCheck },
    { label: "Partners", value: entities.partners || partners.length, icon: Network },
    { label: "Recommendations", value: dashboard?.recommendations || 0, icon: Sparkles },
    { label: "Approved", value: relationships.approved || 0, icon: Handshake },
    { label: "Review Needed", value: relationships.review_needed || 0, icon: BarChart3 }
  ];

  return (
    <div className="gridStack">
      <section className="statsGrid">
        {stats.map((item) => <MetricCard key={item.label} {...item} />)}
      </section>
      <section className="panel">
        <div className="panelHeader">
          <h3>Problem Fit</h3>
          <span className="statusBadge">relationship-first</span>
        </div>
        <div className="twoColumn">
          <Fact label="Program" value={programs[0]?.name || cohorts[0]?.program} />
          <Fact label="Manual coordination" value={dashboard?.problem_fit?.manual_coordination_reduced} />
          <Fact label="Reusable data" value={dashboard?.problem_fit?.reuse_signal} />
          <Fact label="Benchmark accuracy" value={`${Math.round((evaluation?.top_1_accuracy || 0) * 100)}% top-1`} />
        </div>
      </section>
    </div>
  );
}
