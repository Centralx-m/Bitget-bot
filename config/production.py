# config/production.py - Production configuration
from utils.constants import Config

prod_config = {
    **Config.__dict__,
    'DEBUG': False,
    'SCAN_INTERVAL_SECONDS': 60,
    'DRY_RUN': False
}