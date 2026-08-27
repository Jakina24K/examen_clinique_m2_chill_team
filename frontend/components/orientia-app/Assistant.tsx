import { useState } from "react";
import { ArrowRight, Bot, FileText, Send, Sparkles } from "lucide-react";
import { Badge } from "./Badge";
import { suggestions } from "./data/formations";

export function Assistant() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Bonjour Aina ! Je suis ORIENT'IA, ton assistant d'orientation. Je peux t'aider à explorer les formations ISPM et à mieux comprendre ce qui te correspond.",
      time: "10:42",
    },
    {
      role: "user",
      text: "Quelles formations correspondent à mon profil scientifique ?",
      time: "10:43",
    },
    {
      role: "assistant",
      text: "Avec ton profil en série D et ton intérêt pour les sciences, deux parcours semblent particulièrement intéressants. Voici ce que j'ai trouvé :",
      time: "10:43",
      card: true,
    },
  ]);
  const [input, setInput] = useState("");

  const send = (value = input) => {
    if (!value.trim()) return;
    setMessages((m) => [...m, { role: "user", text: value, time: "10:44" }]);
    setInput("");
    setTimeout(
      () =>
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            text: "Très bonne question. Je vais croiser ton profil avec les informations officielles des parcours pour te donner une réponse claire et vérifiable.",
            time: "10:44",
          },
        ]),
      350,
    );
  };

  return (
    <div className="assistant-page">
      <div className="assistant-top">
        <div>
          <span className="breadcrumb">Mon espace / Mon assistant</span>
          <h1>Ton espace de réflexion</h1>
        </div>
        <div className="source-status">
          <span /> Réponses sourcées · IAISPM v1.4
        </div>
      </div>
      <div className="chat-shell">
        <div className="chat-header">
          <div className="assistant-avatar">
            <Bot size={19} />
          </div>
          <div>
            <strong>ORIENT'IA</strong>
            <span>
              Assistant d'orientation ISPM <i />
            </span>
          </div>
          <button className="icon-button">
            <FileText size={18} />
          </button>
        </div>
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`message-row ${m.role}`}>
              <div className={`message-avatar ${m.role}`}>
                {m.role === "assistant" ? <Bot size={16} /> : "AM"}
              </div>
              <div className="message-wrap">
                <div className="message-bubble">{m.text}</div>
                {m.card && (
                  <div className="recommendation">
                    <div className="rec-head">
                      <div>
                        <Badge label="RECOMMANDÉ POUR TOI" tone="green" />
                        <h3>
                          ISAIA <span>·</span> Intelligence & Systèmes
                          d'Information Avancés
                        </h3>
                      </div>
                      <strong>92%</strong>
                    </div>
                    <p>
                      Un parcours au croisement de la data, de l'intelligence
                      artificielle et de la décision.
                    </p>
                    <div className="rec-bars">
                      <div>
                        <span>Ton profil</span>
                        <i>
                          <b style={{ width: "92%" }} />
                        </i>
                        <strong>92</strong>
                      </div>
                      <div>
                        <span>Prérequis</span>
                        <i>
                          <b style={{ width: "78%" }} />
                        </i>
                        <strong>78</strong>
                      </div>
                      <div>
                        <span>Débouchés</span>
                        <i>
                          <b style={{ width: "88%" }} />
                        </i>
                        <strong>88</strong>
                      </div>
                    </div>
                    <button>
                      Voir la fiche formation <ArrowRight size={14} />
                    </button>
                  </div>
                )}
                <small>{m.time}</small>
              </div>
            </div>
          ))}
        </div>
        <div className="suggestion-row">
          {suggestions.map((s) => (
            <button key={s} onClick={() => send(s)}>
              <Sparkles size={13} /> {s}
            </button>
          ))}
        </div>
        <div className="composer">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (
                e.key === "Enter" &&
                !e.nativeEvent.isComposing &&
                e.keyCode !== 229
              )
                send();
            }}
            placeholder="Pose ta question à ORIENT'IA..."
            aria-label="Votre question"
          />
          <button onClick={() => send()} aria-label="Envoyer">
            <Send size={18} />
          </button>
        </div>
        <p className="chat-disclaimer">
          ORIENT'IA est un outil d'aide à l'orientation. Ses réponses ne
          remplacent pas l'avis d'un conseiller pédagogique.
        </p>
      </div>
    </div>
  );
}
