import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart3,
  Building2,
  Handshake,
  Network,
  RefreshCw,
  Sparkles,
  UserRoundCheck
} from "lucide-react";
import { createRelationship, getInitialData, refreshRecommendationAi, runMatch } from "./api/client.js";
import { NavButton } from "./components/ui.jsx";
import { Dashboard } from "./views/Dashboard.jsx";
import { Directory } from "./views/Directories.jsx";
import { EvaluationView } from "./views/Evaluation.jsx";
import { MatchingWorkspace } from "./views/Matching.jsx";
import { RelationshipBoard } from "./views/Relationships.jsx";
import "./styles.css";

function App() {
  const [cohorts, setCohorts] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [partners, setPartners] = useState([]);
  const [startups, setStartups] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [selectedStartupId, setSelectedStartupId] = useState("");
  const [matchRun, setMatchRun] = useState(null);
  const [activeView, setActiveView] = useState("dashboard");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [refreshingRecommendationIds, setRefreshingRecommendationIds] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    setLoading(true);
    setError("");
    try {
      const [
        cohortData,
        programData,
        partnerData,
        startupData,
        mentorData,
        relationshipData,
        dashboardData,
        evaluationData
      ] = await getInitialData();
      setCohorts(cohortData);
      setPrograms(programData);
      setPartners(partnerData);
      setStartups(startupData);
      setMentors(mentorData);
      setRelationships(relationshipData);
      setDashboard(dashboardData);
      setEvaluation(evaluationData);
      setSelectedStartupId((current) => current || startupData[0]?.id || "");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function runMatching() {
    if (!selectedStartupId) return;
    setRunning(true);
    setError("");
    try {
      const response = await runMatch(selectedStartupId);
      setMatchRun(response);
      setActiveView("matching");
      await loadInitialData();
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

  async function setRelationship(recommendation, status) {
    const payload = {
      match_run_id: recommendation.match_run_id,
      startup_id: recommendation.startup_id,
      mentor_id: recommendation.mentor_id,
      relationship_type: recommendation.relationship_type,
      status,
      lifecycle_status: status,
      notes: recommendation.ai?.rationale || "",
      next_action: recommendation.ai?.recommended_next_action || "",
      review_reason: status === "needs_review" ? recommendation.ai?.risks?.join("; ") : "",
      outcome_metric: recommendation.ai?.outcome_metric || ""
    };
    try {
      const created = await createRelationship(payload);
      setRelationships((current) => [created, ...current]);
      setDashboard((current) => current ? {
        ...current,
        relationships: {
          ...current.relationships,
          total: (current.relationships?.total || 0) + 1,
          approved: (current.relationships?.approved || 0) + (status === "approved" ? 1 : 0),
          review_needed: (current.relationships?.review_needed || 0) + (status === "needs_review" ? 1 : 0),
          rejected: (current.relationships?.rejected || 0) + (status === "rejected" ? 1 : 0)
        }
      } : current);
    } catch (err) {
      setError(err.message);
    }
  }

  async function refreshRecommendation(recommendationId) {
    setRefreshingRecommendationIds((current) => [...new Set([...current, recommendationId])]);
    setError("");
    try {
      const updated = await refreshRecommendationAi(recommendationId);
      setMatchRun((current) => current ? {
        ...current,
        recommendations: current.recommendations.map((recommendation) =>
          recommendation.id === recommendationId ? updated : recommendation
        )
      } : current);
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshingRecommendationIds((current) =>
        current.filter((id) => id !== recommendationId)
      );
    }
  }

  const selectedStartup = useMemo(
    () => startups.find((startup) => startup.id === selectedStartupId),
    [startups, selectedStartupId]
  );

  return (
    <main className="appShell">
      <aside className="sidebar">
        <div className="brandBlock">
          <div className="brandMark">ES</div>
          <div>
            <h1>EcoSync AI</h1>
            <p>Ecosystem linkage</p>
          </div>
        </div>
        <nav className="navList">
          <NavButton icon={BarChart3} label="Dashboard" active={activeView === "dashboard"} onClick={() => setActiveView("dashboard")} />
          <NavButton icon={Sparkles} label="Matching" active={activeView === "matching"} onClick={() => setActiveView("matching")} />
          <NavButton icon={Building2} label="Startups" active={activeView === "startups"} onClick={() => setActiveView("startups")} />
          <NavButton icon={UserRoundCheck} label="Mentors" active={activeView === "mentors"} onClick={() => setActiveView("mentors")} />
          <NavButton icon={Network} label="Partners" active={activeView === "partners"} onClick={() => setActiveView("partners")} />
          <NavButton icon={Handshake} label="Relationships" active={activeView === "relationships"} onClick={() => setActiveView("relationships")} />
          <NavButton icon={BarChart3} label="Evaluation" active={activeView === "evaluation"} onClick={() => setActiveView("evaluation")} />
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">{cohorts[0]?.name || "Kuala Lumpur SME Growth Cohort"}</p>
            <h2>{viewTitle(activeView)}</h2>
          </div>
          <button className="iconButton" onClick={loadInitialData} title="Refresh data">
            <RefreshCw size={18} />
          </button>
        </header>

        {error && <div className="alert">{error}</div>}
        {loading ? (
          <div className="emptyState">Loading ecosystem data...</div>
        ) : (
          <>
            {activeView === "dashboard" && <Dashboard dashboard={dashboard} cohorts={cohorts} programs={programs} partners={partners} evaluation={evaluation} />}
            {activeView === "matching" && (
              <MatchingWorkspace
                startups={startups}
                selectedStartup={selectedStartup}
                selectedStartupId={selectedStartupId}
                setSelectedStartupId={setSelectedStartupId}
                runMatching={runMatching}
                running={running}
                matchRun={matchRun}
                setRelationship={setRelationship}
                refreshRecommendation={refreshRecommendation}
                refreshingRecommendationIds={refreshingRecommendationIds}
              />
            )}
            {activeView === "startups" && <Directory title="Startup Profiles" items={startups} kind="startup" />}
            {activeView === "mentors" && <Directory title="Mentor Directory" items={mentors} kind="mentor" />}
            {activeView === "partners" && <Directory title="Partner Directory" items={partners} kind="partner" />}
            {activeView === "relationships" && <RelationshipBoard relationships={relationships} mentors={mentors} startups={startups} />}
            {activeView === "evaluation" && <EvaluationView evaluation={evaluation} />}
          </>
        )}
      </section>
    </main>
  );
}

function viewTitle(view) {
  return {
    dashboard: "Ecosystem Dashboard",
    matching: "Relationship Matching",
    startups: "Startup Profiles",
    mentors: "Mentor Directory",
    partners: "Partner Directory",
    relationships: "Relationship Board",
    evaluation: "AI Evaluation"
  }[view];
}

createRoot(document.getElementById("root")).render(<App />);
