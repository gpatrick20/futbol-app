import { useEffect, useState } from "react";

import {
  ApiError,
  getAvailableMatches,
  getOrganizedMatches,
  getParticipatingMatches,
  joinMatch,
} from "../../services/api";
import type { Match } from "../../services/api";
import CreateMatchForm from "./CreateMatchForm";

import Alert from "../ui/Alert";
import Button from "../ui/Button";
import Card from "../ui/Card";

type MatchesPageProps = {
  onBack: () => void;
};

const STATUS_LABELS: Record<Match["status"], string> = {
  proposed: "Propuesto",
  voting: "En votación",
  confirmed: "Confirmado",
  full: "Completo",
  cancelled: "Cancelado",
  played: "Jugado",
};

const FORMAT_LABELS: Record<Match["format"], string> = {
  futbol5: "Fútbol 5",
  futbol7: "Fútbol 7",
  futbol11: "Fútbol 11",
};

export default function MatchesPage({
  onBack,
}: MatchesPageProps) {
  const [organizedMatches, setOrganizedMatches] = useState<
    Match[]
  >([]);
  const [participatingMatches, setParticipatingMatches] =
    useState<Match[]>([]);
  const [availableMatches, setAvailableMatches] = useState<
    Match[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<
    "organized" | "participating" | "available"
  >("organized");
  const [view, setView] = useState<"list" | "create">(
    "list",
  );
  const [error, setError] = useState("");
  const [joinError, setJoinError] = useState("");
  const [joiningMatchId, setJoiningMatchId] = useState<
    string | null
  >(null);
  const [reloadAttempt, setReloadAttempt] = useState(0);

  useEffect(() => {
    let ignore = false;

    async function loadMatches() {
      setLoading(true);
      setError("");
      setJoinError("");

      try {
        const [organizedData, participatingData, availableData] =
          await Promise.all([
            getOrganizedMatches(),
            getParticipatingMatches(),
            getAvailableMatches(),
          ]);

        if (!ignore) {
          setOrganizedMatches(organizedData);
          setParticipatingMatches(participatingData);
          setAvailableMatches(availableData);
        }
      } catch (err) {
        if (ignore) {
          return;
        }

        if (err instanceof ApiError && err.status === 401) {
          return;
        }

        setError(
          "No pudimos cargar tus partidos. Verifica la conexión e inténtalo otra vez.",
        );
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    void loadMatches();

    return () => {
      ignore = true;
    };
  }, [activeTab, reloadAttempt]);

  function formatMatchSchedule(match: Match) {
    if (!match.match_date) {
      return "Fecha por definir";
    }

    const dateLabel = new Date(
      `${match.match_date}T00:00:00`,
    ).toLocaleDateString("es-CL", {
      dateStyle: "medium",
    });

    if (!match.start_time) {
      return dateLabel;
    }

    const timeLabel = new Date(
      `${match.match_date}T${match.start_time}`,
    ).toLocaleTimeString("es-CL", {
      hour: "2-digit",
      minute: "2-digit",
    });

    return `${dateLabel}, ${timeLabel}`;
  }

  async function handleJoin(matchId: string) {
    if (joiningMatchId) {
      return;
    }

    setJoiningMatchId(matchId);
    setJoinError("");

    try {
      await joinMatch(matchId);
      const [participatingData, availableData] =
        await Promise.all([
          getParticipatingMatches(),
          getAvailableMatches(),
        ]);
      setParticipatingMatches(participatingData);
      setAvailableMatches(availableData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        return;
      }

      if (err instanceof ApiError) {
        setJoinError(err.message);
      } else {
        setJoinError(
          "No pudimos completar tu inscripción. Inténtalo otra vez.",
        );
      }
    } finally {
      setJoiningMatchId(null);
    }
  }

  const matches =
    activeTab === "organized"
      ? organizedMatches
      : activeTab === "participating"
        ? participatingMatches
        : availableMatches;

  if (view === "create") {
    return (
      <section
        style={{
          width: "100%",
          maxWidth: 540,
          margin: "48px auto",
          padding: "24px 16px",
        }}
      >
        <CreateMatchForm
          onCreated={() => {
            setActiveTab("organized");
            setView("list");
            setReloadAttempt((current) => current + 1);
          }}
          onCancel={() => setView("list")}
        />
      </section>
    );
  }

  return (
    <section
      style={{
        width: "100%",
        maxWidth: 1040,
        margin: "48px auto",
        padding: "24px 16px",
      }}
    >
      <Card>
        <h1>Mis partidos</h1>
        <p>
          Administra los partidos que organizas y revisa
          aquellos en los que participas.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 8,
            marginTop: 24,
          }}
          role="tablist"
          aria-label="Filtros de partidos"
        >
          <Button
            variant={
              activeTab === "organized"
                ? "primary"
                : "secondary"
            }
            onClick={() => setActiveTab("organized")}
            role="tab"
            aria-selected={activeTab === "organized"}
          >
            Organizados por mí
          </Button>

          <Button
            variant={
              activeTab === "participating"
                ? "primary"
                : "secondary"
            }
            onClick={() => setActiveTab("participating")}
            role="tab"
            aria-selected={activeTab === "participating"}
          >
            En los que participo
          </Button>

          <Button
            variant={
              activeTab === "available"
                ? "primary"
                : "secondary"
            }
            onClick={() => setActiveTab("available")}
            role="tab"
            aria-selected={activeTab === "available"}
          >
            Disponibles para unirme
          </Button>
        </div>

        <div
          style={{
            display: "grid",
            gap: 16,
            marginTop: 24,
          }}
        >
          {loading ? (
            <p role="status">Cargando partidos...</p>
          ) : error ? (
            <>
              <Alert variant="error">{error}</Alert>

              <Button
                variant="secondary"
                onClick={() =>
                  setReloadAttempt((current) => current + 1)
                }
              >
                Reintentar
              </Button>
            </>
          ) : matches.length === 0 ? (
            <p role="status">
              Todavía no hay partidos para mostrar.
            </p>
          ) : (
            <ul
              style={{
                display: "grid",
                gap: 12,
                margin: 0,
                padding: 0,
                listStyle: "none",
              }}
            >
              {matches.map((match) => (
                <li
                  key={match.id}
                  style={{
                    border: "1px solid var(--color-border)",
                    borderRadius: 8,
                    padding: 16,
                  }}
                >
                  <strong>{match.venue_name}</strong>
                  <p>
                    {FORMAT_LABELS[match.format]} ·{" "}
                    {STATUS_LABELS[match.status]}
                  </p>
                  <p>{formatMatchSchedule(match)}</p>
                  <p>
                    {match.commune ?? "Comuna sin indicar"}
                  </p>
                  <p>
                    {match.min_players} a {match.max_players}{" "}
                    jugadores
                  </p>
                  {activeTab === "available" && (
                    <Button
                      onClick={() => handleJoin(match.id)}
                      loading={joiningMatchId === match.id}
                      loadingText="Uniéndome..."
                      disabled={Boolean(joiningMatchId)}
                    >
                      Unirme
                    </Button>
                  )}
                </li>
              ))}
            </ul>
          )}

          {joinError && (
            <Alert variant="error">{joinError}</Alert>
          )}

          <Button
            onClick={() => setView("create")}
          >
            Crear partido
          </Button>

          <Button
            variant="secondary"
            onClick={onBack}
          >
            Volver al inicio
          </Button>
        </div>
      </Card>
    </section>
  );
}