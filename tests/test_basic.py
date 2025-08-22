import os
import pytest

os.environ.setdefault("ADMIN_PASSWORD","admin")

@pytest.fixture
def app():
    import app as appmod
    return appmod.app.test_client()

def test_campaigns_page(app):
    resp = app.get("/campaigns/")
    assert resp.status_code in (200,302)

def test_settings_page(app):
    resp = app.get("/settings/")
    assert resp.status_code in (200,302)
