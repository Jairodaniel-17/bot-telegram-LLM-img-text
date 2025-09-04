from bot.database import set_user_config, get_user_config


def test_set_and_get_user_config_in_memory(in_memory_db):
    user_id = 123
    assert set_user_config(user_id, "api_key", "sk-123")
    assert set_user_config(user_id, "base_url", "https://api.test/v1")
    assert set_user_config(user_id, "model_name", "gpt-4-turbo")
    assert set_user_config(user_id, "system_prompt", "hola")

    cfg = get_user_config(user_id)
    assert cfg["api_key"] == "sk-123"
    assert cfg["base_url"] == "https://api.test/v1"
    assert cfg["model_name"] == "gpt-4-turbo"
    assert cfg["system_prompt"] == "hola"
