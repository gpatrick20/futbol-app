import { useState } from "react";
import type { FormEvent } from "react";

import { getCurrentUser, login } from "./services/api";
import type { User } from "./services/api";

export default function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const token = await login(email.trim(), password);
      const currentUser = await getCurrentUser(token.access_token);

      setUser(currentUser);
      setPassword("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo iniciar sesión.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    setUser(null);
    setPassword("");
    setError("");
  }

  return (
    <main
      style={{
        maxWidth: 440,
        margin: "64px auto",
        padding: 24,
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1>futbol-app</h1>
      <p>Organiza partidos de fútbol con tu grupo.</p>

      {user ? (
        <section>
          <h2>Bienvenido, {user.full_name}</h2>
          <p>Email: {user.email}</p>
          <p>Rol: {user.role}</p>
          <p>Posición: {user.position ?? "Sin indicar"}</p>

          <button type="button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </section>
      ) : (
        <form
          onSubmit={handleLogin}
          style={{ display: "grid", gap: 16 }}
        >
          <h2>Iniciar sesión</h2>

          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={loading}
            required
          />

          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={loading}
            required
          />

          {error && (
            <p role="alert" style={{ color: "#b91c1c" }}>
              {error}
            </p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Ingresando..." : "Ingresar"}
          </button>
        </form>
      )}
    </main>
  );
}
