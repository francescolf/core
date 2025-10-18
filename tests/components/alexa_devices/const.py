"""Alexa Devices tests const."""

import datetime

from aioamazondevices.api import AmazonDevice, AmazonDeviceSensor, AmazonSchedule

TEST_CODE = "023123"
TEST_PASSWORD = "fake_password"
TEST_USERNAME = "fake_email@gmail.com"

TEST_DEVICE_1_SN = "echo_test_serial_number"
TEST_DEVICE_1_ID = "echo_test_device_id"
TEST_DEVICE_1 = AmazonDevice(
    account_name="Echo Test",
    capabilities=["AUDIO_PLAYER", "MICROPHONE"],
    device_family="mine",
    device_type="echo",
    household_device=False,
    device_owner_customer_id="amazon_ower_id",
    device_cluster_members=[TEST_DEVICE_1_SN],
    online=True,
    serial_number=TEST_DEVICE_1_SN,
    software_version="echo_test_software_version",
    entity_id="11111111-2222-3333-4444-555555555555",
    endpoint_id="G1234567890123456789012345678A",
    sensors={
        "dnd": AmazonDeviceSensor(
            name="dnd",
            value=False,
            error=False,
            error_msg=None,
            error_type=None,
            scale=None,
        ),
        "temperature": AmazonDeviceSensor(
            name="temperature",
            value="22.5",
            error=False,
            error_msg=None,
            error_type=None,
            scale="CELSIUS",
        ),
    },
    notifications={
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
    },
)

TEST_DEVICE_2_SN = "echo_test_2_serial_number"
TEST_DEVICE_2_ID = "echo_test_2_device_id"
TEST_DEVICE_2 = AmazonDevice(
    account_name="Echo Test 2",
    capabilities=["AUDIO_PLAYER", "MICROPHONE"],
    device_family="mine",
    device_type="echo",
    household_device=True,
    device_owner_customer_id="amazon_ower_id",
    device_cluster_members=[TEST_DEVICE_2_SN],
    online=True,
    serial_number=TEST_DEVICE_2_SN,
    software_version="echo_test_2_software_version",
    entity_id="11111111-2222-3333-4444-555555555555",
    endpoint_id="G1234567890123456789012345678A",
    sensors={
        "temperature": AmazonDeviceSensor(
            name="temperature",
            value="22.5",
            error=False,
            error_msg=None,
            error_type=None,
            scale="CELSIUS",
        )
    },
    notifications={
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
    },
)
