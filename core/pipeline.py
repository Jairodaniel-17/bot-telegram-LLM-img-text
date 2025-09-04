from core.llm_clients import chat_gpt, chat_multimodal
from typing import Dict, Optional, Union
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def run_pipeline(
    config: Dict,
    user_input: str,
    image_path: Optional[Union[str, Path]] = None,
    image_url: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Ejecuta el pipeline de LLM seleccionando automáticamente el cliente adecuado.

    Args:
        config: Diccionario de configuración que debe incluir:
            - model_name: Nombre del modelo a usar
            - api_key: Clave API (opcional si está en entorno)
            - base_url: URL base de la API (opcional)
        user_input: Texto de entrada del usuario
        image_path: Ruta local a imagen (opcional, para modelos multimodales)
        image_url: URL de imagen (opcional, para modelos multimodales)
        system_prompt: Prompt del sistema (opcional, sobreescribe config)
        **kwargs: Argumentos adicionales para los clientes

    Returns:
        Respuesta del modelo como string

    Raises:
        ValueError: Si la configuración es inválida
        RuntimeError: Si falla la ejecución del modelo
    """
    try:
        # Validar configuración básica
        if not config or "model_name" not in config:
            raise ValueError("Configuración inválida: falta 'model_name'")

        model_name = config["model_name"].lower()

        # Determinar si es multimodal basado en el nombre del modelo o en parámetros
        is_multimodal = any(
            m in model_name for m in ["multimodal", "4o", "vision", "turbo-vision"]
        ) or any([image_path, image_url])

        if is_multimodal:
            logger.info(f"Ejecutando modelo multimodal: {model_name}")
            return chat_multimodal(
                config=config,
                user_input=user_input,
                image_path=image_path,
                image_url=image_url,
                system_prompt=system_prompt,
                **kwargs,
            )
        else:
            logger.info(f"Ejecutando modelo de texto: {model_name}")
            return chat_gpt(
                config=config,
                user_input=user_input,
                system_prompt=system_prompt,
                **kwargs,
            )

    except ValueError as ve:
        logger.error(f"Error de validación: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Error en el pipeline: {str(e)}")
        raise RuntimeError(f"Error al ejecutar el pipeline: {str(e)}")


# # Ejemplo de uso
# if __name__ == "__main__":
#     # Configuración básica
#     config = {
#         "model_name": "gpt-4-turbo",  # Cambiar a "gpt-3.5-turbo" para prueba
#         "api_key": "tu_api_key",
#         "base_url": "https://api.openai.com/v1"
#     }

#     # Caso 1: Texto normal
#     try:
#         response = run_pipeline(config, "Hola, ¿cómo estás?")
#         print("Respuesta texto:", response)
#     except Exception as e:
#         print(f"Error en texto: {e}")

#     # Caso 2: Multimodal con imagen local
#     try:
#         response_img = run_pipeline(
#             config,
#             "¿Qué hay en esta imagen?",
#             image_path="ruta/a/imagen.jpg"
#         )
#         print("Respuesta multimodal:", response_img)
#     except Exception as e:
#         print(f"Error en multimodal: {e}")

#     # Caso 3: Con system prompt personalizado
#     try:
#         response_custom = run_pipeline(
#             config,
#             "Explica este concepto: gravedad cuántica",
#             system_prompt="Eres un físico teórico, explica en términos simples."
#         )
#         print("Respuesta con system prompt:", response_custom)
#     except Exception as e:
#         print(f"Error con system prompt: {e}")
