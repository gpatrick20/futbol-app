import { useState } from "react";

import {
  ApiError,
  createMatch,
} from "../../services/api";
import type { Match } from "../../services/api";

import Alert from "../ui/Alert";
import Button from "../ui/Button";
import Card from "../ui/Card";

type CreateMatchFormProps = {
  onCreated: (match: Match) => void;
  onCancel: () => void;
};

export default function CreateMatchForm({
  onCreated,
  onCancel,
}: CreateMatchFormProps) {
  const [format, setFormat] = useState<
    "futbol5" | "futbol7" | "futbol11"
  >("futbol5");
  const [venueName, setVenueName] = useState("");
  const [address, setAddress] = useState("");
  const [commune, setCommune] = useState("");
  const [matchDate, setMatchDate] = useState("");
  const [startTime, setStartTime] = useState("");
  const [totalCost, setTotalCost] = useState("");
  const [minPlayers, setMinPlayers] = useState("10");
  const [maxPlayers, setMaxPlayers] = useState("12");

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      const newMatch = await createMatch({
        format,
        venue_name: venueName,
        address: address || null,
        commune: commune || null,
        match_date: matchDate || null,
        start_time: startTime || null,
        total_cost: totalCost || null,
        min_players: Number(minPlayers),
        max_players: Number(maxPlayers),
      });

      onCreated(newMatch);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        return;
      }

      setError(
        "No pudimos crear el partido. Revisa los datos e inténtalo otra vez.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <h2>Crear partido</h2>
      <p>
        Estás creando este partido con tu cuenta actual. No
        necesitas cambiar de rol ni crear otra cuenta.
      </p>

      <form
        onSubmit={handleSubmit}
        style={{
          display: "grid",
          gap: 16,
          marginTop: 24,
        }}
      >
        {error && <Alert variant="error">{error}</Alert>}

        <label>
          Formato
          <select
            value={format}
            onChange={(event) =>
              setFormat(
                event.target
                  .value as typeof format,
              )
            }
            required
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          >
            <option value="futbol5">Fútbol 5</option>
            <option value="futbol7">Fútbol 7</option>
            <option value="futbol11">Fútbol 11</option>
          </select>
        </label>

        <label>
          Nombre de la cancha
          <input
            value={venueName}
            onChange={(event) =>
              setVenueName(event.target.value)
            }
            required
            minLength={2}
            maxLength={150}
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Dirección
          <input
            value={address}
            onChange={(event) =>
              setAddress(event.target.value)
            }
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Comuna
          <input
            value={commune}
            onChange={(event) =>
              setCommune(event.target.value)
            }
            maxLength={100}
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Fecha
          <input
            type="date"
            value={matchDate}
            onChange={(event) =>
              setMatchDate(event.target.value)
            }
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Hora
          <input
            type="time"
            value={startTime}
            onChange={(event) =>
              setStartTime(event.target.value)
            }
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Costo total (opcional)
          <input
            type="number"
            min="0"
            step="0.01"
            value={totalCost}
            onChange={(event) =>
              setTotalCost(event.target.value)
            }
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Mínimo de jugadores
          <input
            type="number"
            min="0"
            value={minPlayers}
            onChange={(event) =>
              setMinPlayers(event.target.value)
            }
            required
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <label>
          Máximo de jugadores
          <input
            type="number"
            min="0"
            value={maxPlayers}
            onChange={(event) =>
              setMaxPlayers(event.target.value)
            }
            required
            style={{
              width: "100%",
              padding: 10,
              marginTop: 6,
            }}
          />
        </label>

        <div
          style={{
            display: "grid",
            gap: 12,
          }}
        >
          <Button
            type="submit"
            loading={saving}
            loadingText="Creando partido..."
          >
            Crear partido
          </Button>

          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
            disabled={saving}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </Card>
  );
}