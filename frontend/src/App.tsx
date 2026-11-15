import { useState } from "react";
import type { User } from "./services/api";
import AuthForm from "./components/auth/AuthForm";
import Button from "./components/ui/Button";
import Card from "./components/ui/Card";

export default function App() {
  const [user, setUser] = useState<User | null>(null);

  return (
    <main style={{ maxWidth: 440, margin: "48px auto", padding: 24 }}>
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
            <Button variant="secondary" onClick={() => setUser(null)}>
              Cerrar sesión
            </Button>
          </section>
        ) : (
          <AuthForm onAuthenticated={setUser} />
        )}
      </Card>
    </main>
  );
}
