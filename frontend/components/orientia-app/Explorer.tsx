import { useMemo, useState } from "react";
import { Filter, Search } from "lucide-react";
import { FormationCard } from "./FormationCard";
import { formations } from "./data/formations";

export function Explorer({ setView }: { setView: (v: string) => void }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(
    () =>
      formations.filter((f) =>
        `${f.name} ${f.title} ${f.tag} ${f.visual}`
          .toLowerCase()
          .includes(query.toLowerCase()),
      ),
    [query],
  );

  return (
    <div className="dashboard-content university-page">
      <div className="topline">
        <div>
          <span className="breadcrumb">ISPM / Catalogue académique</span>
          <h1>
            Les formations de <span>l'ISPM.</span>
          </h1>
        </div>
      </div>
      <div className="explorer-intro">
        <div>
          <p>
            Explore les cinq mentions de l'Institut Supérieur Polytechnique de
            Madagascar. Compare les parcours et projette-toi dans ton futur
            campus.
          </p>
        </div>
        <div className="catalog-stat">
          <strong>05</strong>
          <span>
            mentions
            <br />
            académiques
          </span>
        </div>
        <div className="catalog-stat">
          <strong>16</strong>
          <span>
            parcours
            <br />
            proposés
          </span>
        </div>
      </div>
      <div className="filter-bar">
        <div className="search-box">
          <Search size={18} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Rechercher une mention ou un domaine..."
            aria-label="Rechercher une formation"
          />
        </div>
        <button>
          <Filter size={16} /> Domaines <span>{filtered.length}</span>
        </button>
      </div>
      <div className="formation-grid explorer-grid formation-gallery">
        {filtered.map((f) => (
          <FormationCard
            key={f.name}
            formation={f}
            onClick={() => setView("assistant")}
          />
        ))}
      </div>
    </div>
  );
}
