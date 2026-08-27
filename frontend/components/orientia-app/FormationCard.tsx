import { ArrowRight } from "lucide-react";
import { Badge } from "./Badge";
import { formations } from "./data/formations";

function ArrowUpRight() {
  return <ArrowRight size={15} />;
}

export function FormationCard({
  formation,
  onClick,
}: {
  formation: (typeof formations)[number];
  onClick: () => void;
}) {
  return (
    <button
      className={`formation-card formation-${formation.color}`}
      onClick={onClick}
    >
      <div className="formation-visual">
        <div className="visual-grid" />
        <span className="visual-label">{formation.visual}</span>
        <div className={`formation-icon icon-${formation.color}`}>
          {formation.name.slice(0, 2)}
        </div>
      </div>
      <div className="formation-meta">
        <Badge label={formation.tag} tone={formation.color} />
        <span className="path-count">{formation.paths} parcours</span>
      </div>
      <h3>{formation.name}</h3>
      <p>{formation.title}</p>
      <small className="formation-desc">{formation.desc}</small>
      <div className="flex justify-end mt-2">
        <span className="card-link flex items-center gap-1">
          Voir les parcours <ArrowUpRight />
        </span>
      </div>
    </button>
  );
}
