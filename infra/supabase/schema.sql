-- Table: public.risk_limits
create table if not exists public.risk_limits (
  scope text primary key,          -- 'global' or agent name
  max_notional numeric,            -- e.g. 100000
  max_qty numeric                  -- optional per-order cap
);

-- Seed a default global row (optional; safe on re-run)
insert into public.risk_limits (scope, max_notional)
values ('global', 100000)
on conflict (scope) do nothing; 