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

type ProtectedRequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

async function protectedRequest<T>(
  path: string,
  options: ProtectedRequestOptions = {},
): Promise<T> {
  const { body, ...restOptions } = options;

  const headers = new Headers(restOptions.headers);

  if (body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...restOptions,
    headers,
    credentials: "include",
    body:
      body === undefined
        ? undefined
        : JSON.stringify(body),
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
export type Match = {
  id: string;
  created_by: string;
  format: "futbol5" | "futbol7" | "futbol11";
  venue_name: string;
  address: string | null;
  commune: string | null;
  match_date: string | null;
  start_time: string | null;
  status:
    | "proposed"
    | "voting"
    | "confirmed"
    | "full"
    | "cancelled"
    | "played";
  total_cost: string | null;
  min_players: number;
  max_players: number;
  created_at: string;
};

export type MatchCreateData = {
  format: "futbol5" | "futbol7" | "futbol11";
  venue_name: string;
  address?: string | null;
  commune?: string | null;
  match_date?: string | null;
  start_time?: string | null;
  total_cost?: string | number | null;
  min_players: number;
  max_players: number;
};

export type MatchParticipant = {
  id: string;
  match_id: string;
  user_id: string;
  status:
    | "invited"
    | "confirmed"
    | "tentative"
    | "absent"
    | "substitute";
  joined_at: string;
};

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

export async function getMatches(): Promise<Match[]> {
  return protectedRequest<Match[]>("/matches", {
    method: "GET",
  });
}

export async function getOrganizedMatches(): Promise<Match[]> {
  return protectedRequest<Match[]>("/matches/organized", {
    method: "GET",
  });
}


export async function getParticipatingMatches(): Promise<Match[]> {
  return protectedRequest<Match[]>("/matches/participating", {
    method: "GET",
  });
}

export async function getAvailableMatches(): Promise<Match[]> {
  return protectedRequest<Match[]>("/matches/available", {
    method: "GET",
  });
}

export async function joinMatch(
  matchId: string,
): Promise<MatchParticipant> {
  return protectedRequest<MatchParticipant>(
    `/matches/${matchId}/participants`,
    {
      method: "POST",
    },
  );
}

export async function createMatch(
  matchData: MatchCreateData,
): Promise<Match> {
  return protectedRequest<Match>("/matches", {
    method: "POST",
    body: matchData,
  });
}