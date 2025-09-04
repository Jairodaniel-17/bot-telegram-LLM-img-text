from openai import OpenAI
from typing import Dict, Optional, Union
import base64
import mimetypes
from pathlib import Path
import logging

# Configurar logging básico
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


def chat_gpt(
    config: Dict[str, str], user_input: str, system_prompt: Optional[str] = None
) -> str:
    """
    Cliente para modelos GPT que solo procesan texto (GPT-3.5, GPT-4, etc.).

    Args:
        config: Diccionario con:
            - api_key: Clave API de OpenAI
            - base_url: URL base de la API
            - model_name: Nombre del modelo a usar
        user_input: Texto de entrada del usuario
        system_prompt: Opcional, sobreescribe el config["system_prompt"] si existe

    Returns:
        Respuesta del modelo como string

    Raises:
        ValueError: Si falta configuración esencial
        Exception: Para errores de API
    """
    try:
        # Validar configuración mínima
        required_keys = ["api_key", "base_url", "model_name"]
        if not all(k in config for k in required_keys):
            raise ValueError(f"Configuración incompleta. Se requieren: {required_keys}")

        client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

        # Usar system_prompt proporcionado o el de config o uno por defecto
        system_content = system_prompt or config.get(
            "system_prompt", "You are a helpful assistant."
        )

        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_input},
            ],
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error en chat_gpt: {str(e)}")
        raise


def chat_multimodal(
    config: Dict[str, str],
    user_input: str,
    image_path: Optional[Union[str, Path]] = None,
    image_url: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Cliente para modelos multimodales (GPT-4o, etc.) que soportan imágenes.

    Args:
        config: Diccionario con:
            - api_key: Clave API de OpenAI
            - base_url: URL base de la API
            - model_name: Nombre del modelo a usar
        user_input: Texto de entrada del usuario
        image_path: Ruta local a la imagen (opcional, pero se requiere image_path o image_url)
        image_url: URL pública de la imagen (opcional)
        system_prompt: Opcional, sobreescribe el config["system_prompt"] si existe

    Returns:
        Respuesta del modelo como string

    Raises:
        ValueError: Si no se proporciona imagen o hay problemas con la imagen
        Exception: Para errores de API
    """
    try:
        # Validar que haya al menos una imagen
        if not any([image_path, image_url]):
            raise ValueError("Se requiere image_path o image_url para multimodal_chat")

        # Obtener la representación de la imagen (URL o base64)
        image_content = _prepare_image_content(image_path, image_url)

        client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])

        # Usar system_prompt proporcionado o el de config o uno por defecto
        system_content = system_prompt or config.get(
            "system_prompt", "You are a helpful assistant."
        )

        # Construir mensaje multimodal
        messages = [
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": [{"type": "text", "text": user_input}, image_content],
            },
        ]

        response = client.chat.completions.create(
            model=config["model_name"],
            messages=messages,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error en chat_multimodal: {str(e)}")
        raise


def _prepare_image_content(
    image_path: Optional[Union[str, Path]] = None, image_url: Optional[str] = None
) -> Dict:
    """
    Prepara el contenido de imagen para la API, usando URL o base64.

    Args:
        image_path: Ruta local a la imagen
        image_url: URL pública de la imagen

    Returns:
        Diccionario con el contenido de imagen en formato para la API

    Raises:
        ValueError: Si hay problemas con la imagen
    """
    if image_url:
        # Si tenemos URL, usamos esa directamente
        return {"type": "image_url", "image_url": {"url": image_url}}
    else:
        # Si no, codificamos la imagen local en base64
        try:
            path = Path(image_path)
            if not path.exists():
                raise ValueError(f"Archivo no encontrado: {image_path}")

            mime_type, _ = mimetypes.guess_type(path)
            if not mime_type or not mime_type.startswith("image/"):
                raise ValueError(
                    f"El archivo no parece ser una imagen válida: {image_path}"
                )

            with open(path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            return {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
            }
        except Exception as e:
            logger.error(f"Error al procesar imagen: {str(e)}")
            raise ValueError(f"Error al procesar imagen: {str(e)}")
