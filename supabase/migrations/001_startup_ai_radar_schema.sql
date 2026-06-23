-- NVIDIA Startup AI Radar - relational knowledge schema
-- Run this file in Supabase SQL Editor or through the Supabase CLI.

create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists public.discovery_runs (
  id uuid primary key default gen_random_uuid(),
  query text not null,
  status text not null default 'completed'
    check (status in ('running', 'completed', 'failed', 'partial')),
  attempt_count integer not null default 0 check (attempt_count >= 0),
  errors jsonb not null default '[]'::jsonb,
  raw_result jsonb,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.discovery_search_terms (
  id uuid primary key default gen_random_uuid(),
  discovery_run_id uuid not null references public.discovery_runs(id) on delete cascade,
  term text not null,
  position integer not null default 0,
  created_at timestamptz not null default now(),
  unique (discovery_run_id, term)
);

create table if not exists public.companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  normalized_name text generated always as (
    lower(regexp_replace(trim(name), '\s+', ' ', 'g'))
  ) stored,
  description text,
  sector text,
  website_url text,
  country text default 'Brazil',
  city text,
  state_region text,
  founded_year integer check (
    founded_year is null or (founded_year between 1800 and extract(year from now())::integer + 1)
  ),
  status text not null default 'discovered'
    check (status in ('discovered', 'validated', 'rejected', 'archived')),
  first_seen_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (normalized_name)
);

create trigger companies_set_updated_at
before update on public.companies
for each row execute function public.set_updated_at();

create table if not exists public.company_discoveries (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  discovery_run_id uuid not null references public.discovery_runs(id) on delete cascade,
  extracted_name text not null,
  extracted_description text,
  extracted_sector text,
  raw_startup jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (company_id, discovery_run_id)
);

create table if not exists public.company_sources (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references public.companies(id) on delete cascade,
  discovery_run_id uuid references public.discovery_runs(id) on delete set null,
  title text not null,
  url text not null,
  url_hash text generated always as (encode(digest(url, 'sha256'), 'hex')) stored,
  snippet text,
  source_type text not null default 'public_search',
  source_domain text generated always as (
    regexp_replace(
      regexp_replace(lower(url), '^https?://(www\.)?', ''),
      '/.*$',
      ''
    )
  ) stored,
  collected_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (company_id, url_hash)
);

create table if not exists public.company_ai_signals (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  signal text not null,
  signal_type text not null default 'keyword'
    check (signal_type in ('keyword', 'model', 'workflow', 'infrastructure', 'domain')),
  evidence_source_id uuid references public.company_sources(id) on delete set null,
  confidence text not null default 'medium'
    check (confidence in ('low', 'medium', 'high')),
  created_at timestamptz not null default now(),
  unique (company_id, signal, signal_type)
);

