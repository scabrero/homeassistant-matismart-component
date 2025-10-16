"""Constants for the Matis integration."""

from enum import IntEnum, auto

from pymatis.constants import Baudrate, Parity, StopBits


class DeviceType(IntEnum):
    """Type of device."""

    SERIAL = auto()
    NETWORK = auto()


DOMAIN = "matismart"
DEFAULT_NAME = "Matismart"
DEFAULT_SCAN_INTERVAL = 10

CONF_HARDWARE_ID = "hardware_id"
CONF_SERIAL_CONFIG = "serial_config"
CONF_SERIAL_BAUDRATE = "serial_baudrate"
CONF_SERIAL_PARITY = "serial_parity"
CONF_SERIAL_STOPBITS = "serial_stopbits"

CONF_DEFAULT_TYPE = DeviceType.NETWORK
CONF_DEFAULT_HOST = "192.168.31.102"
CONF_DEFAULT_PORT = 502
CONF_DEFAULT_MODBUS_ADDRESS = 53
CONF_DEFAULT_BAUDRATE = Baudrate.BAUD_9600
CONF_DEFAULT_PARITY = Parity.PARITY_EVEN
CONF_DEFAULT_STOPBITS = StopBits.STOP_1
