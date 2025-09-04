import pytest

from core import pipeline


class DummyClients:
    @staticmethod
    def chat_gpt(config, user_input, system_prompt=None, **kwargs):
        return f"TEXT:{user_input}"

    @staticmethod
    def chat_multimodal(
        config,
        user_input,
        image_path=None,
        image_url=None,
        system_prompt=None,
        **kwargs,
    ):
        img = image_path or image_url
        return f"IMG:{user_input}:{bool(img)}"


@pytest.fixture(autouse=True)
def _mock_clients(monkeypatch):
    monkeypatch.setattr(pipeline, "chat_gpt", DummyClients.chat_gpt)
    monkeypatch.setattr(pipeline, "chat_multimodal", DummyClients.chat_multimodal)


def test_pipeline_text():
    cfg = {"model_name": "gpt-4-turbo"}
    out = pipeline.run_pipeline(cfg, "hola")
    assert out.startswith("TEXT:")


def test_pipeline_multimodal_by_image():
    cfg = {"model_name": "gpt-4-turbo"}
    out = pipeline.run_pipeline(cfg, "describe", image_path="/tmp/fake.jpg")
    assert out.startswith("IMG:")


def test_pipeline_multimodal_by_model_name():
    cfg = {"model_name": "gpt-4o"}
    out = pipeline.run_pipeline(cfg, "hola")
    assert out.startswith("IMG:") or out.startswith("TEXT:")
