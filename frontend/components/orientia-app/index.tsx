"use client";

import { useEffect, useState } from "react";
import {
  Check,
  ArrowRight,
  User,
  Mail,
  Phone,
  MapPin,
  GraduationCap,
  Calendar,
  Sparkles,
  Save,
  Edit3,
} from "lucide-react";
import { Button } from "./Button";
import { Badge } from "./Badge";
import { Landing } from "./Landing";
import { Sidebar } from "./Sidebar";
import { Dashboard } from "./Dashboard";
import { Assistant } from "./Assistant";
import { Explorer } from "./Explorer";
import { Parcours } from "./Parcours";
import { LoginPage, RegisterPage } from "@/components/auth-pages";

export function Profile({ setView }: { setView: (v: string) => void }) {
  const [profile, setProfile] = useState({
    prenom: "Aina",
    nom: "Marie",
    email: "aina.marie@email.com",
    telephone: "",
    serie: "D",
    annee: "2026",
    ville: "Antananarivo",
  });

  const [selectedInterests, setSelectedInterests] = useState<string[]>([
    "Résoudre des problèmes",
    "Créer & imaginer",
    "Comprendre le monde",
  ]);

  const [selectedSubjects, setSelectedSubjects] = useState<string[]>([
    "Mathématiques",
    "Sciences physiques",
  ]);

  const [selectedSkills, setSelectedSkills] = useState<string[]>([
    "Analyse",
    "Créativité",
  ]);

  const toggleInterest = (value: string) =>
    setSelectedInterests((items) =>
      items.includes(value)
        ? items.filter((item) => item !== value)
        : [...items, value],
    );

  const toggleSubject = (value: string) =>
    setSelectedSubjects((items) =>
      items.includes(value)
        ? items.filter((item) => item !== value)
        : [...items, value],
    );

  const toggleSkill = (value: string) =>
    setSelectedSkills((items) =>
      items.includes(value)
        ? items.filter((item) => item !== value)
        : [...items, value],
    );

  useEffect(() => {
    const saved = window.localStorage.getItem("orientia_profile");
    if (saved) {
      const parsed = JSON.parse(saved);
      setProfile((current) => ({ ...current, ...parsed }));
      if (parsed.interests) setSelectedInterests(parsed.interests);
      if (parsed.subjects) setSelectedSubjects(parsed.subjects);
      if (parsed.skills) setSelectedSkills(parsed.skills);
    }
  }, []);

  const update = (field: keyof typeof profile, value: string) =>
    setProfile((current) => ({ ...current, [field]: value }));

  const saveProfile = () => {
    const data = {
      ...profile,
      interests: selectedInterests,
      subjects: selectedSubjects,
      skills: selectedSkills,
    };
    window.localStorage.setItem("orientia_profile", JSON.stringify(data));
    setView("dashboard");
  };

  // Calcul du pourcentage de complétion
  const completionPercentage = Math.min(
    40 +
      (selectedInterests.length > 0 ? 20 : 0) +
      (selectedSubjects.length >= 2 ? 20 : 0) +
      (selectedSkills.length >= 2 ? 20 : 0),
    100,
  );

  return (
    <div className="dashboard-content profile-page">
      {/* HEADER */}
      <div className="profile-header">
        <div className="topline">
          <div>
            <span className="breadcrumb">Mon espace / Mon profil</span>
            <h1>
              Ton <span>profil d'orientation</span>
            </h1>
            <p className="profile-subtitle">
              Complète ces informations pour recevoir des recommandations
              personnalisées.
            </p>
          </div>
          <Button onClick={saveProfile} className="save-btn">
            <Save size={16} /> Enregistrer
          </Button>
        </div>
      </div>

      <div className="profile-layout">
        {/* FORMULAIRE PRINCIPAL */}
        <section className="panel form-panel">
          {/* INFORMATIONS PERSONNELLES */}
          <div className="form-section">
            <div className="section-header">
              <div className="section-icon">
                <User size={18} />
              </div>
              <div>
                <span className="section-kicker">
                  INFORMATIONS PERSONNELLES
                </span>
                <h3>Qui es-tu ?</h3>
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label>Prénom</label>
                <div className="input-wrapper">
                  <User size={16} className="input-icon" />
                  <input
                    value={profile.prenom}
                    onChange={(event) => update("prenom", event.target.value)}
                    placeholder="Ton prénom"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Nom</label>
                <div className="input-wrapper">
                  <User size={16} className="input-icon" />
                  <input
                    value={profile.nom}
                    onChange={(event) => update("nom", event.target.value)}
                    placeholder="Ton nom"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Adresse e-mail</label>
                <div className="input-wrapper">
                  <Mail size={16} className="input-icon" />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(event) => update("email", event.target.value)}
                    placeholder="ton.email@exemple.com"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Téléphone</label>
                <div className="input-wrapper">
                  <Phone size={16} className="input-icon" />
                  <input
                    value={profile.telephone}
                    onChange={(event) =>
                      update("telephone", event.target.value)
                    }
                    placeholder="+261 34 00 000 00"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Ville de résidence</label>
                <div className="input-wrapper">
                  <MapPin size={16} className="input-icon" />
                  <input
                    value={profile.ville}
                    onChange={(event) => update("ville", event.target.value)}
                    placeholder="Antananarivo"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Série au baccalauréat</label>
                <div className="input-wrapper">
                  <GraduationCap size={16} className="input-icon" />
                  <select
                    value={profile.serie}
                    onChange={(event) => update("serie", event.target.value)}
                  >
                    <option value="D">Série D</option>
                    <option value="C">Série C</option>
                    <option value="A">Série A</option>
                    <option value="S">Série S</option>
                    <option value="ES">Série ES</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Année d'obtention</label>
                <div className="input-wrapper">
                  <Calendar size={16} className="input-icon" />
                  <select
                    value={profile.annee}
                    onChange={(event) => update("annee", event.target.value)}
                  >
                    <option value="2026">2026</option>
                    <option value="2025">2025</option>
                    <option value="2024">2024</option>
                    <option value="2023">2023</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* CENTRES D'INTÉRÊT */}
          <div className="form-section">
            <div className="section-header">
              <div className="section-icon">
                <Sparkles size={18} />
              </div>
              <div>
                <span className="section-kicker">OPTIONNEL</span>
                <h3>Centres d'intérêt</h3>
                <p className="section-note">
                  Ce qui te passionne et te motive au quotidien.
                </p>
              </div>
            </div>

            <div className="tag-grid">
              {[
                "Résoudre des problèmes",
                "Créer & imaginer",
                "Comprendre le monde",
                "Travailler en équipe",
                "Analyser des données",
                "Construire des projets",
                "Aider les autres",
                "Voyager & découvrir",
                "Innover & expérimenter",
              ].map((x) => (
                <button
                  type="button"
                  key={x}
                  onClick={() => toggleInterest(x)}
                  className={`tag-btn ${selectedInterests.includes(x) ? "selected" : ""}`}
                  aria-pressed={selectedInterests.includes(x)}
                >
                  {selectedInterests.includes(x) && <Check size={14} />}
                  {x}
                </button>
              ))}
            </div>
          </div>

          {/* MATIÈRES PRÉFÉRÉES */}
          <div className="form-section">
            <div className="section-header">
              <div className="section-icon">
                <BookOpen size={18} />
              </div>
              <div>
                <span className="section-kicker">PRÉFÉRENCES ACADÉMIQUES</span>
                <h3>Matières préférées</h3>
                <p className="section-note">
                  Les matières où tu te sens le plus à l'aise.
                </p>
              </div>
            </div>

            <div className="tag-grid">
              {[
                "Mathématiques",
                "Sciences physiques",
                "Informatique",
                "Biologie",
                "Économie",
                "Français",
                "Anglais",
                "Histoire-Géo",
                "Philosophie",
              ].map((x) => (
                <button
                  type="button"
                  key={x}
                  onClick={() => toggleSubject(x)}
                  className={`tag-btn ${selectedSubjects.includes(x) ? "selected" : ""}`}
                  aria-pressed={selectedSubjects.includes(x)}
                >
                  {selectedSubjects.includes(x) && <Check size={14} />}
                  {x}
                </button>
              ))}
            </div>
          </div>

          {/* COMPÉTENCES */}
          <div className="form-section">
            <div className="section-header">
              <div className="section-icon">
                <Award size={18} />
              </div>
              <div>
                <span className="section-kicker">COMPÉTENCES</span>
                <h3>Tes atouts</h3>
                <p className="section-note">
                  Les compétences qui te définissent.
                </p>
              </div>
            </div>

            <div className="tag-grid">
              {[
                "Analyse",
                "Créativité",
                "Communication",
                "Organisation",
                "Esprit d'équipe",
                "Leadership",
                "Adaptabilité",
                "Rigueur",
                "Empathie",
              ].map((x) => (
                <button
                  type="button"
                  key={x}
                  onClick={() => toggleSkill(x)}
                  className={`tag-btn ${selectedSkills.includes(x) ? "selected" : ""}`}
                  aria-pressed={selectedSkills.includes(x)}
                >
                  {selectedSkills.includes(x) && <Check size={14} />}
                  {x}
                </button>
              ))}
            </div>
          </div>

          {/* BOUTON D'ENREGISTREMENT MOBILE */}
          <div className="mobile-save">
            <Button onClick={saveProfile} className="save-btn-full">
              <Save size={16} /> Enregistrer mon profil
            </Button>
          </div>
        </section>

        {/* SIDEBAR - PROGRESSION */}
        <aside className="panel completion-card">
          <div className="completion-visual">
            <div>
              <strong>{completionPercentage}</strong>
              <span>%</span>
            </div>
          </div>

          <h3>Progression du profil</h3>
          <div className="completion-bar">
            <div className="completion-bar-track">
              <div
                className="completion-bar-fill"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
            <span className="completion-bar-label">
              {completionPercentage}% complété
            </span>
          </div>

          <div className="completion-list">
            <div className="completion-item done">
              <Check size={14} />
              <span>Informations générales</span>
              <Badge label="OK" tone="green" />
            </div>
            <div className="completion-item done">
              <Check size={14} />
              <span>Matières préférées</span>
              <Badge label="OK" tone="green" />
            </div>
            <div className="completion-item done">
              <Check size={14} />
              <span>Compétences</span>
              <Badge label="OK" tone="green" />
            </div>
            <div
              className={`completion-item ${selectedInterests.length > 0 ? "done" : "pending"}`}
            >
              {selectedInterests.length > 0 ? (
                <Check size={14} />
              ) : (
                <span className="circle">○</span>
              )}
              <span>Centres d'intérêt</span>
              {selectedInterests.length > 0 ? (
                <Badge label="OK" tone="green" />
              ) : (
                <Badge label="Optionnel" tone="yellow" />
              )}
            </div>
          </div>

          <div className="completion-tip">
            <Sparkles size={16} />
            <div>
              <strong>Astuce</strong>
              <p>
                Plus ton profil est complet, plus les recommandations seront
                précises.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

// Icônes supplémentaires
function BookOpen(props: any) {
  return (
    <svg
      {...props}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
    </svg>
  );
}

function Award(props: any) {
  return (
    <svg
      {...props}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="8" r="6" />
      <path d="M5.5 13.5L3 21l4-1.5L12 21l5-1.5L21 21l-2.5-7.5" />
    </svg>
  );
}

function IsmpFloatingLogo() {
  return (
    <a
      href="https://ispm-edu.com/"
      target="_blank"
      rel="noreferrer"
      aria-label="Visiter le site de l'ISPM"
      style={{
        position: "fixed",
        right: 24,
        bottom: 24,
        zIndex: 20,
        display: "grid",
        placeItems: "center",
        width: 58,
        height: 58,
        borderRadius: "50%",
        background: "#fff",
        boxShadow: "0 8px 24px rgba(0,0,0,.25)",
      }}
    >
      <img
        src="/logoispm.jfif"
        alt="Logo ISPM"
        width="44"
        height="44"
        style={{
          width: 44,
          height: 44,
          borderRadius: "50%",
          objectFit: "cover",
        }}
      />
    </a>
  );
}

export default function OrientiaApp() {
  const [started, setStarted] = useState(false);
  const [view, setView] = useState("dashboard");
  const [ready, setReady] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register" | null>(null);

  useEffect(() => {
    const path = window.location.pathname;
    const token = window.localStorage.getItem("user_token");

    if (path === "/login") {
      setAuthMode("login");
      setReady(true);
      return;
    }
    if (path === "/register") {
      setAuthMode("register");
      setReady(true);
      return;
    }

    if (["/dashboard", "/assistant", "/explorer", "/profile"].includes(path)) {
      if (!token) {
        window.location.href = "/login";
        return;
      }
      setView(path.slice(1));
      setStarted(true);
    }
    if (path.startsWith("/parcours/")) {
      if (!token) {
        window.location.href = "/login";
        return;
      }
      setView(
        `parcours:${decodeURIComponent(path.slice("/parcours/".length))}`,
      );
      setStarted(true);
    }
    setReady(true);
  }, []);

  const navigate = (next: string) => {
    setView(next);
    setStarted(true);
    const nextPath = next.startsWith("parcours:")
      ? `/parcours/${encodeURIComponent(next.slice("parcours:".length))}`
      : `/${next}`;
    window.history.pushState({}, "", nextPath);
  };

  const logout = () => {
    window.localStorage.removeItem("user_token");
    window.localStorage.removeItem("orientia_user");
    window.location.href = "/login";
  };

  if (!ready) return null;
  if (authMode === "login") return <LoginPage />;
  if (authMode === "register") return <RegisterPage />;
  if (!started)
    return <Landing onStart={() => (window.location.href = "/login")} />;

  return (
    <div className="app-shell">
      <Sidebar view={view} setView={navigate} onLogout={logout} />
      <main className="main-area">
        {view === "dashboard" && <Dashboard setView={navigate} />}
        {view === "assistant" && <Assistant />}
        {view === "explorer" && <Explorer setView={navigate} />}
        {view === "profile" && <Profile setView={navigate} />}
        {view.startsWith("parcours:") && (
          <Parcours
            mention={view.slice("parcours:".length)}
            setView={navigate}
          />
        )}
      </main>
      <IsmpFloatingLogo />
    </div>
  );
}
