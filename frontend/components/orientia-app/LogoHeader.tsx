"use client";

import { ArrowRight, ExternalLink } from "lucide-react";
import { Brand } from "./Brand";
import { Button } from "./Button";

export function LogoHeader({ onLogin }: { onLogin: () => void }) {
  return (
    <header className="public-header">
      <Brand />
      <nav>
        <a href="#about">Comment ça marche</a>
        <a href="#trust">Traçabilité</a>
        <a href="https://ispm-edu.com/" target="_blank">
          ISPM <ExternalLink size={13} />
        </a>
      </nav>
      <Button variant="outline" onClick={onLogin}>
        Se connecter <ArrowRight size={16} />
      </Button>
    </header>
  );
}
