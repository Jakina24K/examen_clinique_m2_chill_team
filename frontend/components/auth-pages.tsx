"use client";

import { FormEvent, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  UserRound,
} from "lucide-react";

type AuthMode = "login" | "register";

// ===== AUTH SHELL =====
function AuthShell({
  mode,
  children,
}: {
  mode: AuthMode;
  children: React.ReactNode;
}) {
  return (
    <main className="auth-page">
      <div className="auth-decoration auth-decoration-left" />
      <div className="auth-decoration auth-decoration-right" />
      <section className="auth-card">
        <a href="/" className="auth-brand">
          <span className="brand-mark">
            <span>O</span>
            <span>IA</span>
          </span>
          <span>
            <strong>ORIENT'IA</strong>
            <small>Par ISPM</small>
          </span>
        </a>
        <div className="auth-intro">
          <span className="auth-kicker">
            {mode === "login" ? "RAVI DE TE REVOIR" : "TON AVENIR COMMENCE ICI"}
          </span>
          <h1>
            {mode === "login" ? "Content de te revoir." : "Créons ton compte."}
          </h1>
          <p>
            {mode === "login"
              ? "Retrouve ton espace d'orientation et continue à construire ton projet."
              : "Quelques informations pour personnaliser ton parcours avec ORIENT'IA."}
          </p>
        </div>
        {children}
        <p className="auth-legal">
          En continuant, tu acceptes les conditions d'utilisation et la
          politique de confidentialité d'ORIENT'IA.
        </p>
      </section>
    </main>
  );
}

// ===== FIELD =====
function Field({
  label,
  name,
  type = "text",
  value,
  onChange,
  error,
  placeholder,
  autoComplete,
}: {
  label: string;
  name: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  placeholder?: string;
  autoComplete?: string;
}) {
  const [visible, setVisible] = useState(false);
  const isPassword = type === "password";

  return (
    <label className="auth-field" htmlFor={name}>
      <span>{label}</span>
      <div className="auth-control">
        <span className="auth-field-icon">
          {isPassword ? (
            <LockKeyhole size={16} />
          ) : name === "email" ? (
            <Mail size={16} />
          ) : (
            <UserRound size={16} />
          )}
        </span>
        <input
          id={name}
          name={name}
          type={isPassword && visible ? "text" : type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          aria-invalid={Boolean(error)}
        />
        {isPassword && (
          <button
            type="button"
            className="password-toggle"
            onClick={() => setVisible(!visible)}
            aria-label={
              visible ? "Masquer le mot de passe" : "Afficher le mot de passe"
            }
          >
            {visible ? <EyeOff size={16} /> : <Eye size={16} />}
          </button>
        )}
      </div>
      {error && <small className="auth-error">{error}</small>}
    </label>
  );
}

// ===== LOGIN PAGE =====
export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const next: Record<string, string> = {};
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
      next.email = "Saisis une adresse e-mail valide.";
    if (!password) next.password = "Le mot de passe est obligatoire.";
    setErrors(next);
    if (Object.keys(next).length) return;
    setLoading(true);

    setTimeout(() => {
      window.localStorage.setItem("user_token", "fake-jwt-token");
      window.localStorage.setItem(
        "orientia_user",
        JSON.stringify({ name: "Aina M.", email }),
      );
      // Redirection vers dashboard
      window.location.href = "/dashboard";
    }, 650);
  };

  const goToRegister = (e: React.MouseEvent) => {
    e.preventDefault();
    window.location.href = "/register";
  };

  return (
    <AuthShell mode="login">
      <form className="auth-form" onSubmit={submit} noValidate>
        <Field
          label="Adresse e-mail"
          name="email"
          type="email"
          value={email}
          onChange={setEmail}
          error={errors.email}
          placeholder="toi@exemple.com"
          autoComplete="email"
        />
        <Field
          label="Mot de passe"
          name="password"
          type="password"
          value={password}
          onChange={setPassword}
          error={errors.password}
          placeholder="••••••••"
          autoComplete="current-password"
        />
        <a className="forgot-link" href="#forgot">
          Mot de passe oublié ?
        </a>
        <button className="auth-submit" disabled={loading}>
          {loading ? "Connexion en cours…" : "Se connecter"}
          {!loading && <ArrowRight size={16} />}
        </button>
      </form>
      <p className="auth-switch">
        Pas encore de compte ?{" "}
        <a href="#" onClick={goToRegister}>
          Créer un compte
        </a>
      </p>
    </AuthShell>
  );
}

// ===== REGISTER PAGE =====
export function RegisterPage() {
  const [values, setValues] = useState({
    nom: "",
    prenom: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const update = (name: keyof typeof values) => (value: string) =>
    setValues((current) => ({ ...current, [name]: value }));

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const next: Record<string, string> = {};
    if (!values.nom) next.nom = "Le nom est obligatoire.";
    if (!values.prenom) next.prenom = "Le prénom est obligatoire.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email))
      next.email = "Saisis une adresse e-mail valide.";
    if (values.password.length < 8)
      next.password = "Le mot de passe doit contenir au moins 8 caractères.";
    if (values.confirm_password !== values.password)
      next.confirm_password = "Les mots de passe ne correspondent pas.";
    setErrors(next);
    if (Object.keys(next).length) return;
    setLoading(true);

    setTimeout(() => {
      window.localStorage.setItem("user_token", "fake-jwt-token");
      window.localStorage.setItem(
        "orientia_user",
        JSON.stringify({
          nom: values.nom,
          prenom: values.prenom,
          email: values.email,
        }),
      );
      // Redirection vers dashboard
      window.location.href = "/dashboard";
    }, 650);
  };

  const goToLogin = (e: React.MouseEvent) => {
    e.preventDefault();
    window.location.href = "/login";
  };

  return (
    <AuthShell mode="register">
      <form className="auth-form register-form" onSubmit={submit} noValidate>
        <div className="auth-form-row">
          <Field
            label="Nom"
            name="nom"
            value={values.nom}
            onChange={update("nom")}
            error={errors.nom}
            placeholder="Rakoto"
            autoComplete="family-name"
          />
          <Field
            label="Prénom"
            name="prenom"
            value={values.prenom}
            onChange={update("prenom")}
            error={errors.prenom}
            placeholder="Aina"
            autoComplete="given-name"
          />
        </div>
        <Field
          label="Adresse e-mail"
          name="email"
          type="email"
          value={values.email}
          onChange={update("email")}
          error={errors.email}
          placeholder="toi@exemple.com"
          autoComplete="email"
        />
        <Field
          label="Mot de passe"
          name="password"
          type="password"
          value={values.password}
          onChange={update("password")}
          error={errors.password}
          placeholder="8 caractères minimum"
          autoComplete="new-password"
        />
        <Field
          label="Confirmer le mot de passe"
          name="confirm_password"
          type="password"
          value={values.confirm_password}
          onChange={update("confirm_password")}
          error={errors.confirm_password}
          placeholder="Retape ton mot de passe"
          autoComplete="new-password"
        />
        <button className="auth-submit" disabled={loading}>
          {loading ? "Création en cours…" : "Créer mon compte"}
          {!loading && <ArrowRight size={16} />}
        </button>
      </form>
      <p className="auth-switch">
        Déjà un compte ?{" "}
        <a href="#" onClick={goToLogin}>
          Se connecter
        </a>
      </p>
    </AuthShell>
  );
}
