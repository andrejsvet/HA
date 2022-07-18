"""Support for PCA 301 smart switch."""
from __future__ import annotations

import logging
import random
import pypca
import json
import paho.mqtt.publish as publish
from serial import SerialException

from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_PORT
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "PCA301"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the PCA switch platform."""

    if discovery_info is None:
        return

    serial_device = discovery_info["device"]

    try:
        pca = pypca.PCA(serial_device)
        pca.open()

        entities = [SmartPlugSwitch(pca, device,discovery_info) for device in pca.get_devices()]
        add_entities(entities, True)

    except SerialException as exc:
        _LOGGER.warning("Unable to open serial port: %s", exc)
        return

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, pca.close)

    pca.start_scan()


class SmartPlugSwitch(SwitchEntity):
    """Representation of a PCA Smart Plug switch."""

    def __init__(self, pca, device_id, discovery_info):
        """Initialize the switch."""
        self._device_id = device_id
        self._name = "PCA301"+device_id
        self._state = None
        self._available = True
        self._pca = pca
        self._host = discovery_info["host"]
        self._port = discovery_info["port"]
        self._user = discovery_info["username"]
        self._pass = discovery_info["password"]
        
    @property
    def name(self):
        """Return the name of the Smart Plug, if any."""
        return self._name

    @property
    def available(self) -> bool:
        """Return if switch is available."""
        return self._available

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._pca.turn_on(self._device_id)

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._pca.turn_off(self._device_id)

    def update(self):
        """Update the PCA switch's state."""
        try:
            datajson = {}
            datajson["power"] = f"{self._pca.get_current_power(self._device_id):.1f}"
            datajson["consumption"] = f"{self._pca.get_total_consumption(self._device_id):.2f}"
            self._state = self._pca.get_state(self._device_id)
            datajson["state"] = self._state
            self.write_mqtt(self._device_id,datajson)
            self._available = True

        except (OSError) as ex:
            if self._available:
                _LOGGER.warning("Could not read state for %s: %s", self.name, ex)
                self._available = False
                
    def write_mqtt(self,deviceid,output):
        """Write mqtt."""
        mqtt_topic='elvpca/'+deviceid
        mqtt_clientid = f'python-mqtt-{random.randint(0, 1000)}'
        mqtt_auth = { 'username': self._user, 'password': self._pass }
        mqtt_url = self._host
        mqtt_port = int(self._port)
        publish.single(mqtt_topic,json.dumps(output),qos=0,retain=True,hostname=mqtt_url,port=mqtt_port,client_id=mqtt_clientid,keepalive=60,will=None, auth=mqtt_auth,tls=None)
        return
