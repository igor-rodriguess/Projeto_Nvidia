begin;

create extension if not exists pgcrypto with schema extensions;
create schema if not exists nvidia_inception;

do $$
declare
  exposed_schemas text;
begin
  if exists (select 1 from pg_roles where rolname = 'authenticator') then
    select split_part(setting, '=', 2)
      into exposed_schemas
      from unnest(
        coalesce(
          (select rolconfig from pg_roles where rolname = 'authenticator'),
          array[]::text[]
        )
      ) as setting
     where setting like 'pgrst.db_schemas=%'
     limit 1;

    exposed_schemas := coalesce(exposed_schemas, 'public, graphql_public');
    if not ('nvidia_inception' = any(
      string_to_array(replace(exposed_schemas, ' ', ''), ',')
    )) then
      exposed_schemas := exposed_schemas || ', nvidia_inception';
    end if;

    execute format(
      'alter role authenticator set pgrst.db_schemas = %L',
      exposed_schemas
    );
  end if;
end;
$$;

revoke all on schema nvidia_inception from public, anon, authenticated;
grant usage on schema nvidia_inception to service_role;

create or replace function nvidia_inception.set_updated_at()
returns trigger
language plpgsql
security invoker
set search_path = nvidia_inception, public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists nvidia_inception.startups (
  id uuid primary key default gen_random_uuid(),
  nome text not null check (length(trim(nome)) > 0),
  site_oficial text,
  categoria text,
  cidade text,
  estado varchar(2),
  pais text not null default 'Brasil',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint startups_site_http check (
    site_oficial is null or site_oficial ~* '^https?://'
  )
);

create unique index if not exists startups_nome_lower_uidx
  on nvidia_inception.startups (lower(nome));
create unique index if not exists startups_site_oficial_uidx
  on nvidia_inception.startups (site_oficial)
  where site_oficial is not null;

create table if not exists nvidia_inception.pipeline_runs (
  id uuid primary key default gen_random_uuid(),
  startup_id uuid not null references nvidia_inception.startups(id) on delete cascade,
  status text not null default 'pending'
    check (status in ('pending', 'running', 'completed', 'partial', 'failed')),
  started_at timestamptz,
  finished_at timestamptz,
  duration_ms bigint check (duration_ms is null or duration_ms >= 0),
  current_stage text,
  trace_path text,
  errors jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint pipeline_run_dates check (
    finished_at is null or started_at is null or finished_at >= started_at
  )
);

create table if not exists nvidia_inception.search_queries (
  id uuid primary key default gen_random_uuid(),
  pipeline_run_id uuid not null references nvidia_inception.pipeline_runs(id) on delete cascade,
  consulta text not null check (length(trim(consulta)) > 0),
  camada smallint check (camada between 1 and 7),
  objetivo text,
  resultados_count integer not null default 0 check (resultados_count >= 0),
  created_at timestamptz not null default now(),
  unique (pipeline_run_id, consulta)
);

create table if not exists nvidia_inception.sources (
  id uuid primary key default gen_random_uuid(),
  pipeline_run_id uuid not null references nvidia_inception.pipeline_runs(id) on delete cascade,
  url text not null check (url ~* '^https?://'),
  tipo_fonte text not null default 'outro'
    check (tipo_fonte in ('oficial', 'imprensa', 'ecossistema', 'social', 'outro')),
  credibilidade double precision not null default 0.0
    check (credibilidade between 0.0 and 1.0),
  status text not null default 'acessivel'
    check (status in ('acessivel', 'quebrada', 'bloqueada')),
  created_at timestamptz not null default now(),
  unique (pipeline_run_id, url)
);

create table if not exists nvidia_inception.evidences (
  id uuid primary key default gen_random_uuid(),
  pipeline_run_id uuid not null references nvidia_inception.pipeline_runs(id) on delete cascade,
  source_id uuid not null references nvidia_inception.sources(id) on delete cascade,
  trecho text,
  score_confianca double precision not null default 0.0
    check (score_confianca between 0.0 and 1.0),
  classificacao text not null default 'baixa'
    check (classificacao in ('alta', 'media', 'baixa')),
  contem_ia boolean not null default false,
  descartada boolean not null default false,
  motivo_descarte text,
  created_at timestamptz not null default now(),
  constraint evidencia_descarte_motivo check (
    not descartada or motivo_descarte is not null
  ),
  unique (pipeline_run_id, source_id, trecho)
);

