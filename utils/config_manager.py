import json
from utils.logger import log

class ConfigManager:
    def __init__(self, config_path='config/settings.json'):
        self.config_path = config_path
        self.settings = {}
        self.load_config()

    def load_config(self):
        """Loads and validates the configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                self.settings = json.load(f)
            log.info(f"Configuration loaded successfully from {self.config_path}")
            self._validate_config()
        except FileNotFoundError:
            log.error(f"Configuration file not found at {self.config_path}. Bot may not function correctly.")
            self.settings = self._get_default_config() # Load defaults as a fallback
        except json.JSONDecodeError:
            log.error(f"Invalid JSON in {self.config_path}. Please check the file format.")
            self.settings = self._get_default_config()

    def _validate_config(self):
        """Validates critical configuration values."""
        if "device" not in self.settings or "adb_device_id" not in self.settings["device"]:
            log.warning("Config validation: 'device.adb_device_id' is not set.")
        if "ai_tiers" not in self.settings:
            log.error("Config validation: 'ai_tiers' section is missing.")
            raise ValueError("Missing critical configuration: ai_tiers")
        # Add more validation rules as needed
        log.info("Configuration validation passed.")

    def get(self, key, default=None):
        """Retrieves a value from the configuration using dot notation."""
        try:
            keys = key.split('.')
            value = self.settings
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            log.warning(f"Config key '{key}' not found. Returning default value: {default}")
            return default

    def _get_default_config(self):
        """Provides a basic default configuration."""
        log.info("Loading fallback default configuration.")
        return {
            "performance": {"target_latency_ms": 500, "max_retry_count": 2},
            "learning": {"similarity_threshold": 0.80, "decay_rate": 0.05},
            "ai_tiers": {
                "TinyLLM": {"enabled": True},
                "GeminiAPI": {"enabled": False, "api_key": ""}
            },
            "device": {"adb_device_id": ""}
        }

# Global instance for easy access from other modules
config = ConfigManager()
