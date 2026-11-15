import { useEffect, useState } from "react";

import { ApiError, getCurrentUser, logout } from "./services/api";
import type { User } from "./services/api";

import AuthForm from "./components/auth/AuthForm";
import Alert from "./components/ui/Alert";
import Button from "./components/ui/Button";
import Card from "./components/ui/Card";

export default function App() {
  const [user, setUser] = useState<User | null>(null);

  const [checkingSession, setCheckingSession] = useState(true);
  const [sessionError, setSessionError] = useState("");
  const [sessionAttempt, setSessionAttempt] = useState(0);

  const [loggingOut, setLoggingOut] = useState(false);
  const [logoutError, setLogoutError] = useState("");

  useEffect(() => {
    let ignore = false;

    async function restoreSession() {
      setCheckingSession(true);
      setSessionError("");

      try {
        const currentUser = await getCurrentUser();

        if (!ignore) {
          setUser(currentUser);
        }
      } catch (err) {
        if (ignore) {
          return;
        }

        if (err instanceof ApiError && err.status === 401) {
          setUser(null);
        } else {
          setSessionError(
            "No pudimos comprobar tu sesión. Verifica la conexión y vuelve a intentar.",
          );
        }
      } finally {
        if (!ignore) {
          setCheckingSession(false);
        }
      }
    }

    void restoreSession();

    return () => {
      ignore = true;
    };
  }, [sessionAttempt]);

  function retrySession() {
    setCheckingSession(true);
    setSessionError("");
    setSessionAttempt((current) => current + 1);
  }

  async function handleLogout() {
    setLoggingOut(true);
    setLogoutError("");

    try {
      await logout();
      setUser(null);
    } catch {
      setLogoutError(
        "No se pudo cerrar la sesión en el servidor. Vuelve a intentarlo.",
      );
    } finally {
      setLoggingOut(false);
    }
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

        {checkingSession ? (
          <p role="status">Comprobando sesión...</p>
        ) : sessionError ? (
          <div style={{ display: "grid", gap: 16 }}>
            <Alert variant="error">{sessionError}</Alert>

            <Button onClick={retrySession} fullWidth>
              Reintentar
            </Button>
          </div>
        ) : user ? (
          <section>
            <h2>Bienvenido, {user.full_name}</h2>

            <p>Email: {user.email}</p>
            <p>Rol: {user.role}</p>
            <p>Comuna: {user.commune ?? "Sin indicar"}</p>
            <p>Posición: {user.position ?? "Sin indicar"}</p>

            <div style={{ display: "grid", gap: 16 }}>
              {logoutError && (
                <Alert variant="error">{logoutError}</Alert>
              )}

              <Button
                variant="secondary"
                onClick={handleLogout}
                loading={loggingOut}
                loadingText="Cerrando sesión..."
              >
                Cerrar sesión
              </Button>
            </div>
          </section>
        ) : (
          <AuthForm onAuthenticated={setUser} />
        )}
      </Card>
    </main>
  );
}
