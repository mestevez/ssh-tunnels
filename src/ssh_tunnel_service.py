import logging
import socket

from sshtunnel import SSHTunnelForwarder

from src.config import load_environment_variables
from src.tunnel_model import TunnelConfig, TunnelStatus


def _build_tunnel_instance(
    ssh_host: str,
    ssh_port: int,
    ssh_user: str,
    ssh_key_path: str,
    ssh_key_passphrase: str,
    remote_host: str,
    remote_port: int,
    local_port: int
) -> SSHTunnelForwarder:
    return SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_pkey=ssh_key_path,
        allow_agent=True,
        ssh_private_key_password=ssh_key_passphrase,
        remote_bind_address=(remote_host, remote_port),
        local_bind_address=("127.0.0.1", local_port),
    )

def initialize_ssh_tunnel(
    ssh_host: str,
    ssh_port: int,
    ssh_user: str,
    ssh_key_path: str,
    ssh_key_passphrase: str,
    remote_host: str,
    remote_port: int,
    local_port: int
):
    tunnel = _build_tunnel_instance(
        ssh_host=ssh_host,
        ssh_port=ssh_port,
        ssh_user=ssh_user,
        ssh_key_path=ssh_key_path,
        ssh_key_passphrase=ssh_key_passphrase,
        remote_host=remote_host,
        remote_port=remote_port,
        local_port=local_port
    )

    tunnel.start()

    logging.info("Tunnel established!")
    logging.info(f"Access the remote service at: http://127.0.0.1:{local_port}")

def is_ssh_tunnel_active(
    tunnel: TunnelConfig
) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", tunnel.local_port))
        return result == 0

def get_ssh_tunnels_status(
        tunnels: list[TunnelConfig]
) -> list[TunnelStatus]:
    return [TunnelStatus(
        name=tunnel.name,
        description=tunnel.description,
        ssh_host=tunnel.ssh_host,
        ssh_port=tunnel.ssh_port,
        remote_host=tunnel.remote_host,
        remote_port=tunnel.remote_port,
        local_port=tunnel.local_port,
        enabled=tunnel.enabled,
        tags=tunnel.tags,
        active=is_ssh_tunnel_active(tunnel)
    ) for tunnel in tunnels]


def print_ssh_tunnels_status(tunnels: list[TunnelStatus]) -> None:
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    print("== SSH Tunnels Status ==")
    for tunnel in tunnels:
        status_label = "ACTIVE" if tunnel.active else "INACTIVE"
        status_colour = GREEN if tunnel.active else RED
        status = f"{status_colour}{status_label}{RESET}"
        enabled_status = "ENABLED" if tunnel.enabled else "DISABLED"
        print(f"{tunnel.name}: {tunnel.remote_host}:{tunnel.remote_port} -> {tunnel.local_port} - {status} ({enabled_status})")

def start_ssh_tunnels(
        tunnels: list[TunnelConfig],
        ssh_user: str,
        ssh_key_path: str,
        ssh_key_passphrase: str
):
    for tunnel_config in tunnels:
        if tunnel_config.enabled:
            logging.info("Starting tunnel: %s - %s", tunnel_config.name, tunnel_config.description)
            try:
                initialize_ssh_tunnel(
                    ssh_host=tunnel_config.ssh_host,
                    ssh_port=tunnel_config.ssh_port,
                    ssh_user=ssh_user,
                    ssh_key_path=ssh_key_path,
                    ssh_key_passphrase=ssh_key_passphrase,
                    remote_host=tunnel_config.remote_host,
                    remote_port=tunnel_config.remote_port,
                    local_port=tunnel_config.local_port
                )
            except Exception as e:
                logging.error(f"Failed to start tunnel {tunnel_config.name}: {e}")
        else:
            logging.warning(f"Skipping inactive tunnel: {tunnel_config.name}")
    input("Press Enter to exit...")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config_envs = load_environment_variables()
    sample_tunnels = [
        TunnelConfig(
            name="Cortellis Search OS",
            description="...",
            ssh_host="bastion-ad.eu-west-1.dev.cortellis.aws.clarivate.net",
            ssh_port=22,
            remote_host="cortellis-ls-search-os.stable.cortellis.dev-cortellis.com",
            remote_port=8080,
            local_port=9088,
            enabled=True,
            tags=[]
        )
    ]

    # start_ssh_tunnels(
    #     ssh_user=config_envs.ssh_user,
    #     ssh_key_path=config_envs.ssh_key_path,
    #     ssh_key_passphrase=config_envs.ssh_key_passphrase,
    #     tunnels=sample_tunnels
    # )
    tunnel_status = get_ssh_tunnels_status(
        tunnels=sample_tunnels
    )
    print_ssh_tunnels_status(tunnel_status)
