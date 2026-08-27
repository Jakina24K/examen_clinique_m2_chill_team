import {
  ArrowRight,
  Bot,
  Check,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { Button } from "./Button";
import { Badge } from "./Badge";
import { FormationCard } from "./FormationCard";
import { formations } from "./data/formations";

export function Dashboard({ setView }: { setView: (v: string) => void }) {
  return (
    <div className="dashboard-content">
      <div className="topline">
        <div>
          <span className="breadcrumb">Mon espace / Tableau de bord</span>
          <h1>
            Bonjour Aina, <span>prête à trouver ta voie ?</span>
          </h1>
        </div>
        <div className="top-actions">
          <button aria-label="Notifications" className="icon-button">
            ◌<b />
          </button>
          <div className="avatar">AM</div>
        </div>
      </div>
      <div className="welcome-banner">
        <div>
          <div className="eyebrow">TON ORIENTATION, TON RYTHME</div>
          <h2>
            On commence par mieux
            <br />
            <em>te connaître.</em>
          </h2>
          <p>
            Complète ton profil pour recevoir des recommandations qui te
            ressemblent vraiment.
          </p>
          <Button onClick={() => setView("profile")}>
            Compléter mon profil <ArrowRight size={16} />
          </Button>
        </div>
        <div className="progress-ring">
          <strong>
            40<span>%</span>
          </strong>
          <small>profil complété</small>
        </div>
      </div>
      <div className="dashboard-grid">
        <section className="panel profile-panel">
          <div className="panel-head">
            <div>
              <span className="section-kicker">MON PROFIL</span>
              <h3>Ce que nous savons de toi</h3>
            </div>
            <button className="edit-link" onClick={() => setView("profile")}>
              Modifier <ArrowRight size={14} />
            </button>
          </div>
          <div className="profile-info">
            <span className="large-avatar">AM</span>
            <div>
              <strong>Aina Marie</strong>
              <span>Terminale · Série D</span>
            </div>
            <Badge label="En construction" tone="yellow" />
          </div>
          <div className="skill-row">
            <span>Mathématiques</span>
            <span>Sciences</span>
            <span>Créativité</span>
          </div>
          <div className="profile-progress">
            <span />
            <b>40%</b>
          </div>
        </section>
        <section className="panel assistant-panel">
          <div className="assistant-glow">
            <Bot size={22} />
          </div>
          <div>
            <span className="section-kicker">ORIENT'IA</span>
            <h3>Une question sur ton avenir ?</h3>
            <p>
              Je peux t'aider à y voir plus clair, sans jamais décider à ta
              place.
            </p>
            <button
              className="assistant-link"
              onClick={() => setView("assistant")}
            >
              Discuter avec l'assistant <ArrowRight size={15} />
            </button>
          </div>
        </section>
      </div>
      <div className="section-heading">
        <div>
          <span className="section-kicker">POUR COMMENCER</span>
          <h2>Explore les formations</h2>
        </div>
        <button className="edit-link" onClick={() => setView("explorer")}>
          Voir toutes les formations <ArrowRight size={14} />
        </button>
      </div>
      <div className="formation-grid">
        {formations.slice(0, 3).map((f) => (
          <FormationCard
            key={f.name}
            formation={f}
            onClick={() => setView("explorer")}
          />
        ))}
      </div>
      <div className="trace-note">
        <ShieldCheck size={18} />
        <span>
          Les recommandations ORIENT'IA s'appuient sur{" "}
          <strong>12 sources officielles ISPM</strong> vérifiées le 20 août
          2026.
        </span>
        <a href="#sources">
          En savoir plus <ChevronRight size={14} />
        </a>
      </div>
    </div>
  );
}
