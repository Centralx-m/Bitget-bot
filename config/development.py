# config/development.py - Development configuration
from utils.constants import Config

dev_config = {
    **Config.__dict__,
    'DEBUG': True,
    'SCAN_INTERVAL_SECONDS': 30,
    'DRY_RUN': True
}