# Bot de Telegram para interacción con LLM (texto e imágenes)

Este proyecto es un bot de Telegram construido con `python-telegram-bot` 20.x que permite chatear con modelos de lenguaje (LLM) y, opcionalmente, enviar imágenes para análisis con modelos multimodales. La configuración por usuario (API Key, Base URL, modelo y system prompt) se guarda en SQLite.

### Características
- **Comandos de configuración por usuario**: `/set_api_key`, `/set_base_url`, `/set_model`, `/set_system_prompt`, `/config_status`.
- **Soporte multimodal**: envía una foto y el bot usará el pipeline adecuado.
- **Persistencia en SQLite**: `data/bot.db` guarda la configuración de cada usuario.
- **Logging estructurado** con `loguru`, a consola y a `bot.log`.
- **Diseño extensible**: capa `core/` con clientes LLM y un `pipeline` que selecciona automáticamente el flujo (texto o multimodal).
- **Sistema de seguridad**: módulo `bot/security/` con validadores, rate limiting y sanitización de inputs usando patrones GoF (Composite, Strategy).

---

### Requisitos
- Python 3.10+
- Cuenta y API Key del proveedor LLM (por ejemplo, OpenAI-compatible)
- Token de bot de Telegram

Dependencias (archivo `requirements.txt`):
```
python-telegram-bot==20.7
python-dotenv==1.0.1
requests==2.31.0
openai
pytest
pytest-asyncio
pytest-mock
loguru
```

---

### Estructura del proyecto
```
BOTELEGRAM/
  bot/
    config.py
    database.py
    security/
      __init__.py
      guards.py
      sanitizers.py
    handlers/
      commands.py
      messages.py
      callbacks.py
    main.py
  core/
    llm_clients.py
    pipeline.py
  data/
    bot.db
  tests/
    conftest.py
    test_guards.py
    test_database.py
    test_pipeline.py
  requirements.txt
  README.md
  bot.log
```

---

### Configuración
1) Crea un archivo `.env` en la raíz del proyecto con al menos:
```
TELEGRAM_TOKEN=tu_token_de_telegram
# Opcional: nivel de logs (DEBUG, INFO, WARNING, ERROR)
LOGGER_LEVEL=INFO
```

2) Instala dependencias (Windows PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3) Ejecuta el bot:
```powershell
# Opción 1: Usar el launcher desde la raíz del proyecto
python run_bot.py

# Opción 2: Ejecutar como módulo
python -m bot.main

# Opción 3: Ejecutar desde el directorio bot (no recomendado)
cd bot
python main.py
```

**Nota**: Se recomienda usar `python run_bot.py` desde la raíz del proyecto para evitar problemas de importación.

El bot iniciará polling y mostrará logs en consola y en `bot.log`.

---

### Testing
Para ejecutar la suite de pruebas:

```powershell
pytest -q
```

Los tests cubren:
- **Módulo de seguridad**: validación de rate limiting, longitud de mensajes, tamaño de imágenes, filtros de contenido y spam de comandos.
- **Base de datos**: operaciones CRUD de configuración de usuario.
- **Pipeline LLM**: selección automática entre clientes de texto y multimodal.

La configuración de tests usa SQLite en memoria y mocks para clientes LLM externos.

---

### Uso en Telegram
Una vez iniciado el bot:
- Envía `/start` para ver la ayuda y el menú.
- Configura tus credenciales y preferencias con los comandos:
  - `/set_api_key <tu_api_key>`
  - `/set_base_url <https://tu.base.url/v1>`
  - `/set_model <nombre_modelo>` (ej. `gpt-4o` o `gpt-4-turbo`)
  - `/set_system_prompt <mensaje>`
  - `/config_status` para ver el estado actual

Luego, envía mensajes de texto y/o fotos. Si envías una foto, el bot usará el flujo multimodal. Si no incluyes texto con la foto, el bot usará por defecto: "Describe la imagen".

---