create table if not exists nvidia_inception.ai_assessments (
  id uuid primary key default gen_random_uuid(),
  pipeline_run_id uuid not null unique references nvidia_inception.pipeline_runs(id) on delete cascade,
  classificacao text not null
    check (classificacao in ('AI-native', 'AI-enabled', 'API-consumer', 'Non-AI')),
  nivel_maturidade smallint not null,
  confianca_classificacao double precision not null
    check (confianca_classificacao between 0.0 and 1.0),
  tecnologias_utilizadas jsonb not null default '{}'::jsonb,
  necessidades jsonb not null default '[]'::jsonb,
  justificativa text not null,
  evidencias_usadas jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  constraint assessment_maturity_check check (
    (classificacao = 'Non-AI' and nivel_maturidade = 0)
    or (classificacao <> 'Non-AI' and nivel_maturidade between 1 and 5)
  )
);

create table if not exists nvidia_inception.nvidia_recommendations (
  id uuid primary key default gen_random_uuid(),
  pipeline_run_id uuid not null unique references nvidia_inception.pipeline_runs(id) on delete cascade,
  recomendacao_json jsonb not null default '{}'::jsonb,
  fit_score double precision check (fit_score is null or fit_score between 0.0 and 1.0),
  created_at timestamptz not null default now()
);

create table if not exists nvidia_inception.recommendation_citations (
  id uuid primary key default gen_random_uuid(),
  recommendation_id uuid not null references nvidia_inception.nvidia_recommendations(id) on delete cascade,
  tecnologia text not null,
  trecho_doc text not null,
  url_doc text not null check (url_doc ~* '^https?://'),
  created_at timestamptz not null default now(),
  unique (recommendation_id, tecnologia, url_doc, trecho_doc)
);

create index if not exists pipeline_runs_startup_id_idx
  on nvidia_inception.pipeline_runs(startup_id);
create index if not exists pipeline_runs_status_idx
  on nvidia_inception.pipeline_runs(status);
create index if not exists search_queries_run_id_idx
  on nvidia_inception.search_queries(pipeline_run_id);
create index if not exists sources_run_id_idx
  on nvidia_inception.sources(pipeline_run_id);
create index if not exists sources_status_idx
  on nvidia_inception.sources(status);
create index if not exists evidences_run_id_idx
  on nvidia_inception.evidences(pipeline_run_id);
create index if not exists evidences_classificacao_idx
  on nvidia_inception.evidences(classificacao);
create index if not exists assessments_run_id_idx
  on nvidia_inception.ai_assessments(pipeline_run_id);
create index if not exists assessments_classificacao_idx
  on nvidia_inception.ai_assessments(classificacao);
create index if not exists recommendations_run_id_idx
  on nvidia_inception.nvidia_recommendations(pipeline_run_id);
create index if not exists citations_recommendation_id_idx
  on nvidia_inception.recommendation_citations(recommendation_id);

drop trigger if exists startups_set_updated_at on nvidia_inception.startups;
create trigger startups_set_updated_at
before update on nvidia_inception.startups
for each row execute function nvidia_inception.set_updated_at();

drop trigger if exists pipeline_runs_set_updated_at on nvidia_inception.pipeline_runs;
create trigger pipeline_runs_set_updated_at
before update on nvidia_inception.pipeline_runs
for each row execute function nvidia_inception.set_updated_at();

alter table nvidia_inception.startups enable row level security;
alter table nvidia_inception.pipeline_runs enable row level security;
alter table nvidia_inception.search_queries enable row level security;
alter table nvidia_inception.sources enable row level security;
alter table nvidia_inception.evidences enable row level security;
alter table nvidia_inception.ai_assessments enable row level security;
alter table nvidia_inception.nvidia_recommendations enable row level security;
alter table nvidia_inception.recommendation_citations enable row level security;

do $$
declare
  table_name text;
begin
  foreach table_name in array array[
    'startups', 'pipeline_runs', 'search_queries', 'sources', 'evidences',
    'ai_assessments', 'nvidia_recommendations', 'recommendation_citations'
  ] loop
    execute format('drop policy if exists service_role_all on nvidia_inception.%I', table_name);
    execute format(
      'create policy service_role_all on nvidia_inception.%I for all to service_role '
      'using ((select auth.role()) = ''service_role'') '
      'with check ((select auth.role()) = ''service_role'')',
      table_name
    );
  end loop;
end;
$$;

grant all on all tables in schema nvidia_inception to service_role;
grant all on all sequences in schema nvidia_inception to service_role;
grant execute on all functions in schema nvidia_inception to service_role;
alter default privileges for role postgres in schema nvidia_inception
  grant all on tables to service_role;
alter default privileges for role postgres in schema nvidia_inception
  grant all on sequences to service_role;
alter default privileges for role postgres in schema nvidia_inception
  grant execute on functions to service_role;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'pipeline-traces',
  'pipeline-traces',
  false,
  52428800,
  array['application/json']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

commit;

notify pgrst, 'reload config';
notify pgrst, 'reload schema';
