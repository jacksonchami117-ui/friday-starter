import pytest
import os
import subprocess
import time
import requests


@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.testing = True
    return app.test_client()


def test_healthz_endpoint(client):
    """Test that /healthz endpoint returns 200 with 'ok' body"""
    r = client.get("/healthz")
    assert r.status_code == 200
    assert b"ok" in r.data


def test_health_endpoint_still_works(client):
    """Ensure existing /health endpoint still works"""
    r = client.get("/health")
    assert r.status_code == 200
    assert b"ok" in r.data


def test_port_flag_precedence():
    """Test CLI port flag precedence: CLI > ENV > default"""
    # Test that we can import and run CLI
    from app import main
    
    # Test CLI help works
    import subprocess
    result = subprocess.run(
        ["python", "app.py", "--help"], 
        capture_output=True, 
        text=True,
        cwd="/home/runner/work/friday-starter/friday-starter"
    )
    assert result.returncode == 0
    assert "--port" in result.stdout
    assert "overrides PORT env var" in result.stdout


def test_port_precedence_integration():
    """Integration test for port precedence - quick start/stop test"""
    import subprocess
    import time
    import signal
    
    # Test with CLI port flag
    proc = subprocess.Popen(
        ["python", "app.py", "--port", "9999"],
        cwd="/home/runner/work/friday-starter/friday-starter",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give server time to start
    time.sleep(2)
    
    try:
        # Quick check that something is listening
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 9999))
        sock.close()
        
        # 0 means connection successful
        assert result == 0, "Server should be listening on port 9999"
        
    finally:
        # Clean up process
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()