create table if not exists public.company_evidence_validations (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  discovery_run_id uuid references public.discovery_runs(id) on delete set null,
  is_publicly_supported boolean not null default false,
  has_ai_evidence boolean not null default false,
  source_count integer not null default 0 check (source_count >= 0),
  reliable_source_count integer not null default 0 check (reliable_source_count >= 0),
  confidence_level text not null default 'none'
    check (confidence_level in ('none', 'low', 'medium', 'high')),
  validation_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.company_ai_maturity_assessments (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  discovery_run_id uuid references public.discovery_runs(id) on delete set null,
  level text not null check (level in ('unclear', 'emerging', 'applied', 'advanced')),
  score integer not null default 0 check (score >= 0),
  method text not null default 'keyword_and_evidence_rules',
  assessment_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.nvidia_technologies (
  id text primary key,
  name text not null,
  category text not null,
  description text,
  source_ids text[] not null default '{}',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create trigger nvidia_technologies_set_updated_at
before update on public.nvidia_technologies
for each row execute function public.set_updated_at();

insert into public.nvidia_technologies (id, name, category, description, source_ids)
values
  ('nvidia_inception', 'NVIDIA Inception', 'startup_program', 'Startup ecosystem program for technical resources, visibility and partner access.', array['nvidia_inception']),
  ('nvidia_api_catalog', 'NVIDIA API Catalog', 'model_exploration', 'Catalog for exploring and testing NVIDIA-hosted AI APIs and models.', array['nvidia_api_catalog']),
  ('nvidia_nim', 'NVIDIA NIM', 'model_serving', 'Microservices for deploying optimized AI models and generative AI inference.', array['nvidia_nim']),
  ('nvidia_nemo', 'NVIDIA NeMo', 'model_customization', 'Suite for developing, customizing, evaluating and operating generative AI systems.', array['nvidia_nemo']),
  ('nemo_guardrails', 'NeMo Guardrails', 'ai_safety', 'Toolkit for programmable guardrails in LLM conversational systems.', array['nvidia_nemo_guardrails']),
  ('triton_inference_server', 'NVIDIA Triton Inference Server', 'production_inference', 'Inference server for deploying and serving models across multiple frameworks.', array['nvidia_triton', 'nvidia_triton_docs']),
  ('tensorrt_llm', 'NVIDIA TensorRT-LLM', 'llm_optimization', 'Library for optimizing LLM inference on NVIDIA GPUs.', array['nvidia_tensorrt_llm']),
  ('rapids_cudf_cuml', 'NVIDIA RAPIDS, cuDF, and cuML', 'data_science_acceleration', 'GPU-accelerated data science stack for dataframe and classical ML workflows.', array['nvidia_rapids', 'nvidia_cudf', 'nvidia_cuml']),
  ('cuda_toolkit', 'CUDA Toolkit', 'accelerated_computing_development', 'Development toolkit for building GPU-accelerated applications.', array['nvidia_cuda']),
  ('nvidia_riva', 'NVIDIA Riva', 'speech_ai', 'Speech AI SDK for real-time speech and language applications.', array['nvidia_riva']),
  ('nvidia_omniverse', 'NVIDIA Omniverse', 'simulation_and_digital_twins', 'Platform for simulation, digital twins and connected 3D workflows.', array['nvidia_omniverse']),
  ('nvidia_isaac', 'NVIDIA Isaac', 'robotics', 'Platform and tooling for robotics development, simulation and autonomous machines.', array['nvidia_isaac']),
  ('nvidia_clara', 'NVIDIA Clara / Healthcare and Life Sciences', 'healthcare_ai', 'NVIDIA healthcare and life sciences ecosystem for AI and accelerated computing.', array['nvidia_clara']),
  ('nvidia_morpheus', 'NVIDIA Morpheus', 'cybersecurity_ai', 'AI framework for cybersecurity analytics and threat detection workflows.', array['nvidia_morpheus']),
  ('nvidia_ai_enterprise', 'NVIDIA AI Enterprise', 'enterprise_ai_platform', 'Enterprise AI software platform for supported production AI operations.', array['nvidia_ai_enterprise'])
on conflict (id) do update set
  name = excluded.name,
  category = excluded.category,
  description = excluded.description,
  source_ids = excluded.source_ids,
  updated_at = now();

create table if not exists public.company_nvidia_recommendations (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  discovery_run_id uuid references public.discovery_runs(id) on delete set null,
  technology_id text not null references public.nvidia_technologies(id) on delete restrict,
  confidence text not null check (confidence in ('low', 'medium', 'high')),
  match_score integer not null default 0 check (match_score >= 0),
  reason text not null,
  matched_startup_signals text[] not null default '{}',
  matched_ai_signals text[] not null default '{}',
  matched_sector text,
  retrieved_from_vector_store boolean not null default false,
  guardrails text[] not null default '{}',
  missing_evidence text[] not null default '{}',
  recommendation_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.company_nvidia_recommendation_sources (
  id uuid primary key default gen_random_uuid(),
  recommendation_id uuid not null references public.company_nvidia_recommendations(id) on delete cascade,
  source_id text not null,
  title text not null,
  url text not null,
  source_type text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.company_knowledge_items (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  source_id uuid references public.company_sources(id) on delete set null,
  knowledge_type text not null default 'fact'
    check (knowledge_type in ('fact', 'claim', 'risk', 'need', 'technology_signal', 'market_signal')),
  content text not null,
  confidence text not null default 'medium'
    check (confidence in ('low', 'medium', 'high')),
  extraction_method text not null default 'pipeline',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.company_snapshots (
  id uuid primary key default gen_random_uuid(),
  company_id uuid not null references public.companies(id) on delete cascade,
  discovery_run_id uuid references public.discovery_runs(id) on delete set null,
  snapshot_type text not null default 'pipeline_result',
  payload jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_discovery_runs_created_at
  on public.discovery_runs (created_at desc);

create index if not exists idx_companies_normalized_name
  on public.companies (normalized_name);

create index if not exists idx_companies_sector
  on public.companies (sector);

create index if not exists idx_company_sources_company_id
  on public.company_sources (company_id);

create index if not exists idx_company_sources_domain
  on public.company_sources (source_domain);

create index if not exists idx_company_ai_signals_company_id
  on public.company_ai_signals (company_id);

create index if not exists idx_company_ai_signals_signal
  on public.company_ai_signals (signal);

create index if not exists idx_company_recommendations_company_id
  on public.company_nvidia_recommendations (company_id);

create index if not exists idx_company_recommendations_technology_id
  on public.company_nvidia_recommendations (technology_id);

create index if not exists idx_company_knowledge_items_company_id
  on public.company_knowledge_items (company_id);

create index if not exists idx_company_snapshots_company_id
  on public.company_snapshots (company_id);

create or replace view public.company_latest_evidence_validation as
select distinct on (company_id)
  *
from public.company_evidence_validations
order by company_id, created_at desc;

create or replace view public.company_latest_ai_maturity as
select distinct on (company_id)
  *
from public.company_ai_maturity_assessments
order by company_id, created_at desc;

create or replace view public.company_radar_summary as
select
  c.id,
  c.name,
  c.description,
  c.sector,
  c.country,
  c.status,
  ev.has_ai_evidence,
  ev.confidence_level as evidence_confidence,
  mt.level as ai_maturity_level,
  mt.score as ai_maturity_score,
  count(distinct cs.id) as source_count,
  count(distinct rec.id) as recommendation_count,
  c.created_at,
  c.updated_at
from public.companies c
left join public.company_latest_evidence_validation ev on ev.company_id = c.id
left join public.company_latest_ai_maturity mt on mt.company_id = c.id
left join public.company_sources cs on cs.company_id = c.id
left join public.company_nvidia_recommendations rec on rec.company_id = c.id
group by
  c.id,
  ev.has_ai_evidence,
  ev.confidence_level,
  mt.level,
  mt.score;

alter table public.discovery_runs enable row level security;
alter table public.discovery_search_terms enable row level security;
alter table public.companies enable row level security;
alter table public.company_discoveries enable row level security;
alter table public.company_sources enable row level security;
alter table public.company_ai_signals enable row level security;
alter table public.company_evidence_validations enable row level security;
alter table public.company_ai_maturity_assessments enable row level security;
alter table public.nvidia_technologies enable row level security;
alter table public.company_nvidia_recommendations enable row level security;
alter table public.company_nvidia_recommendation_sources enable row level security;
alter table public.company_knowledge_items enable row level security;
alter table public.company_snapshots enable row level security;

comment on table public.companies is 'Canonical companies/startups discovered by NVIDIA Startup AI Radar.';
comment on table public.company_sources is 'Traceable public evidence linked to companies.';
comment on table public.company_knowledge_items is 'Small structured knowledge facts extracted about a company. Use this for future company-level memory and retrieval.';
comment on table public.company_nvidia_recommendations is 'NVIDIA technology recommendations generated by the RAG agent with guardrails and missing evidence.';
comment on view public.company_radar_summary is 'Operational summary view for dashboards and API reads.';
