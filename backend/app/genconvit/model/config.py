import os
import yaml

def load_config():
    # Lấy đường dẫn tuyệt đối đến file config.yaml
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config
