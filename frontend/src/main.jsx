import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart3,
  Building2,
  Check,
  Clock3,
  Handshake,
  RefreshCw,
  Search,
  Sparkles,
  UserRoundCheck,
  X
} from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function App() {
  const [cohorts, setCohorts] = useState([]);
  const [startups, setStartups] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [relationships, setRelationships] = useState([]);
  const [selectedStartupId, setSelectedStartupId] = useState("");
  const [matchRun, setMatchRun] = useState(null);
  const [activeView, setActiveView] = useState("matching");
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    setLoading(true);
    setError("");
    try {
      const [cohortData, startupData, mentorData] = await Promise.all([
        fetchJson("/cohorts/"),
        fetchJson("/startups/"),
        fetchJson("/mentors/")
      ]);
      setCohorts(cohortData);
      setStartups(startupData);
      setMentors(mentorData);
      setSelectedStartupId(startupData[0]?.id || "");
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
      const response = await fetchJson("/match-runs/", {
        method: "POST",
        body: JSON.stringify({ startup_id: selectedStartupId })
      });
      setMatchRun(response);
      setActiveView("matching");
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
      notes: recommendation.ai.recommended_next_action
    };
    try {
      const created = await fetchJson("/relationships/", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setRelationships((current) => [created, ...current]);
    } catch (err) {
      setError(err.message);
    }
  }

  const selectedStartup = useMemo(
    () => startups.find((startup) => startup.id === selectedStartupId),
    [startups, selectedStartupId]
  );

  const stats = [
    { label: "Startups", value: startups.length, icon: Building2 },
    { label: "Mentors", value: mentors.length, icon: UserRoundCheck },
    { label: "Recommended", value: matchRun?.recommendations?.length || 0, icon: Sparkles },
    { label: "Approved", value: relationships.filter((item) => item.status === "approved").length, icon: Handshake }
  ];

  return (
    <main className="appShell">
      <aside className="sidebar">
        <div className="brandBlock">
          <div className="brandMark">ES</div>
          <div>
            <h1>EcoSync AI</h1>
            <p>Relationship orchestration</p>
          </div>
        </div>
        <nav className="navList">
          <NavButton icon={BarChart3} label="Overview" active={activeView === "overview"} onClick={() => setActiveView("overview")} />
          <NavButton icon={Sparkles} label="Matching" active={activeView === "matching"} onClick={() => setActiveView("matching")} />
          <NavButton icon={Building2} label="Startups" active={activeView === "startups"} onClick={() => setActiveView("startups")} />
          <NavButton icon={UserRoundCheck} label="Mentors" active={activeView === "mentors"} onClick={() => setActiveView("mentors")} />
          <NavButton icon={Handshake} label="Relationships" active={activeView === "relationships"} onClick={() => setActiveView("relationships")} />
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
          <div className="emptyState">Loading cohort data...</div>
        ) : (
          <>
            {activeView === "overview" && <Overview stats={stats} cohorts={cohorts} startups={startups} mentors={mentors} />}
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
              />
            )}
            {activeView === "startups" && <StartupDirectory startups={startups} />}
            {activeView === "mentors" && <MentorDirectory mentors={mentors} />}
            {activeView === "relationships" && <RelationshipBoard relationships={relationships} mentors={mentors} startups={startups} />}
          </>
        )}
      </section>
    </main>
  );
}

function NavButton({ icon: Icon, label, active, onClick }) {
  return (
    <button className={`navButton ${active ? "active" : ""}`} onClick={onClick}>
      <Icon size={18} />
      <span>{label}</span>
    </button>
  );
}

