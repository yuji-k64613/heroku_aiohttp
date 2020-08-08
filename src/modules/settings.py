import pathlib
import yaml

def get_config():
    BASE_DIR = pathlib.Path(__file__).parent.parent.parent
    config_path = BASE_DIR / 'config' / 'server.yaml'

    with open(config_path) as f:
        config = yaml.safe_load(f)
        return config
