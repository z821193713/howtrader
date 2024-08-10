"""
Global setting of VN Trader.
"""
import os
from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone

from .utility import load_json

SETTINGS: Dict[str, Any] = {
    "font.family": "Arial",
    "font.size": 12,
    "order_update_interval": 120,
    "position_update_interval": 120,
    "account_update_interval": 120,
    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "database.driver": "doris",
    "database.database": "howtraderdb",
    "database.host": "172.28.13.216",
    "database.port": 9030,
    "database.user": "root",
    "database.password": "!qaz@wsx#edc$rfv",

    "database.timezone": get_localzone().zone,
    "database.authentication_source": "admin",  # for mongodb
}

# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
