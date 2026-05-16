import React from "react";
import { BarChart3 } from "lucide-react";
import { MetricCard } from "../components/ui.jsx";

export function EvaluationView({ evaluation }) {
  const cases = evaluation?.cases || [];
  return (
    <div className="gridStack">
      <section className="statsGrid">
        <MetricCard label="Benchmark Cases" value={evaluation?.benchmark_cases || 0} icon={BarChart3} />
        <MetricCard label="Top-1 Accuracy" value={`${Math.round((evaluation?.top_1_accuracy || 0) * 100)}%`} icon={BarChart3} />
        <MetricCard label="Avg Confidence" value={`${Math.round((evaluation?.average_confidence || 0) * 100)}%`} icon={BarChart3} />
        <MetricCard label="Fallback Cases" value={evaluation?.mode_counts?.["demo-fallback"] || 0} icon={BarChart3} />
      </section>
      <section className="panel">
        <div className="panelHeader">
          <h3>Model Performance Evidence</h3>
          <span className="statusBadge">prelim rubric</span>
        </div>
        <div className="tableList">
          {cases.map((item) => (
            <div className="tableRow" key={item.startup_id}>
              <div>
                <strong>{item.startup_name}</strong>
                <p>Expected {item.expected_top_mentor}; actual {item.actual_top_mentor}; score {item.actual_score}</p>
                <small>{item.reason}</small>
              </div>
              <span className={`statusBadge ${item.passed ? "approved" : "rejected"}`}>{item.passed ? "passed" : "check"}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
