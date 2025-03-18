from configparser import ConfigParser
from typing import Any
from pathlib import Path

DEFAULT_CONFIG = {
    'GENERAL': {
        'log_level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    },
}


class Config:
    def __init__(self, config_file: Path):
        self.config = ConfigParser()
        self._validate_config(config_file)
        self.config.read(config_file)

    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """Get a configuration value."""
        return self.config.get(section, option, fallback=fallback)

    def set(self, section: str, option: str, value: str):
        """Set a configuration value."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, value)

    def save(self, config_file: str):
        """Save the configuration to a file."""
        with open(config_file, 'w') as f:
            self.config.write(f)

    def _validate_config(self, config_file):
        """Validate the configuration file, creating it if it doesn't exist."""
        if not config_file.exists():
            self._create_default_config(config_file)

    def _create_default_config(self, config_file):
        """Create a default configuration file."""
        self.config.read_dict(DEFAULT_CONFIG)
        with open(config_file, 'w') as f:
            self.config.write(f)
        print(f"Default configuration created at {config_file}.")
