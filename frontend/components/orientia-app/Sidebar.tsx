import {
  ArrowRight,
  BookOpen,
  CircleHelp,
  LayoutDashboard,
  MessageCircle,
  Settings2,
  UserRound,
  ChevronRight,
} from "lucide-react";
import { Brand } from "./Brand";

export function Sidebar({
  view,
  setView,
  onLogout,
}: {
  view: string;
  setView: (v: string) => void;
  onLogout: () => void;
}) {
  const items = [
    ["dashboard", "Tableau de bord", LayoutDashboard],
    ["assistant", "Mon assistant", MessageCircle],
    ["explorer", "Explorer les formations", BookOpen],
    ["profile", "Mon profil", UserRound],
  ] as const;

  return (
    <aside className="sidebar">
      <Brand compact />
      <div className="side-label">MON ESPACE</div>
      <nav className="side-nav">
        {items.map(([id, label, Icon]) => (
          <button
            key={id}
            className={view === id ? "active" : ""}
            onClick={() => setView(id)}
          >
            <Icon size={18} />
            {label}
            {id === "assistant" && <b className="notification">1</b>}
          </button>
        ))}
      </nav>
      <div className="side-bottom">
        <div className="side-help">
          <CircleHelp size={18} />
          <div>
            <strong>Besoin d'aide ?</strong>
            <small>Notre équipe est là.</small>
          </div>
        </div>
        <button>
          <Settings2 size={17} /> Paramètres
        </button>
        <button onClick={onLogout}>
          <ArrowRight size={17} /> Déconnexion
        </button>
        <div className="profile-mini">
          <span className="avatar">AM</span>
          <div>
            <strong>Aina M.</strong>
            <small>Étudiante</small>
          </div>
          <ChevronRight size={16} />
        </div>
      </div>
    </aside>
  );
}
