import hashlib
import os, sys, pathlib
# ensure root path for importing src
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import src.db as db

def test_email_token_lowercase_and_short():
    email = 'USER@example.com'
    expected = hashlib.sha1(email.lower().encode('utf-8')).hexdigest()[:16]
    assert db.email_token(email) == expected
