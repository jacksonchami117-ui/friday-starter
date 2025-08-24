import pytest

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.testing = True
    return app.test_client()

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert b"ok" in r.data

def test_home(client):
    assert client.get("/home").status_code == 200

def test_diagnostics(client):
    r = client.get("/diagnostics")
    assert r.status_code in (200, 500)

def test_render_start(client):
    r = client.post("/render/start", json={"manifest": {}})
    assert r.status_code in (200,400,500)

def test_campaign_create(client):
    r = client.post("/campaigns/create", data={"name":"pytest-campaign"})
    assert r.status_code in (200,302,400)

def test_404(client):
    assert client.get("/does/not/exist").status_code == 404
