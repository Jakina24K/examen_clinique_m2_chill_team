import { ArrowLeft, BookOpen, CheckCircle2 } from "lucide-react";
import { Badge } from "./Badge";
import { formations } from "./data/formations";
type ParcoursDetail = {
  description: string;
  matieres: string;
  specificites: string;
};

export function Parcours({
  mention,
  setView,
}: {
  mention: string;
  setView: (view: string) => void;
}) {
  const formation =
    formations.find((item) => item.name === mention) ?? formations[0];

  return (
    <div className="dashboard-content university-page">
      <div className="topline">
        <div>
          <span className="breadcrumb">ISPM / Parcours / {formation.name}</span>
          <h1>
            Les parcours de <span>{formation.title}.</span>
          </h1>
          <p className="profile-subtitle">
            Découvre les parcours associés à cette mention.
          </p>
        </div>
        <button className="edit-link" onClick={() => setView("explorer")}>
          <ArrowLeft size={14} /> Retour aux mentions
        </button>
      </div>

      <div className="explorer-intro">
        <div>
          <span className="section-kicker">MENTION ISPM</span>
          <p>{formation.desc}</p>
        </div>
        <div className="catalog-stat">
          <strong>{formation.paths}</strong>
          <span>
            parcours
            <br />
            référencés
          </span>
        </div>
      </div>

      <div className="formation-grid explorer-grid">
        {formation.parcours.map((parcours, index) => {
          const detail = (
            formation.parcoursDetails as unknown as Record<
              string,
              ParcoursDetail
            >
          )[parcours];

          return (
            <article
              className={`panel formation-card formation-${formation.color}`}
              key={parcours}
              style={{ cursor: "default", textAlign: "left" }}
            >
              <div className="formation-meta">
                <Badge label={formation.tag} tone={formation.color} />
                <span className="path-count">
                  Parcours {String(index + 1).padStart(2, "0")}
                </span>
              </div>
              <div className="section-icon" style={{ margin: "18px 0 14px" }}>
                <BookOpen size={18} />
              </div>
              <h3>{parcours}</h3>
              <p>{formation.title}</p>
              <small className="formation-desc">{detail.description}</small>
              <div
                style={{ display: "grid", gap: 8, marginTop: 14, fontSize: 11 }}
              >
                <span>
                  <strong>Matières :</strong> {detail.matieres}
                </span>
                <span>
                  <strong>Spécificités :</strong> {detail.specificites}
                </span>
              </div>
            </article>
          );
        })}
      </div>

      <div className="trace-note">
        <CheckCircle2 size={18} />
        <span>
          Ces parcours sont rattachés à la mention{" "}
          <strong>{formation.title}</strong>.
        </span>
      </div>
    </div>
  );
}
