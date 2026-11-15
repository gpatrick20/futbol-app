import { useState } from "react";
import type { FormEvent } from "react";
import { ApiError, createMatch } from "../../services/api";
import type { Match, MatchCreateData } from "../../services/api";
import Alert from "../ui/Alert";
import Button from "../ui/Button";
import Card from "../ui/Card";

type Props = {
  onCreated: (match: Match) => void;
  onCancel: () => void;
};

export default function CreateMatchForm({ onCreated, onCancel }: Props) {
  const [format, setFormat] = useState<MatchCreateData["format"]>("futbol5");
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
  const inputStyle = { width: "100%", padding: 10, marginTop: 6 };

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (saving) return;
    setError("");
    const minimum = Number(minPlayers);
    const maximum = Number(maxPlayers);
    if (
      minPlayers.trim() === "" || maxPlayers.trim() === "" ||
      !Number.isInteger(minimum) || !Number.isInteger(maximum) ||
      minimum < 0 || maximum < 1 || maximum < minimum
    ) {
      setError("Usa cupos enteros: mínimo desde 0 y máximo desde 1, sin que el mínimo supere al máximo. Tu cupo está incluido.");
      return;
    }
    if (venueName.trim().length < 2) {
      setError("Ingresa al menos dos caracteres para el nombre de la cancha.");
      return;
    }
    setSaving(true);
    try {
      const match = await createMatch({
        format,
        venue_name: venueName.trim(),
        address: address.trim() || null,
        commune: commune.trim() || null,
        match_date: matchDate || null,
        start_time: startTime || null,
        total_cost: totalCost || null,
        min_players: minimum,
        max_players: maximum,
      });
      onCreated(match);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return;
      setError(err instanceof ApiError ? err.message : "No pudimos crear el partido. Inténtalo otra vez.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <h2>Crear partido</h2>
      <p>Quedarás inscrito automáticamente como jugador confirmado en el Equipo A. Tu cupo está incluido en el máximo de jugadores.</p>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16, marginTop: 24 }}>
        {error && <Alert variant="error">{error}</Alert>}
        <fieldset disabled={saving} style={{ border: 0, padding: 0, margin: 0, minWidth: 0, display: "grid", gap: 16 }}>
          <legend>Datos del partido</legend>
          <label>Formato
            <select value={format} onChange={(e) => setFormat(e.target.value as MatchCreateData["format"])} required style={inputStyle}>
              <option value="futbol5">Fútbol 5</option>
              <option value="futbol7">Fútbol 7</option>
              <option value="futbol11">Fútbol 11</option>
            </select>
          </label>
          <label>Nombre de la cancha
            <input value={venueName} onChange={(e) => setVenueName(e.target.value)} required minLength={2} maxLength={150} style={inputStyle} />
          </label>
          <label>Dirección
            <input value={address} onChange={(e) => setAddress(e.target.value)} style={inputStyle} />
          </label>
          <label>Comuna
            <input value={commune} onChange={(e) => setCommune(e.target.value)} maxLength={100} style={inputStyle} />
          </label>
          <label>Fecha
            <input type="date" value={matchDate} onChange={(e) => setMatchDate(e.target.value)} style={inputStyle} />
          </label>
          <label>Hora
            <input type="time" value={startTime} onChange={(e) => setStartTime(e.target.value)} style={inputStyle} />
          </label>
          <label>Costo total (opcional)
            <input type="number" min="0" step="0.01" value={totalCost} onChange={(e) => setTotalCost(e.target.value)} style={inputStyle} />
          </label>
          <label>Mínimo de jugadores
            <input type="number" min="0" step="1" value={minPlayers} onChange={(e) => setMinPlayers(e.target.value)} required style={inputStyle} />
          </label>
          <label>Máximo de jugadores (incluyéndote)
            <input type="number" min="1" step="1" value={maxPlayers} onChange={(e) => setMaxPlayers(e.target.value)} required style={inputStyle} />
          </label>
        </fieldset>
        <Button type="submit" loading={saving} loadingText="Creando partido..." disabled={saving}>Crear partido</Button>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={saving}>Cancelar</Button>
      </form>
    </Card>
  );
}
