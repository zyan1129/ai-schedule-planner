-- SmartSchedule: per-user profiles and saved schedules.
-- Paste into Supabase dashboard -> SQL Editor -> Run. Safe to run more than once.

create table if not exists public.profiles (
    user_id       text primary key,          -- Google OIDC "sub" (stable per account)
    email         text,
    name          text,
    picture       text,
    created_at    timestamptz not null default now(),
    last_login_at timestamptz not null default now()
);

create table if not exists public.schedules (
    user_id    text primary key references public.profiles (user_id) on delete cascade,
    parsed     jsonb,                        -- schedule as parsed from the input text
    working    jsonb,                        -- edited schedule (incl. status = 'unsure')
    conflicts  jsonb,
    updated_at timestamptz not null default now()
);

-- RLS on with no policies: the public anon key can't touch these tables.
-- The app talks to Supabase only from the server, using the service_role key,
-- which bypasses RLS.
alter table public.profiles  enable row level security;
alter table public.schedules enable row level security;