### Detalles técnicos
- `bot/main.py`: Inicializa base de datos, registra handlers, configura comandos y arranca el polling.
- `bot/handlers/commands.py`: Implementa los comandos de configuración y estado.
- `bot/handlers/messages.py`: Orquesta la recepción de texto/fotos, descarga imágenes a temporales seguros y llama al `pipeline`.
- `bot/handlers/callbacks.py`: Maneja botones de interfaz simple (callback queries).
- `bot/database.py`: Crea `data/bot.db` y ofrece helpers para guardar/leer configuración por usuario.
- `core/pipeline.py`: Decide si llama a cliente de **texto** o **multimodal** según el modelo o si hay imagen.
- `core/llm_clients.py`: Clientes basados en `openai` (compatible con servidores OpenAI-like) para texto y multimodal.
- `bot/security/guards.py`: Implementa validadores de seguridad usando el patrón Composite (CompositeGuard) y Strategy (diferentes tipos de Guard).
- `bot/security/sanitizers.py`: Sanitización de texto usando Composite pattern para aplicar múltiples filtros secuencialmente.

Notas sobre proveedores:
- El bot no impone un proveedor específico; usa `OpenAI(api_key, base_url)`.
- Ajusta `/set_base_url` si usas un endpoint compatible distinto a `https://api.openai.com/v1`.
- Asegúrate de elegir un `/set_model` que tu proveedor soporte (p. ej., `gpt-4o` para multimodal, `gpt-4-turbo` para texto).

---

### Variables y base de datos
- `.env`: `TELEGRAM_TOKEN` es obligatorio. `LOGGER_LEVEL` opcional.
- `data/bot.db`: SQLite con la tabla `user_config` que almacena `api_key`, `base_url`, `model_name`, `system_prompt` por `user_id` de Telegram.
- Los logs se escriben en `bot.log` con rotación de 10 MB y retención de 10 días.

---

### Características de seguridad
El bot incluye múltiples capas de protección:

- **Rate Limiting**: máximo 6 mensajes por usuario en ventana de 10 segundos.
- **Validación de contenido**: longitud máxima de 4000 caracteres, filtro de lenguaje ofensivo.
- **Control de imágenes**: tamaño máximo de 5 MB, validación antes de descarga.
- **Anti-spam**: cooldown de 2 segundos entre comandos del mismo usuario.
- **Sanitización**: eliminación de caracteres de control y trimming automático.

---

### Solución de problemas
- "TELEGRAM_TOKEN no definido": agrega `TELEGRAM_TOKEN` al `.env` en la raíz.
- Errores de autenticación LLM: verifica `/set_api_key` y, si usas un servidor compatible, fija `/set_base_url` correcto.
- El modelo no responde a imágenes: asegúrate de usar un modelo multimodal (p. ej., `gpt-4o`) y que el proveedor lo soporte.
- Permisos de PowerShell al activar venv: ejecuta PowerShell como administrador o ajusta la ExecutionPolicy temporalmente:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
- Tests fallan con "ModuleNotFoundError": asegúrate de ejecutar desde la raíz del proyecto y tener `__init__.py` en `bot/` y `core/`.

---

### Desarrollo y contribución
1) Clona el repo y crea tu rama.
2) Crea un entorno virtual e instala dependencias.
3) Ejecuta `python bot/main.py` y prueba con tu bot.
4) Ejecuta `pytest -q` para verificar que los tests pasen.
5) Envía PRs con descripciones claras. Mantén el estilo y tipado existente.

---

### Licencia
Este proyecto se distribuye con fines educativos. Ajusta la licencia según tus necesidades.

---

### Patrones de diseño implementados
- **Composite**: `CompositeGuard` y `CompositeSanitizer` permiten combinar múltiples validadores/sanitizadores.
- **Strategy**: Diferentes implementaciones de `Guard` y `Sanitizer` intercambiables.
- **Chain of Responsibility**: Los guards se ejecutan secuencialmente hasta encontrar la primera violación.


