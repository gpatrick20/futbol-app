BEGIN;

CREATE TABLE public.users (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 email varchar(255) NOT NULL UNIQUE,
 hashed_password varchar(255) NOT NULL,
 full_name varchar(120) NOT NULL,
 role varchar(20) NOT NULL DEFAULT 'player' CHECK (role IN ('leader','player')),
 commune varchar(100), position varchar(50),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.teams (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 name varchar(120) NOT NULL,
 leader_id uuid NOT NULL REFERENCES public.users(id),
 commune varchar(100), description text,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.team_members (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 team_id uuid NOT NULL REFERENCES public.teams(id),
 user_id uuid NOT NULL REFERENCES public.users(id),
 role varchar(20) NOT NULL DEFAULT 'player' CHECK (role IN ('leader','player')),
 joined_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE (team_id,user_id)
);
CREATE TABLE public.matches (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 created_by uuid NOT NULL REFERENCES public.users(id),
 format varchar(20) NOT NULL CHECK (format IN ('futbol5','futbol7','futbol11')),
 venue_name varchar(150) NOT NULL, address text, commune varchar(100),
 match_date date, start_time time,
 status varchar(30) NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed','voting','confirmed','full','cancelled','played')),
 total_cost numeric(10,2) CHECK (total_cost >= 0),
 min_players integer NOT NULL DEFAULT 0 CHECK (min_players >= 0),
 max_players integer NOT NULL DEFAULT 0 CHECK (max_players >= min_players),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.match_participants (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 match_id uuid NOT NULL REFERENCES public.matches(id),
 user_id uuid NOT NULL REFERENCES public.users(id),
 status varchar(20) NOT NULL DEFAULT 'invited' CHECK (status IN ('invited','confirmed','tentative','absent','substitute')),
 joined_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE (match_id,user_id)
);
CREATE TABLE public.availability_votes (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 match_id uuid NOT NULL REFERENCES public.matches(id),
 user_id uuid NOT NULL REFERENCES public.users(id),
 proposed_date date NOT NULL, proposed_time time NOT NULL,
 availability varchar(20) NOT NULL CHECK (availability IN ('available','maybe','unavailable')),
 UNIQUE (match_id,user_id,proposed_date,proposed_time)
);
CREATE TABLE public.payments (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 match_id uuid NOT NULL REFERENCES public.matches(id),
 user_id uuid NOT NULL REFERENCES public.users(id),
 amount numeric(10,2) NOT NULL CHECK (amount >= 0),
 status varchar(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','paid','rejected')),
 method varchar(20) CHECK (method IN ('cash','transfer','online')),
 paid_at timestamptz,
 UNIQUE (match_id,user_id)
);
CREATE TABLE public.match_events (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 match_id uuid NOT NULL REFERENCES public.matches(id),
 player_id uuid NOT NULL REFERENCES public.users(id),
 event_type varchar(20) NOT NULL CHECK (event_type IN ('goal','assist','mvp')),
 minute integer CHECK (minute >= 0),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.team_match_results (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 match_id uuid NOT NULL REFERENCES public.matches(id),
 team_id uuid NOT NULL REFERENCES public.teams(id),
 goals_for integer NOT NULL DEFAULT 0 CHECK (goals_for >= 0),
 goals_against integer NOT NULL DEFAULT 0 CHECK (goals_against >= 0),
 result varchar(10) NOT NULL CHECK (result IN ('win','loss','draw')),
 UNIQUE (match_id,team_id),
 CHECK ((result = 'win' AND goals_for > goals_against) OR (result = 'loss' AND goals_for < goals_against) OR (result = 'draw' AND goals_for = goals_against))
);

CREATE INDEX ix_users_email ON public.users(email);
CREATE INDEX ix_teams_leader_id ON public.teams(leader_id);
CREATE INDEX ix_team_members_user_id ON public.team_members(user_id);
CREATE INDEX ix_matches_created_by ON public.matches(created_by);
CREATE INDEX ix_match_participants_user_id ON public.match_participants(user_id);
CREATE INDEX ix_availability_votes_user_id ON public.availability_votes(user_id);
CREATE INDEX ix_payments_user_id ON public.payments(user_id);
CREATE INDEX ix_match_events_match_id ON public.match_events(match_id);
CREATE INDEX ix_match_events_player_id ON public.match_events(player_id);
CREATE INDEX ix_team_match_results_team_id ON public.team_match_results(team_id);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.availability_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.match_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.team_match_results ENABLE ROW LEVEL SECURITY;

REVOKE ALL ON TABLE public.users, public.teams, public.team_members, public.matches, public.match_participants, public.availability_votes, public.payments, public.match_events, public.team_match_results FROM anon, authenticated;

COMMIT;
