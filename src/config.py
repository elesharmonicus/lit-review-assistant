import tomllib
from pathlib import Path

def load_config(config_path: Path = None) -> dict:
    """Load configuration from a TOML file."""
    config_path = config_path or (Path(__file__).parent.parent / "config.toml")
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}

DATA_DIR = Path(__file__).parent.parent / "data"
