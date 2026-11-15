const API_URL = "http://localhost:8000";


export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const SESSION_EXPIRED_EVENT = "futbol:session-expired";

async function protectedRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
  });

  if (response.status === 401) {
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
  }

  return readResponse<T>(response);
}

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
      // Conservamos el mensaje HTTP si no hay una respuesta JSON.
    }

    throw new ApiError(message, response.status);
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
  credentials: "include",
  headers: {
    "Content-Type": "application/x-www-form-urlencoded",
  },
  body,
  });

  return readResponse<TokenResponse>(response);
}

export async function getCurrentUser(): Promise<User> {
  return protectedRequest<User>("/auth/me", {
    cache: "no-store",
  });
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role: "leader" | "player";
  commune: string | null;
  position: string | null;
}

export async function register(data: RegisterData): Promise<User> {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  return readResponse<User>(response);
}

export async function logout(): Promise<void> {
  const response = await fetch(`${API_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });

  await readResponse<{ message: string }>(response);
}