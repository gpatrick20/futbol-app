import { useState } from "react";
import type { FormEvent } from "react";

import { getCurrentUser, login, register } from "./services/api";
import type { User } from "./services/api";

import Button from "./components/ui/Button";
import Card from "./components/ui/Card";
import Input from "./components/ui/Input";

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
      }}
    >
      <Card>
        <h1>futbol-app</h1>
        <p>Organiza partidos de fútbol con tu grupo.</p>

        {user ? (
          <section>
            <h2>Bienvenido, {user.full_name}</h2>
            <p>Email: {user.email}</p>
            <p>Rol: {user.role}</p>
            <p>Comuna: {user.commune ?? "Sin indicar"}</p>
            <p>Posición: {user.position ?? "Sin indicar"}</p>

            <Button variant="secondary" onClick={handleLogout}>
              Cerrar sesión
            </Button>
          </section>
        ) : (
          <>
            <h2>
              {mode === "login" ? "Iniciar sesión" : "Crear cuenta"}
            </h2>

            <form
              onSubmit={handleSubmit}
              style={{ display: "grid", gap: 16 }}
            >
              {mode === "register" && (
                <Input
                  id="full-name"
                  label="Nombre completo"
                  autoComplete="name"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  maxLength={120}
                  disabled={loading}
                  required
                />
              )}

              <Input
                id="email"
                label="Email"
                type="email"
                autoComplete="username"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                maxLength={255}
                disabled={loading}
                required
              />

              <Input
                id="password"
                label="Contraseña"
                type="password"
                autoComplete={
                  mode === "register" ? "new-password" : "current-password"
                }
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={mode === "register" ? 8 : undefined}
                hint={
                  mode === "register"
                    ? "Usa al menos 8 caracteres."
                    : undefined
                }
                disabled={loading}
                required
              />

              {mode === "register" && (
                <>
                  <div style={{ display: "grid", gap: 6 }}>
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
                  </div>

                  <Input
                    id="commune"
                    label="Comuna (opcional)"
                    value={commune}
                    onChange={(event) => setCommune(event.target.value)}
                    maxLength={100}
                    disabled={loading}
                  />

                  <Input
                    id="position"
                    label="Posición (opcional)"
                    value={position}
                    onChange={(event) => setPosition(event.target.value)}
                    maxLength={50}
                    disabled={loading}
                  />
                </>
              )}

              {error && (
                <p role="alert" style={{ color: "var(--color-danger)" }}>
                  {error}
                </p>
              )}

              {message && (
                <p role="status" style={{ color: "var(--color-success)" }}>
                  {message}
                </p>
              )}

              <Button
                type="submit"
                fullWidth
                loading={loading}
                loadingText={
                  mode === "login" ? "Ingresando..." : "Creando cuenta..."
                }
              >
                {mode === "login" ? "Ingresar" : "Crear cuenta"}
              </Button>
            </form>

            <Button
              variant="secondary"
              onClick={switchMode}
              disabled={loading}
              fullWidth
              style={{ marginTop: 16 }}
            >
              {mode === "login"
                ? "No tengo cuenta: registrarme"
                : "Ya tengo cuenta: iniciar sesión"}
            </Button>
          </>
        )}
      </Card>
    </main>
  );
}