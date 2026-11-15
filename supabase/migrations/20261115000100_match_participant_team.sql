BEGIN;

-- Solo asigna un bando a participaciones existentes; no crea participantes.
ALTER TABLE public.match_participants
    ADD COLUMN team varchar(1) NOT NULL DEFAULT 'A';

ALTER TABLE public.match_participants
    ADD CONSTRAINT ck_match_participants_team CHECK (team IN ('A', 'B'));

COMMENT ON COLUMN public.match_participants.team IS
    'Bando A/B dentro del partido; no representa membresía en public.teams.';

COMMIT;
