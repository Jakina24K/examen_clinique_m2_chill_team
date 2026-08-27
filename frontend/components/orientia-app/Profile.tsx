import { useState } from "react";
import { Check, ArrowRight } from "lucide-react";
import { Button } from "./Button";
import { Badge } from "./Badge";

export function Profile({ setView }: { setView: (v: string) => void }) {
  const [selected, setSelected] = useState<string[]>([
    "Résoudre des problèmes",
    "Créer & imaginer",
    "Comprendre le monde",
  ]);

  const toggle = (value: string) =>
    setSelected((items) =>
      items.includes(value)
        ? items.filter((item) => item !== value)
        : [...items, value],
    );

  return (
    <div className="dashboard-content">
      <div className="topline">
        <div>
          <span className="breadcrumb">Mon espace / Mon profil</span>
          <h1>
            Construisons ton <span>profil d'orientation.</span>
          </h1>
        </div>
        <Button onClick={() => setView("dashboard")}>
          Enregistrer les changements <Check size={16} />
        </Button>
      </div>
      <div className="profile-layout">
        <section className="panel form-panel">
          <div className="panel-head">
            <div>
              <span className="section-kicker">À PROPOS DE TOI</span>
              <h3>Les informations essentielles</h3>
            </div>
            <Badge label="Profil étudiant" tone="green" />
          </div>
          <div className="form-grid">
            <label>
              Prénom
              <input defaultValue="Aina Marie" />
            </label>
            <label>
              Adresse e-mail
              <input defaultValue="aina.marie@email.com" />
            </label>
            <label>
              Série au baccalauréat
              <select defaultValue="D">
                <option>D</option>
                <option>C</option>
                <option>A</option>
              </select>
            </label>
            <label>
              Année d'obtention
              <select defaultValue="2026">
                <option>2026</option>
                <option>2027</option>
              </select>
            </label>
          </div>
          <div className="form-section">
            <span className="section-kicker">
              OPTIONNEL · TES CENTRES D'INTÉRÊT
            </span>
            <h3>Qu'est-ce qui te plaît le plus ?</h3>
            <p className="section-note">
              Ces choix sont facultatifs et servent uniquement à affiner tes
              recommandations.
            </p>
            <div className="tag-select">
              {[
                "Résoudre des problèmes",
                "Créer & imaginer",
                "Comprendre le monde",
                "Travailler en équipe",
                "Analyser des données",
                "Construire des projets",
              ].map((x) => (
                <button
                  type="button"
                  key={x}
                  onClick={() => toggle(x)}
                  className={selected.includes(x) ? "selected" : ""}
                  aria-pressed={selected.includes(x)}
                >
                  {selected.includes(x) && <Check size={14} />}
                  {x}
                </button>
              ))}
            </div>
          </div>
          <div className="form-section">
            <span className="section-kicker">TES PRÉFÉRENCES ACADÉMIQUES</span>
            <h3>Matières préférées</h3>
            <div className="tag-select">
              {[
                "Mathématiques",
                "Sciences physiques",
                "Informatique",
                "Biologie",
                "Économie",
                "Français",
              ].map((x, i) => (
                <button
                  type="button"
                  key={x}
                  className={i < 2 ? "selected" : ""}
                  aria-pressed={i < 2}
                >
                  {i < 2 && <Check size={14} />}
                  {x}
                </button>
              ))}
            </div>
            <h3 className="subheading">Compétences</h3>
            <div className="tag-select">
              {[
                "Analyse",
                "Créativité",
                "Communication",
                "Organisation",
                "Esprit d'équipe",
              ].map((x, i) => (
                <button
                  type="button"
                  key={x}
                  className={i < 2 ? "selected" : ""}
                  aria-pressed={i < 2}
                >
                  {i < 2 && <Check size={14} />}
                  {x}
                </button>
              ))}
            </div>
          </div>
        </section>
        <aside className="panel completion-card">
          <div className="completion-visual">
            <div>
              <strong>65</strong>
              <span>%</span>
            </div>
          </div>
          <h3>Ton profil prend forme</h3>
          <p>
            Les centres d'intérêt restent optionnels. Ajoute tes matières et
            compétences pour personnaliser tes recommandations.
          </p>
          <div className="completion-list">
            <span>
              <Check size={14} /> Informations générales
            </span>
            <span>
              <Check size={14} /> Matières préférées
            </span>
            <span>
              <Check size={14} /> Tes compétences
            </span>
            <span className="pending">○ Centres d'intérêt (optionnel)</span>
          </div>
        </aside>
      </div>
    </div>
  );
}
