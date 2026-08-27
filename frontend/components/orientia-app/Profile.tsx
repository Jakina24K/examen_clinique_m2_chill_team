"use client";

import { useEffect, useState } from "react";
import {
  Check,
  User,
  Mail,
  Phone,
  MapPin,
  GraduationCap,
  Calendar,
  Sparkles,
  Save,
  BookOpen,
  Award,
  Heart,
  Brain,
  Users,
  Globe,
  Target,
  Briefcase,
  Zap,
  Eye,
  EyeOff,
} from "lucide-react";
import { Button } from "./Button";
import { Badge } from "./Badge";

export function Profile({ setView }: { setView: (v: string) => void }) {
  const [profile, setProfile] = useState({
    prenom: "Aina",
    nom: "Marie",
    email: "aina.marie@email.com",
    telephone: "034 00 000 00",
    serie: "D",
    annee: "2026",
    ville: "Antananarivo",
    bio: "Étudiant passionné par les sciences et la technologie",
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

  const [isSaving, setIsSaving] = useState(false);
  const [showSaved, setShowSaved] = useState(false);

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
    setIsSaving(true);
    const data = {
      ...profile,
      interests: selectedInterests,
      subjects: selectedSubjects,
      skills: selectedSkills,
    };
    window.localStorage.setItem("orientia_profile", JSON.stringify(data));
    setTimeout(() => {
      setIsSaving(false);
      setShowSaved(true);
      setTimeout(() => setShowSaved(false), 3000);
      setView("dashboard");
    }, 800);
  };

  // Calcul du pourcentage de complétion
  const completionPercentage = Math.min(
    40 +
      (selectedInterests.length > 0 ? 20 : 0) +
      (selectedSubjects.length >= 2 ? 20 : 0) +
      (selectedSkills.length >= 2 ? 20 : 0),
    100,
  );

  const isComplete = completionPercentage === 100;

  return (
    <div className="profile-page-modern">
      <div className="profile-container">
        {/* HEADER */}
        <div className="profile-header-modern">
          <div className="profile-header-left">
            <div className="profile-avatar">
              <span>
                {profile.prenom[0]}
                {profile.nom[0]}
              </span>
            </div>
            <div>
              <h1>
                {profile.prenom} {profile.nom}
              </h1>
              <p className="profile-header-subtitle">
                Étudiant · Série {profile.serie}
              </p>
            </div>
          </div>
          <div className="profile-header-right">
            <div className="profile-completion-badge">
              <div
                className="completion-ring"
                style={{
                  background: `conic-gradient(var(--primary) ${completionPercentage}%, var(--muted) ${completionPercentage}%)`,
                }}
              >
                <span>{completionPercentage}%</span>
              </div>
            </div>
            <button
              onClick={saveProfile}
              className="profile-save-btn"
              disabled={isSaving}
            >
              {isSaving ? (
                <span className="saving-spinner">⏳</span>
              ) : (
                <Save size={18} />
              )}
              {isSaving ? "Enregistrement..." : "Enregistrer"}
            </button>
          </div>
        </div>

        {/* MESSAGE DE SUCCÈS */}
        {showSaved && (
          <div className="profile-saved-toast">
            <Check size={18} />
            <span>Profil enregistré avec succès !</span>
          </div>
        )}

        <div className="profile-body">
          {/* FORMULAIRE */}
          <div className="profile-form">
            {/* SECTION 1 : INFORMATIONS PERSONNELLES */}
            <div className="profile-section">
              <div className="profile-section-header">
                <div className="profile-section-icon">
                  <User size={20} />
                </div>
                <div>
                  <h3>Informations personnelles</h3>
                  <p>Vos coordonnées et informations académiques</p>
                </div>
              </div>

              <div className="profile-grid">
                <div className="profile-field">
                  <label>Prénom</label>
                  <div className="profile-input">
                    <User size={16} />
                    <input
                      value={profile.prenom}
                      onChange={(e) => update("prenom", e.target.value)}
                      placeholder="Votre prénom"
                    />
                  </div>
                </div>

                <div className="profile-field">
                  <label>Nom</label>
                  <div className="profile-input">
                    <User size={16} />
                    <input
                      value={profile.nom}
                      onChange={(e) => update("nom", e.target.value)}
                      placeholder="Votre nom"
                    />
                  </div>
                </div>

                <div className="profile-field">
                  <label>Email</label>
                  <div className="profile-input">
                    <Mail size={16} />
                    <input
                      type="email"
                      value={profile.email}
                      onChange={(e) => update("email", e.target.value)}
                      placeholder="email@exemple.com"
                    />
                  </div>
                </div>

                <div className="profile-field">
                  <label>Téléphone</label>
                  <div className="profile-input">
                    <Phone size={16} />
                    <input
                      value={profile.telephone}
                      onChange={(e) => update("telephone", e.target.value)}
                      placeholder="+261 34 00 000 00"
                    />
                  </div>
                </div>

                <div className="profile-field">
                  <label>Ville</label>
                  <div className="profile-input">
                    <MapPin size={16} />
                    <input
                      value={profile.ville}
                      onChange={(e) => update("ville", e.target.value)}
                      placeholder="Votre ville"
                    />
                  </div>
                </div>

                <div className="profile-field">
                  <label>Série baccalauréat</label>
                  <div className="profile-input">
                    <GraduationCap size={16} />
                    <select
                      value={profile.serie}
                      onChange={(e) => update("serie", e.target.value)}
                    >
                      <option value="D">Série D</option>
                      <option value="C">Série C</option>
                      <option value="A">Série A</option>
                      <option value="S">Série S</option>
                      <option value="ES">Série ES</option>
                      <option value="L">Série L</option>
                    </select>
                  </div>
                </div>

                <div className="profile-field">
                  <label>Année d'obtention</label>
                  <div className="profile-input">
                    <Calendar size={16} />
                    <select
                      value={profile.annee}
                      onChange={(e) => update("annee", e.target.value)}
                    >
                      <option value="2026">2026</option>
                      <option value="2025">2025</option>
                      <option value="2024">2024</option>
                      <option value="2023">2023</option>
                      <option value="2022">2022</option>
                    </select>
                  </div>
                </div>

                <div className="profile-field full-width">
                  <label>Bio</label>
                  <div className="profile-input">
                    <input
                      value={profile.bio}
                      onChange={(e) => update("bio", e.target.value)}
                      placeholder="Décrivez-vous en quelques mots..."
                      className="profile-bio-input"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* SECTION 2 : CENTRES D'INTÉRÊT */}
            <div className="profile-section">
              <div className="profile-section-header">
                <div className="profile-section-icon">
                  <Heart size={20} />
                </div>
                <div>
                  <h3>
                    Centres d'intérêt{" "}
                    <span className="optional">(Optionnel)</span>
                  </h3>
                  <p>Ce qui vous passionne et vous motive</p>
                </div>
              </div>

              <div className="profile-tags">
                {[
                  { label: "Résoudre des problèmes", icon: Brain },
                  { label: "Créer & imaginer", icon: Sparkles },
                  { label: "Comprendre le monde", icon: Globe },
                  { label: "Travailler en équipe", icon: Users },
                  { label: "Analyser des données", icon: Target },
                  { label: "Construire des projets", icon: Briefcase },
                  { label: "Aider les autres", icon: Heart },
                  { label: "Voyager & découvrir", icon: MapPin },
                  { label: "Innover & expérimenter", icon: Zap },
                ].map(({ label, icon: Icon }) => (
                  <button
                    type="button"
                    key={label}
                    onClick={() => toggleInterest(label)}
                    className={`profile-tag ${selectedInterests.includes(label) ? "selected" : ""}`}
                  >
                    <Icon size={14} />
                    <span>{label}</span>
                    {selectedInterests.includes(label) && (
                      <Check size={14} className="tag-check" />
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* SECTION 3 : MATIÈRES PRÉFÉRÉES */}
            <div className="profile-section">
              <div className="profile-section-header">
                <div className="profile-section-icon">
                  <BookOpen size={20} />
                </div>
                <div>
                  <h3>Matières préférées</h3>
                  <p>Sélectionnez au moins 2 matières</p>
                </div>
              </div>

              <div className="profile-tags">
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
                    className={`profile-tag ${selectedSubjects.includes(x) ? "selected" : ""}`}
                  >
                    <span>{x}</span>
                    {selectedSubjects.includes(x) && (
                      <Check size={14} className="tag-check" />
                    )}
                  </button>
                ))}
              </div>
              <div className="profile-selection-count">
                {selectedSubjects.length} matière
                {selectedSubjects.length > 1 ? "s" : ""} sélectionnée
                {selectedSubjects.length > 1 ? "s" : ""} (minimum 2)
              </div>
            </div>

            {/* SECTION 4 : COMPÉTENCES */}
            <div className="profile-section">
              <div className="profile-section-header">
                <div className="profile-section-icon">
                  <Award size={20} />
                </div>
                <div>
                  <h3>Compétences</h3>
                  <p>Sélectionnez au moins 2 compétences</p>
                </div>
              </div>

              <div className="profile-tags">
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
                    className={`profile-tag ${selectedSkills.includes(x) ? "selected" : ""}`}
                  >
                    <span>{x}</span>
                    {selectedSkills.includes(x) && (
                      <Check size={14} className="tag-check" />
                    )}
                  </button>
                ))}
              </div>
              <div className="profile-selection-count">
                {selectedSkills.length} compétence
                {selectedSkills.length > 1 ? "s" : ""} sélectionnée
                {selectedSkills.length > 1 ? "s" : ""} (minimum 2)
              </div>
            </div>

            {/* BOUTON MOBILE */}
            <div className="profile-mobile-save">
              <button onClick={saveProfile} className="profile-save-full">
                <Save size={18} /> Enregistrer mon profil
              </button>
            </div>
          </div>

          {/* SIDEBAR */}
          <div className="profile-sidebar">
            <div className="profile-sidebar-card">
              <div className="profile-sidebar-completion">
                <div className="profile-sidebar-ring">
                  <svg viewBox="0 0 120 120">
                    <circle
                      cx="60"
                      cy="60"
                      r="50"
                      fill="none"
                      stroke="var(--muted)"
                      strokeWidth="10"
                    />
                    <circle
                      cx="60"
                      cy="60"
                      r="50"
                      fill="none"
                      stroke="url(#profileGradient)"
                      strokeWidth="10"
                      strokeDasharray={`${completionPercentage * 3.14} 314`}
                      strokeLinecap="round"
                      transform="rotate(-90 60 60)"
                    />
                    <defs>
                      <linearGradient
                        id="profileGradient"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="0%"
                      >
                        <stop offset="0%" stopColor="#6C63FF" />
                        <stop offset="100%" stopColor="#FF6584" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="profile-sidebar-ring-value">
                    <span>{completionPercentage}%</span>
                    <small>Complété</small>
                  </div>
                </div>
              </div>

              <div className="profile-sidebar-progress">
                <div className="profile-sidebar-item completed">
                  <Check size={16} />
                  <span>Informations personnelles</span>
                  <Badge label="OK" tone="green" />
                </div>
                <div
                  className={`profile-sidebar-item ${selectedSubjects.length >= 2 ? "completed" : "pending"}`}
                >
                  {selectedSubjects.length >= 2 ? (
                    <Check size={16} />
                  ) : (
                    <span className="dot" />
                  )}
                  <span>Matières préférées</span>
                  <Badge
                    label={
                      selectedSubjects.length >= 2
                        ? "OK"
                        : `${selectedSubjects.length}/2`
                    }
                    tone={selectedSubjects.length >= 2 ? "green" : "yellow"}
                  />
                </div>
                <div
                  className={`profile-sidebar-item ${selectedSkills.length >= 2 ? "completed" : "pending"}`}
                >
                  {selectedSkills.length >= 2 ? (
                    <Check size={16} />
                  ) : (
                    <span className="dot" />
                  )}
                  <span>Compétences</span>
                  <Badge
                    label={
                      selectedSkills.length >= 2
                        ? "OK"
                        : `${selectedSkills.length}/2`
                    }
                    tone={selectedSkills.length >= 2 ? "green" : "yellow"}
                  />
                </div>
                <div
                  className={`profile-sidebar-item ${selectedInterests.length > 0 ? "completed" : "pending"}`}
                >
                  {selectedInterests.length > 0 ? (
                    <Check size={16} />
                  ) : (
                    <span className="dot" />
                  )}
                  <span>Centres d'intérêt</span>
                  <Badge
                    label={selectedInterests.length > 0 ? "OK" : "Optionnel"}
                    tone={selectedInterests.length > 0 ? "green" : "yellow"}
                  />
                </div>
              </div>

              {isComplete && (
                <div className="profile-sidebar-success">
                  <Check size={20} />
                  <span>Profil complet !</span>
                  <p>
                    Vous êtes prêt à recevoir des recommandations
                    personnalisées.
                  </p>
                </div>
              )}

              {!isComplete && (
                <div className="profile-sidebar-tip">
                  <Sparkles size={18} />
                  <div>
                    <strong>Complétez votre profil</strong>
                    <p>
                      Plus votre profil est complet, plus les recommandations
                      seront précises.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
