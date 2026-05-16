import React from "react";
import { EmptyState } from "../components/ui.jsx";

export function RelationshipBoard({ relationships, mentors, startups }) {
  if (!relationships.length) {
    return <EmptyState>Approved, reviewed, active, and rejected relationships will appear here during the demo.</EmptyState>;
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
                <p>{mentor?.name || relationship.mentor_id} | {relationship.relationship_type}</p>
                <small>{relationship.next_action || relationship.notes}</small>
              </div>
              <span className={`statusBadge ${relationship.status}`}>{relationship.status}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
