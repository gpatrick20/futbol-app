import { useState } from "react";
import type { FormEvent } from "react";

import { getCurrentUser, login, register } from "./services/api";
import type { User } from "./services/api";

export default function App() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState<"leader" | "player">("player");
  const [commune, setCommune] = useState("");
  const [position, setPosition] = useState("");

  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  function switchMode() {
    setMode((current) => (current === "login" ? "register" : "login"));
    setPassword("");
    setError("");
    setMessage("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    try {
      if (mode === "register") {
        const name = fullName.trim();

        if (!name) {
          throw new Error("Ingresa tu nombre.");
        }

        // Límite explícito mientras el backend utiliza bcrypt.
        if (new TextEncoder().encode(password).length > 72) {
          throw new Error("La contraseña no puede superar los 72 bytes.");
        }

        await register({
          email: email.trim(),
          password,
          full_name: name,
          role,
          commune: commune.trim() || null,
          position: position.trim() || null,
        });

        setMode("login");
        setPassword("");
        setMessage("Cuenta creada correctamente. Ya puedes iniciar sesión.");
        return;
      }

      const token = await login(email.trim(), password);
      const currentUser = await getCurrentUser(token.access_token);

      setUser(currentUser);
      setPassword("");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo completar la operación.",
      );
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    setUser(null);
    setPassword("");
    setError("");
    setMessage("");
    setMode("login");
  }

  return (
    <main
      style={{
        maxWidth: 440,
        margin: "48px auto",
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
          <p>Comuna: {user.commune ?? "Sin indicar"}</p>
          <p>Posición: {user.position ?? "Sin indicar"}</p>

          <button type="button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </section>
      ) : (
        <>
          <h2>{mode === "login" ? "Iniciar sesión" : "Crear cuenta"}</h2>

          <form
            onSubmit={handleSubmit}
            style={{ display: "grid", gap: 12 }}
          >
            {mode === "register" && (
              <>
                <label htmlFor="full-name">Nombre completo</label>
                <input
                  id="full-name"
                  autoComplete="name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  maxLength={120}
                  disabled={loading}
                  required
                />
              </>
            )}

            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              maxLength={255}
              disabled={loading}
              required
            />

            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              autoComplete={
                mode === "register" ? "new-password" : "current-password"
              }
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={mode === "register" ? 8 : undefined}
              disabled={loading}
              required
            />

            {mode === "register" && (
              <>
                <label htmlFor="role">Rol</label>
                <select
                  id="role"
                  value={role}
                  onChange={(event) =>
                    setRole(event.target.value as "leader" | "player")
                  }
                  disabled={loading}
                >
                  <option value="player">Jugador</option>
                  <option value="leader">Organizador</option>
                </select>

                <label htmlFor="commune">Comuna (opcional)</label>
                <input
                  id="commune"
                  value={commune}
                  onChange={(event) => setCommune(event.target.value)}
                  maxLength={100}
                  disabled={loading}
                />

                <label htmlFor="position">Posición (opcional)</label>
                <input
                  id="position"
                  value={position}
                  onChange={(event) => setPosition(event.target.value)}
                  maxLength={50}
                  disabled={loading}
                />
              </>
            )}

            {error && (
              <p role="alert" style={{ color: "#b91c1c" }}>
                {error}
              </p>
            )}

            {message && (
              <p role="status" style={{ color: "#166534" }}>
                {message}
              </p>
            )}

            <button type="submit" disabled={loading}>
              {loading
                ? "Procesando..."
                : mode === "login"
                  ? "Ingresar"
                  : "Crear cuenta"}
            </button>
          </form>

          <button
            type="button"
            onClick={switchMode}
            disabled={loading}
            style={{ marginTop: 16 }}
          >
            {mode === "login"
              ? "No tengo cuenta: registrarme"
              : "Ya tengo cuenta: iniciar sesión"}
          </button>
        </>
      )}
    </main>
  );
}
