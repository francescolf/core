"""Tests for the Alexa Devices sensor platform."""

import datetime
from typing import Any
from unittest.mock import AsyncMock, patch

from aioamazondevices.api import AmazonDeviceSensor, AmazonSchedule
from aioamazondevices.exceptions import (
    CannotAuthenticate,
    CannotConnect,
    CannotRetrieveData,
)
from freezegun.api import FrozenDateTimeFactory
import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.alexa_devices.coordinator import SCAN_INTERVAL
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import setup_integration
from .const import TEST_DEVICE_1_SN

from tests.common import MockConfigEntry, async_fire_time_changed, snapshot_platform


async def test_all_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test all entities."""
    with patch("homeassistant.components.alexa_devices.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    "side_effect",
    [
        CannotConnect,
        CannotRetrieveData,
        CannotAuthenticate,
    ],
)
async def test_coordinator_data_update_fails(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    side_effect: Exception,
) -> None:
    """Test coordinator data update exceptions."""

    entity_id = "sensor.echo_test_temperature"

    await setup_integration(hass, mock_config_entry)

    assert (state := hass.states.get(entity_id))
    assert state.state == "22.5"

    mock_amazon_devices_client.get_devices_data.side_effect = side_effect

    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert (state := hass.states.get(entity_id))
    assert state.state == STATE_UNAVAILABLE


async def test_offline_device(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test offline device handling."""

    entity_id = "sensor.echo_test_temperature"

    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].online = False

    await setup_integration(hass, mock_config_entry)

    assert (state := hass.states.get(entity_id))
    assert state.state == STATE_UNAVAILABLE

    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].online = True

    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert (state := hass.states.get(entity_id))
    assert state.state != STATE_UNAVAILABLE


@pytest.mark.parametrize(
    ("sensor", "api_value", "scale", "state_value", "unit"),
    [
        (
            "temperature",
            "86",
            "FAHRENHEIT",
            "30.0",  # State machine converts to °C
            "°C",  # State machine converts to °C
        ),
        ("temperature", "22.5", "CELSIUS", "22.5", "°C"),
        ("illuminance", "800", None, "800", "lx"),
    ],
)
async def test_unit_of_measurement(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
    sensor: str,
    api_value: Any,
    scale: str | None,
    state_value: Any,
    unit: str | None,
) -> None:
    """Test sensor unit of measurement handling."""

    entity_id = f"sensor.echo_test_{sensor}"

    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].sensors = {
        sensor: AmazonDeviceSensor(
            name=sensor,
            value=api_value,
            error=False,
            error_msg=None,
            error_type=None,
            scale=scale,
        )
    }

    await setup_integration(hass, mock_config_entry)

    assert (state := hass.states.get(entity_id))
    assert state.state == state_value
    assert state.attributes["unit_of_measurement"] == unit


async def test_sensor_unavailable(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensor is unavailable."""

    entity_id = "sensor.echo_test_illuminance"

    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].sensors = {
        "illuminance": AmazonDeviceSensor(
            name="illuminance",
            value="800",
            error=True,
            error_msg=None,
            error_type=None,
            scale=None,
        )
    }

    await setup_integration(hass, mock_config_entry)

    assert (state := hass.states.get(entity_id))
    assert state.state == STATE_UNAVAILABLE


async def test_notification_timestamp_sensors(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test sensors created from device notifications (Timer/Alarm/Reminder)."""

    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].notifications = {
        "Timer": AmazonSchedule(
            type="Timer",
            status="ON",
            label="Test timer",
            next_occurrence=datetime.datetime(
                2025,
                1,
                1,
                9,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
            ),
        ),
        "Alarm": AmazonSchedule(
            type="Alarm",
            status="ON",
            label="Test alarm",
            next_occurrence=datetime.datetime(
                2025,
                1,
                1,
                8,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
            ),
        ),
        "Reminder": AmazonSchedule(
            type="Reminder",
            status="ON",
            label="Test reminder",
            next_occurrence=datetime.datetime(
                2025,
                1,
                1,
                12,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
            ),
        ),
    }

    with patch("homeassistant.components.alexa_devices.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    # Check that timestamp sensors exist and have proper attributes
    timer_entity = hass.states.get("sensor.echo_test_next_timer")
    alarm_entity = hass.states.get("sensor.echo_test_next_alarm")
    reminder_entity = hass.states.get("sensor.echo_test_next_reminder")

    assert timer_entity
    assert alarm_entity
    assert reminder_entity

    # native state should be stored in UTC; compare as datetimes
    expected_timer = datetime.datetime(
        2025,
        1,
        1,
        9,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
    ).astimezone(datetime.UTC)
    expected_alarm = datetime.datetime(
        2025,
        1,
        1,
        8,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
    ).astimezone(datetime.UTC)
    expected_reminder = datetime.datetime(
        2025,
        1,
        1,
        12,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=7200), "CEST"),
    ).astimezone(datetime.UTC)

    assert datetime.datetime.fromisoformat(timer_entity.state) == expected_timer
    assert datetime.datetime.fromisoformat(alarm_entity.state) == expected_alarm
    assert datetime.datetime.fromisoformat(reminder_entity.state) == expected_reminder

    # label should be exposed in attributes
    assert timer_entity.attributes.get("label") == "Test timer"
    assert alarm_entity.attributes.get("label") == "Test alarm"
    assert reminder_entity.attributes.get("label") == "Test reminder"


async def test_notification_sensors_empty_cases(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_amazon_devices_client: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test notification sensors behavior when notifications are missing or empty."""

    # Case 1: notifications dict has no Timer/Alarm/Reminder keys -> sensors should be created but state None
    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].notifications = {}

    with patch("homeassistant.components.alexa_devices.PLATFORMS", [Platform.SENSOR]):
        await setup_integration(hass, mock_config_entry)

    timer_entity = hass.states.get("sensor.echo_test_next_timer")
    alarm_entity = hass.states.get("sensor.echo_test_next_alarm")
    reminder_entity = hass.states.get("sensor.echo_test_next_reminder")

    # Entities should exist but have no native value
    assert timer_entity is not None
    assert alarm_entity is not None
    assert reminder_entity is not None

    assert timer_entity.state is STATE_UNKNOWN
    assert alarm_entity.state is STATE_UNKNOWN
    assert reminder_entity.state is STATE_UNKNOWN

    # Case 2: notification objects present but next_occurrence is None
    mock_amazon_devices_client.get_devices_data.return_value[
        TEST_DEVICE_1_SN
    ].notifications = {
        "Timer": AmazonSchedule(
            type="Timer", status="ON", label="No timer", next_occurrence=None
        ),
        "Alarm": AmazonSchedule(
            type="Alarm", status="ON", label="No alarm", next_occurrence=None
        ),
        "Reminder": AmazonSchedule(
            type="Reminder", status="ON", label="No reminder", next_occurrence=None
        ),
    }

    # Trigger coordinator refresh so entities pick up new notification values
    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    timer_entity = hass.states.get("sensor.echo_test_next_timer")
    alarm_entity = hass.states.get("sensor.echo_test_next_alarm")
    reminder_entity = hass.states.get("sensor.echo_test_next_reminder")

    assert timer_entity
    assert alarm_entity
    assert reminder_entity

    assert timer_entity.state is STATE_UNKNOWN
    assert alarm_entity.state is STATE_UNKNOWN
    assert reminder_entity.state is STATE_UNKNOWN
