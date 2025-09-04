import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any
from loguru import logger

# Configuración
DB_PATH = Path("data/bot.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# El logger se importa desde config.py y ya está configurado con loguru


def init_db():
    """Inicializa la base de datos con una tabla nueva si no existe."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_config (
            user_id INTEGER PRIMARY KEY,
            api_key TEXT,
            base_url TEXT,
            model_name TEXT,
            system_prompt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar DB: {str(e)}")
        raise
    finally:
        conn.close()


def set_user_config(user_id: int, key: str, value: Any) -> bool:
    """
    Guarda una configuración de usuario.
    Retorna True si tuvo éxito, False si falló.
    """
    valid_keys = {"api_key", "base_url", "model_name", "system_prompt"}
    if key not in valid_keys:
        logger.error(f"Intento de guardar clave inválida: {key}")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar si el usuario existe
        cursor.execute("SELECT 1 FROM user_config WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()

        if exists:
            # Actualizar
            cursor.execute(
                f"UPDATE user_config SET {key} = ? WHERE user_id = ?", (value, user_id)
            )
        else:
            # Insertar nuevo
            cursor.execute(
                f"INSERT INTO user_config (user_id, {key}) VALUES (?, ?)",
                (user_id, value),
            )

        conn.commit()
        logger.info(f"Configuración guardada para usuario {user_id}: {key}")
        return True

    except Exception as e:
        logger.error(f"Error al guardar configuración: {str(e)}")
        return False
    finally:
        conn.close()


def get_user_config(user_id: int) -> Dict[str, Optional[str]]:
    """Obtiene la configuración de un usuario."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acceso como diccionario
        cursor = conn.cursor()

        # Verificar que la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_config'")
        if not cursor.fetchone():
            logger.warning(f"Tabla user_config no existe en {DB_PATH}")
            return {}

        cursor.execute(
            "SELECT api_key, base_url, model_name, system_prompt "
            "FROM user_config WHERE user_id = ?",
            (user_id,),
        )

        row = cursor.fetchone()
        if row:
            config = dict(row)
            logger.info(f"Configuración obtenida para usuario {user_id}: {config}")
            return config
        else:
            logger.info(f"No se encontró configuración para usuario {user_id}")
            return {}

    except Exception as e:
        logger.error(f"Error al obtener configuración para usuario {user_id}: {str(e)}", exc_info=True)
        return {}
    finally:
        conn.close()


def close_db():
    """Función de compatibilidad."""
    pass
