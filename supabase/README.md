# Supabase database setup

Use `migrations/001_startup_ai_radar_schema.sql` to create the initial relational database for company knowledge.

What it stores:

- discovery runs and search terms
- canonical companies/startups
- public evidence sources
- AI signals
- evidence validation history
- AI maturity history
- curated NVIDIA technologies
- NVIDIA RAG recommendations
- company knowledge items
- raw pipeline snapshots

How to run in Supabase:

1. Create a Supabase project.
2. Open `SQL Editor`.
3. Paste the contents of `supabase/migrations/001_startup_ai_radar_schema.sql`.
4. Run the SQL.
5. Confirm these tables exist in `Table Editor`.

Security note:

The migration enables Row Level Security on all tables and does not add public policies. This is intentional for now: the backend should write using the Supabase service role key, not the public anon key.

Useful views:

- `company_radar_summary`
- `company_latest_evidence_validation`
- `company_latest_ai_maturity`
