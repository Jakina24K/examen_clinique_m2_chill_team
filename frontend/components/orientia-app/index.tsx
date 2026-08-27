"use client";

import { useEffect, useState } from "react";
import gsap from "gsap";
import { Landing } from "./Landing";
import { Sidebar } from "./Sidebar";
import { Dashboard } from "./Dashboard";
import { Assistant } from "./Assistant";
import { Explorer } from "./Explorer";
import { Profile } from "./Profile";
import { LoginPage, RegisterPage } from "@/components/auth-pages";

export default function OrientiaApp() {
  const [started, setStarted] = useState(false);
  const [view, setView] = useState("dashboard");
  const [ready, setReady] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register" | null>(null);

  useEffect(() => {
    const path = window.location.pathname;
    const token = window.localStorage.getItem("user_token");

    // Gestion des pages d'authentification via l'URL
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

    // Gestion des pages protégées
    if (
      path === "/dashboard" ||
      path === "/assistant" ||
      path === "/explorer" ||
      path === "/profile"
    ) {
      if (!token) {
        // Rediriger vers login
        window.location.href = "/login";
        return;
      }
      setView(path.slice(1));
      setStarted(true);
    }
    setReady(true);
  }, []);

  // Écouteur d'événements pour la navigation interne (login <-> register)
  useEffect(() => {
    const handleNavigate = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail === "login") {
        window.location.href = "/login";
      } else if (customEvent.detail === "register") {
        window.location.href = "/register";
      }
    };

    window.addEventListener("navigate", handleNavigate as EventListener);

    return () => {
      window.removeEventListener("navigate", handleNavigate as EventListener);
    };
  }, []);

  useEffect(() => {
    if (
      !started ||
      !ready ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    )
      return;

    const ctx = gsap.context(() => {
      gsap.from(".dashboard-content > *, .assistant-page > *, .sidebar > *", {
        y: 16,
        opacity: 0,
        duration: 0.55,
        stagger: 0.07,
        ease: "power2.out",
      });
      gsap.from(".panel, .formation-card, .message-row, .recommendation", {
        y: 18,
        opacity: 0,
        scale: 0.985,
        duration: 0.5,
        stagger: 0.08,
        delay: 0.18,
        ease: "power2.out",
      });
      gsap.to(".assistant-glow", {
        scale: 1.08,
        duration: 1.8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(".pulse", {
        scale: 1.25,
        opacity: 0.6,
        duration: 1.2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
    });

    return () => ctx.revert();
  }, [started, ready, view]);

  const navigate = (next: string) => {
    setView(next);
    setStarted(true);
    window.history.pushState({}, "", `/${next}`);
  };

  const logout = () => {
    window.localStorage.removeItem("user_token");
    window.localStorage.removeItem("orientia_user");
    window.location.href = "/login";
  };

  const goToLogin = () => {
    window.location.href = "/login";
  };

  if (!ready) return null;

  // Affichage des pages d'authentification
  if (authMode === "login") {
    return <LoginPage />;
  }
  if (authMode === "register") {
    return <RegisterPage />;
  }

  if (!started) {
    return <Landing onStart={goToLogin} />;
  }

  return (
    <div className="app-shell">
      <Sidebar view={view} setView={navigate} onLogout={logout} />
      <main className="main-area">
        {view === "dashboard" && <Dashboard setView={navigate} />}
        {view === "assistant" && <Assistant />}
        {view === "explorer" && <Explorer setView={navigate} />}
        {view === "profile" && <Profile setView={navigate} />}
      </main>
    </div>
  );
}
