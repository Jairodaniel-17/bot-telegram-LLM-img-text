import sys
from pathlib import Path
import tempfile
import pytest


# Asegura que la raíz del proyecto esté en sys.path para importar 'bot' y 'core'
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _isolate_tmp_dir(monkeypatch):
    # Asegura que tempfiles no colisionen
    tmpdir = tempfile.mkdtemp(prefix="bot_tests_")
    monkeypatch.setenv("TMPDIR", tmpdir)
    # Compat Windows
    monkeypatch.setenv("TEMP", tmpdir)
    monkeypatch.setenv("TMP", tmpdir)
    yield


@pytest.fixture()
def in_memory_db(monkeypatch, tmp_path):
    # Usa un archivo SQLite temporal compartido por todas las conexiones
    from bot import database as db

    db_path = tmp_path / "test_bot.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.init_db()
    yield
