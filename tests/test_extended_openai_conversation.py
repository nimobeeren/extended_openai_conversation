import os
from dataclasses import dataclass

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.components import conversation
from homeassistant.core import Context


from custom_components.extended_openai_conversation import OpenAIAgent
from custom_components.extended_openai_conversation.const import DOMAIN
from custom_components.extended_openai_conversation.config_flow import DEFAULT_OPTIONS


@dataclass
class MockConfig:
    location_name: str = "Home"

class MockBus:
    def async_fire(self, event_type, event_data):
        pass

@dataclass
class MockHomeAssistant:
    config: MockConfig
    data: dict
    bus: MockBus


ENTRY = ConfigEntry(
    version=0,
    minor_version=0,
    domain=DOMAIN,
    title="test",
    data={CONF_API_KEY: os.environ["OPENAI_API_KEY"], **DEFAULT_OPTIONS},
    source="test",
    options={},
)

HASS = MockHomeAssistant(config=MockConfig(), data={}, bus=MockBus())


@pytest.fixture
def agent(monkeypatch):
    agent = OpenAIAgent(hass=HASS, entry=ENTRY)
    monkeypatch.setattr(agent, "get_exposed_entities", lambda: [])
    return agent


def test_init(agent):
    # Sanity check: the agent should have an async_process method
    assert callable(agent.async_process)


@pytest.mark.asyncio
async def test_process(agent):
    input = conversation.ConversationInput(
        text="Hello world!",
        context=Context(),
        conversation_id=None,
        device_id=None,
        language="en",
    )
    result = await agent.async_process(input)
    assert len(result.response.speech['plain']['speech']) > 0
