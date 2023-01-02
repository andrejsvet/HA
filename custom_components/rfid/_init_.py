"""The Elv integration."""
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_PORT, CONF_DEVICE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

DOMAIN = "rfid"

DEFAULT_DEVICE = "/dev/ttyUSB0"
DEFAULT_PORT = "1883"

RFID_PLATFORMS = [Platform.sensor]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {vol.Optional(CONF_DEVICE, default=DEFAULT_DEVICE): cv.string,
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.string, 
            vol.Optional(CONF_USERNAME): cv.string,
            vol.Optional(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the RFID sensor platform."""
    #{"device": config[DOMAIN][CONF_DEVICE]}
    paramjson={}
    paramjson["device"]= config[DOMAIN][CONF_DEVICE]
    paramjson["host"]= config[DOMAIN][CONF_HOST]
    paramjson["port"]= config[DOMAIN][CONF_PORT]
    paramjson["username"]= config[DOMAIN][CONF_USERNAME]
    paramjson["password"]= config[DOMAIN][CONF_PASSWORD]
    
    for platform in RFID_PLATFORMS:
        discovery.load_platform(
            hass, platform, DOMAIN, paramjson, config
        )

    return True
