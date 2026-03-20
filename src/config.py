import os

import yaml

from src.env_model import EnvironmentConfig
from src.tunnel_model import TunnelConfig


def load_environment_variables() -> EnvironmentConfig:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, "../config/config.env")

    file_vars: dict[str, str] = {}
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Environment config file not found: {env_path}")

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                file_vars[key.strip()] = value.strip()

    def get_var(name: str) -> str:
        return os.environ.get(name, file_vars.get(name, ""))

    return EnvironmentConfig(
        ssh_user=get_var("SSH_USER"),
        ssh_password=get_var("SSH_PASSWORD"),
        ssh_key_path=get_var("SSH_KEY_PATH"),
        ssh_pub_key_path=get_var("SSH_PUB_KEY_PATH"),
        ssh_key_passphrase=get_var("SSH_KEY_PASSPHRASE"),
    )

def load_tunnels(tags: list[str]) -> list[TunnelConfig]:
    tunnels_config: list[TunnelConfig] = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    global_path = os.path.join(current_dir, f"../config/tunnels.yaml")

    with open(global_path) as f:
        config = yaml.safe_load(f)

    for tunnel in config.get("tunnels", []):
        tunnel_tags = tunnel.get("tags", [])
        if all(tag in tunnel_tags for tag in tags):
            tunnels_config.append(TunnelConfig(
                name=tunnel.get("name", ""),
                description=tunnel.get("description", ""),
                ssh_host=tunnel.get("ssh_host", ""),
                ssh_port=tunnel.get("ssh_port", 22),
                remote_host=tunnel.get("remote_host", ""),
                remote_port=tunnel.get("remote_port", 0),
                local_port=tunnel.get("local_port", 0),
                enabled=tunnel.get("enabled", True),
                tags=tunnel_tags
            ))

    return tunnels_config

if __name__ == "__main__":
    tunnels = load_tunnels(["cri", "snapshot"])
    for tunnel in tunnels:
        print(f"Loaded tunnel: {tunnel.name} with tags {tunnel.description}")