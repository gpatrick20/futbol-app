# futbol-app

App para organizar partidos de fútbol amateur: votación de horarios, gestión de jugadores, cuotas de cancha, equipos, retas y estadísticas.

## Estructura

```text
futbol-app/
├── backend/   # API en Python + FastAPI + PostgreSQL
├── frontend/  # Interfaz en React + Vite + TypeScript
└── docs/      # PRD, modelo de datos y roadmap
```

## MVP

- Crear partidos de fútbol 5, 7 y 11
- Votar disponibilidad por día y hora
- Invitar y confirmar jugadores
- Calcular y registrar manualmente la cuota de la cancha
- Registrar resultados, goleadores y estadísticas básicas

## Tecnologías

- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL
- Frontend: React, Vite, TypeScript
- Autenticación: JWT
- Pagos: se integrarán en una fase posterior

## Ejecución local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Documentación

- [PRD](docs/PRD.md)
- [Modelo de datos](docs/modelo-datos.md)
- [Roadmap](docs/roadmap.md)
