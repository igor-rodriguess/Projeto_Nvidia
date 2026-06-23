from app.db.supabase_client import SupabaseConfig


def test_supabase_config_returns_none_without_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    assert SupabaseConfig.from_env() is None


def test_supabase_config_reads_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co/")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role")

    config = SupabaseConfig.from_env()

    assert config is not None
    assert config.url == "https://example.supabase.co"
    assert config.service_role_key == "service-role"