function Overview({ stats, cohorts, startups, mentors }) {
  return (
    <div className="gridStack">
      <section className="statsGrid">
        {stats.map(({ label, value, icon: Icon }) => (
          <div className="metricCard" key={label}>
            <Icon size={20} />
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>
      <section className="panel">
        <div className="panelHeader">
          <h3>Cohort Snapshot</h3>
          <span className="statusBadge">{cohorts[0]?.status || "active"}</span>
        </div>
        <div className="twoColumn">
          <Fact label="Program" value={cohorts[0]?.program} />
          <Fact label="Location" value={cohorts[0]?.location} />
          <Fact label="Focus" value={cohorts[0]?.focus_domains?.join(", ")} />
          <Fact label="Demo anchor" value={startups[0]?.name} />
        </div>
      </section>
      <section className="splitPanels">
        <CompactList title="High-need startups" items={startups} getMeta={(item) => item.requested_support?.join(", ")} />
        <CompactList title="Mentor capabilities" items={mentors} getMeta={(item) => item.expertise?.slice(0, 3).join(", ")} />
      </section>
    </div>
  );
}

function MatchingWorkspace({ startups, selectedStartup, selectedStartupId, setSelectedStartupId, runMatching, running, matchRun, setRelationship }) {
  return (
    <div className="matchingLayout">
      <section className="panel controlPanel">
        <div className="panelHeader">
          <h3>Run Mentor Matching</h3>
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
            <p>{selectedStartup.domain} · {selectedStartup.stage} · {selectedStartup.location}</p>
            <TagRow tags={selectedStartup.requested_support} />
          </div>
        )}
        <button className="primaryButton" onClick={runMatching} disabled={running}>
          <Sparkles size={18} />
          {running ? "Running..." : "Run Matching"}
        </button>
      </section>

      <section className="resultsColumn">
        {!matchRun ? (
          <div className="emptyState">Select the F&B startup and run matching to generate ranked mentor relationships.</div>
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

function RecommendationCard({ recommendation, rank, setRelationship }) {
  const mentor = recommendation.mentor;
  return (
    <article className="recommendationCard">
      <div className="recommendationTop">
        <div>
          <span className="rankBadge">#{rank}</span>
          <h3>{mentor.name}</h3>
          <p>{mentor.mentoring_style} · {mentor.availability}</p>
        </div>
        <ScoreRing score={recommendation.total_score} />
      </div>
      <TagRow tags={[recommendation.relationship_type, ...mentor.expertise.slice(0, 3)]} />
      <p className="rationale">{recommendation.ai.rationale}</p>
      <ScoreBreakdown breakdown={recommendation.score_breakdown} />
      <div className="cardFooter">
        <span className="aiMode">{recommendation.ai.ai_mode}</span>
        <div className="actionGroup">
          <button className="ghostButton" onClick={() => setRelationship(recommendation, "review")} title="Mark for review">
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

function ScoreRing({ score }) {
  return (
    <div className="scoreRing" style={{ "--score": `${score * 3.6}deg` }}>
      <strong>{score}</strong>
      <span>fit</span>
    </div>
  );
}

function ScoreBreakdown({ breakdown }) {
  return (
    <div className="breakdown">
      {Object.entries(breakdown).map(([key, value]) => (
        <div className="barRow" key={key}>
          <span>{labelize(key)}</span>
          <div className="barTrack"><div style={{ width: `${Math.min(100, value * 4)}%` }} /></div>
          <b>{value}</b>
        </div>
      ))}
    </div>
  );
}

function StartupDirectory({ startups }) {
  return <Directory title="Startup Directory" items={startups} kind="startup" />;
}

function MentorDirectory({ mentors }) {
  return <Directory title="Mentor Directory" items={mentors} kind="mentor" />;
}

function Directory({ title, items, kind }) {
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
              <p>{kind === "startup" ? `${item.domain} · ${item.stage}` : item.expertise.slice(0, 3).join(", ")}</p>
            </div>
            <span>{item.location}</span>
            <TagRow tags={kind === "startup" ? item.requested_support : item.industries} />
          </div>
        ))}
      </div>
    </section>
  );
}

function RelationshipBoard({ relationships, mentors, startups }) {
  if (!relationships.length) {
    return <div className="emptyState">Approved and reviewed relationships will appear here during the demo.</div>;
  }
  return (
    <section className="panel">
      <div className="panelHeader">
        <h3>Relationship Board</h3>
        <span className="statusBadge">{relationships.length} actions</span>
      </div>
      <div className="tableList">
        {relationships.map((relationship) => {
          const startup = startups.find((item) => item.id === relationship.startup_id);
          const mentor = mentors.find((item) => item.id === relationship.mentor_id);
          return (
            <div className="tableRow" key={relationship.id}>
              <div>
                <strong>{startup?.name || relationship.startup_id}</strong>
                <p>{mentor?.name || relationship.mentor_id} · {relationship.relationship_type}</p>
              </div>
              <span className={`statusBadge ${relationship.status}`}>{relationship.status}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function CompactList({ title, items, getMeta }) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      <div className="compactList">
        {items.map((item) => (
          <div key={item.id}>
            <strong>{item.name}</strong>
            <p>{getMeta(item)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function TagRow({ tags = [] }) {
  return (
    <div className="tagRow">
      {tags.slice(0, 5).map((tag) => <span key={tag}>{tag}</span>)}
    </div>
  );
}

function Fact({ label, value }) {
  return (
    <div className="fact">
      <span>{label}</span>
      <strong>{value || "Not set"}</strong>
    </div>
  );
}

function viewTitle(view) {
  return {
    overview: "Cohort Overview",
    matching: "Matching Workspace",
    startups: "Startup Directory",
    mentors: "Mentor Directory",
    relationships: "Relationship Board"
  }[view];
}

function labelize(value) {
  return value.replaceAll("_", " ");
}

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

createRoot(document.getElementById("root")).render(<App />);
