import os
import sys
import importlib
import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Provide a Flask test client using a temporary SQLite DB.

    Sets `AK_DB` env var before importing/reloading `app` so the app
    initializes its DB at the temporary path.
    """
    db_path = tmp_path / "test_heart_predictions.db"
    monkeypatch.setenv('AK_DB', str(db_path))
    # Enable Razorpay mock mode and provide placeholder keys for tests
    monkeypatch.setenv('RAZORPAY_MOCK', '1')
    monkeypatch.setenv('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
    monkeypatch.setenv('RAZORPAY_KEY_SECRET', 'placeholder_secret')

    # Ensure we import or reload the app after AK_DB is set
    if 'app' in sys.modules:
        importlib.reload(sys.modules['app'])
        app_mod = sys.modules['app']
    else:
        app_mod = importlib.import_module('app')

    app = getattr(app_mod, 'app')
    # Enable testing mode so exceptions propagate to pytest for easier debugging
    app.testing = True
    # Ensure exceptions are propagated (helps pytest show tracebacks)
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # Try to initialize DB schema for the temporary DB
    try:
        if hasattr(app_mod, 'init_db'):
            app_mod.init_db()
    except Exception:
        # If init fails, tests may still run using lazy creation
        pass

    with app.test_client() as c:
        yield c
