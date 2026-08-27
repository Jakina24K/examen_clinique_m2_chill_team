"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import {
  ArrowRight,
  Check,
  ChevronRight,
  MessageCircle,
  ExternalLink,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { LogoHeader } from "./LogoHeader";
import { Button } from "./Button";

export function Landing({ onStart }: { onStart: () => void }) {
  const landingRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = landingRef.current;
    if (!root) return;
    const ctx = gsap.context(() => {
      const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;
      if (prefersReducedMotion) return;

      const intro = gsap.timeline({ defaults: { ease: "power3.out" } });
      intro
        .from(".public-header", { y: -18, opacity: 0, duration: 0.7 })
        .from(
          ".hero-copy > *",
          { y: 22, opacity: 0, duration: 0.65, stagger: 0.09 },
          "-=0.35",
        )
        .from(
          ".hero-visual",
          { scale: 0.92, opacity: 0, duration: 0.9 },
          "-=0.55",
        )
        .from(
          ".steps > div",
          { y: 18, opacity: 0, duration: 0.55, stagger: 0.12 },
          "-=0.45",
        );

      gsap.to(".compass", {
        rotation: 3,
        duration: 2.8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(".needle", {
        rotation: 55,
        duration: 1.8,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(".orbit-one", {
        rotation: -8,
        duration: 5,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(".orbit-two", {
        rotation: 52,
        duration: 6,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(".card-match", {
        y: -8,
        duration: 2.2,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
      });
      gsap.to(".card-source", {
        y: 7,
        duration: 2.6,
        repeat: -1,
        yoyo: true,
        ease: "sine.inOut",
        delay: 0.4,
      });

      root
        .querySelectorAll<HTMLElement>(".formation-card, .trust-strip, .button")
        .forEach((element) => {
          element.addEventListener("mouseenter", () =>
            gsap.to(element, { y: -3, duration: 0.2, ease: "power2.out" }),
          );
          element.addEventListener("mouseleave", () =>
            gsap.to(element, { y: 0, duration: 0.2, ease: "power2.out" }),
          );
        });
    }, root);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={landingRef} className="landing">
      <LogoHeader onLogin={onStart} />
      <main className="hero-wrap">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="pulse" /> L'orientation, autrement
            </div>
            <h1>
              Ton avenir mérite
              <br />
              <em>une bonne boussole.</em>
            </h1>
            <p>
              ORIENT'IA t'accompagne pour trouver la formation ISPM qui te
              ressemble. Une orientation claire, personnalisée et fondée sur des
              sources officielles.
            </p>
            <div className="hero-actions">
              <Button onClick={onStart}>
                Découvrir mon orientation <ArrowRight size={17} />
              </Button>
              <button
                className="text-button"
                onClick={() =>
                  document
                    .getElementById("about")
                    ?.scrollIntoView({ behavior: "smooth" })
                }
              >
                Comment ça marche <ChevronRight size={16} />
              </button>
            </div>
            <div className="hero-proof">
              <div className="avatars">
                <span>MA</span>
                <span>JT</span>
                <span>FN</span>
                <span>+</span>
              </div>
              <span>
                <strong>Déjà adopté par 1 200+</strong>
                <br />
                futurs étudiants ISPM
              </span>
            </div>
          </div>
          <div className="hero-visual">
            <div className="orbit orbit-one" />
            <div className="orbit orbit-two" />
            <div className="compass">
              <div className="compass-ring">
                <div className="needle">
                  <i />
                </div>
                <span className="n">N</span>
                <span className="e">E</span>
                <span className="s">S</span>
                <span className="w">O</span>
              </div>
              <div className="compass-center">
                <Sparkles size={20} />
              </div>
            </div>
            <div className="float-card card-match">
              <div className="float-icon green">
                <Check size={14} />
              </div>
              <div>
                <small>Profil analysé</small>
                <strong>Correspondance 92%</strong>
              </div>
            </div>
            <div className="float-card card-source">
              <ShieldCheck size={17} />
              <div>
                <small>Réponse traçable</small>
                <strong>12 sources officielles</strong>
              </div>
            </div>
          </div>
        </section>
        <section id="about" className="steps">
          <div>
            <span>01</span>
            <h3>Je me découvre</h3>
            <p>
              Quelques questions pour comprendre tes envies, tes forces et tes
              ambitions.
            </p>
          </div>
          <div>
            <span>02</span>
            <h3>J'explore</h3>
            <p>
              Parcours les formations ISPM et découvre les métiers qui
              t'attendent.
            </p>
          </div>
          <div>
            <span>03</span>
            <h3>Je me projette</h3>
            <p>
              Reçois des recommandations expliquées, jamais sorties de nulle
              part.
            </p>
          </div>
        </section>
        <section className="trust-strip" id="trust">
          <ShieldCheck size={21} />
          <div>
            <strong>Des réponses qui se vérifient</strong>
            <span>
              Chaque conseil est accompagné de ses sources et de son niveau de
              confiance.
            </span>
          </div>
          <a href="#sources">
            Voir notre registre des sources <ArrowRight size={14} />
          </a>
        </section>
      </main>
      <footer className="public-footer">
        <span>© 2026 ORIENT'IA · ISPM</span>
        <span>Fahaizana · Fampandrosoana · Fihavanana</span>
        <span>
          <a
            href="https://www.facebook.com/ISPM2014/?locale=fr_FR"
            target="_blank"
          >
            <MessageCircle size={15} />
          </a>
          <a href="https://ispm-edu.com/" target="_blank">
            <ExternalLink size={15} />
          </a>
        </span>
      </footer>
    </div>
  );
}
