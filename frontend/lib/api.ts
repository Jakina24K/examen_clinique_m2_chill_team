const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000";

export type LoginResponse = {
  token: string;
  token_type: string;
  role: string;
};

export type RegisterResponse = {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  role: string;
};

async function getApiError(response: Response, fallback: string) {
  try {
    const body = await response.json();
    return typeof body.detail === "string" ? body.detail : fallback;
  } catch {
    return fallback;
  }
}

async function request<T>(
  path: string,
  body: Record<string, string>,
  fallback: string,
): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 10000);

  try {
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(await getApiError(response, fallback));
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Le serveur ne répond pas. Vérifie qu'il est démarré.");
    }
    if (error instanceof TypeError) {
      throw new Error("Le serveur est momentanément indisponible.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function login(email: string, password: string) {
  return request<LoginResponse>(
    "/api/auth/login",
    { email, mot_de_passe: password },
    "Impossible de se connecter.",
  );
}

export function register(
  nom: string,
  prenom: string,
  email: string,
  password: string,
) {
  return request<RegisterResponse>(
    "/api/auth/register",
    { nom, prenom, email, mot_de_passe: password },
    "Impossible de créer le compte.",
  );
}
