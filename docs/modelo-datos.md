# Modelo de datos inicial

## users

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| email | VARCHAR | Email único del usuario |
| hashed_password | TEXT | Contraseña hasheada |
| full_name | VARCHAR | Nombre completo |
| role | VARCHAR | `leader` o `player` |
| commune | VARCHAR | Comuna o zona habitual |
| position | VARCHAR | Posición habitual opcional |
| created_at | TIMESTAMP | Fecha de creación |

## teams

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| name | VARCHAR | Nombre del equipo |
| leader_id | UUID | Usuario líder |
| commune | VARCHAR | Comuna o zona |
| description | TEXT | Descripción opcional |
| created_at | TIMESTAMP | Fecha de creación |

## team_members

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| team_id | UUID | Equipo |
| user_id | UUID | Usuario |
| role | VARCHAR | `leader` o `player` |
| joined_at | TIMESTAMP | Fecha de ingreso |

## matches

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| created_by | UUID | Líder creador |
| format | VARCHAR | `futbol5`, `futbol7` o `futbol11` |
| venue_name | VARCHAR | Nombre de la cancha |
| address | TEXT | Dirección |
| commune | VARCHAR | Comuna |
| match_date | DATE | Fecha del partido |
| start_time | TIME | Hora de inicio |
| status | VARCHAR | Estado del partido |
| total_cost | NUMERIC | Costo total de la cancha |
| min_players | INTEGER | Mínimo de jugadores |
| max_players | INTEGER | Máximo de jugadores |
| created_at | TIMESTAMP | Fecha de creación |

## match_participants

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| match_id | UUID | Partido |
| user_id | UUID | Usuario |
| status | VARCHAR | `invited`, `confirmed`, `tentative`, `absent` o `substitute` |
| joined_at | TIMESTAMP | Fecha de respuesta |

## availability_votes

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| match_id | UUID | Partido |
| user_id | UUID | Usuario |
| proposed_date | DATE | Fecha propuesta |
| proposed_time | TIME | Hora propuesta |
| availability | VARCHAR | `available`, `maybe` o `unavailable` |

## payments

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| match_id | UUID | Partido |
| user_id | UUID | Usuario |
| amount | NUMERIC | Monto a pagar |
| status | VARCHAR | `pending`, `paid` o `rejected` |
| method | VARCHAR | `cash`, `transfer` u `online` |
| paid_at | TIMESTAMP | Fecha de pago |

## match_events

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| match_id | UUID | Partido |
| player_id | UUID | Jugador |
| event_type | VARCHAR | `goal`, `assist` u `mvp` |
| minute | INTEGER | Minuto del evento, opcional |
| created_at | TIMESTAMP | Fecha de creación |

## team_match_results

| Campo | Tipo | Descripción |
|---|---|---|
| id | UUID | Identificador único |
| match_id | UUID | Partido |
| team_id | UUID | Equipo |
| goals_for | INTEGER | Goles a favor |
| goals_against | INTEGER | Goles en contra |
| result | VARCHAR | `win`, `loss` o `draw` |
