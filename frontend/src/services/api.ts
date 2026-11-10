const API_URL = "http://127.0.0.1:8000";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "leader" | "player";
  commune: string | null;
  position: string | null;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

async function readResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `Error HTTP ${response.status}`;

    try {
      const body = await response.json();

      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        message = "Revisa los datos ingresados.";
      }
    } catch {
      // Mantener el mensaje HTTP cuando no hay un cuerpo JSON.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function login(
  email: string,
  password: string,
): Promise<TokenResponse> {
  const body = new URLSearchParams({
    username: email,
    password,
  });

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body,
  });

  return readResponse<TokenResponse>(response);
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return readResponse<User>(response);
}