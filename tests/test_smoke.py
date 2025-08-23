import importlib

def test_import_and_health():
    app_mod = importlib.import_module("app")
    app = app_mod.create_app()
    client = app.test_client()
    r = client.get("/health")
    assert r.status_code == 200
    assert b"ok" in r.data
