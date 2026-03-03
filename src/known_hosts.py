import logging
from pathlib import Path

import paramiko

_KNOWN_HOSTS_PATH = Path.home() / ".ssh" / "known_hosts"


def remove_known_host(ssh_host: str, ssh_port: int = 22) -> None:
    """Remove all entries for ssh_host from ~/.ssh/known_hosts using paramiko's HostKeys API."""
    if not _KNOWN_HOSTS_PATH.exists():
        return

    host_keys = paramiko.HostKeys(str(_KNOWN_HOSTS_PATH))

    # paramiko stores non-22 ports as "[host]:port"
    lookup_key = f"[{ssh_host}]:{ssh_port}" if ssh_port != 22 else ssh_host

    if lookup_key in host_keys:
        del host_keys[lookup_key]
        host_keys.save(str(_KNOWN_HOSTS_PATH))
        logging.info(f"Removed known_hosts entry for {lookup_key}")
    else:
        logging.debug(f"No known_hosts entry found for {lookup_key}, nothing to remove")


def add_known_host(ssh_host: str, ssh_port: int = 22) -> None:
    """Fetch the current host key via a raw socket and append it to ~/.ssh/known_hosts."""
    transport = paramiko.Transport((ssh_host, ssh_port))
    try:
        transport.connect()
        host_key = transport.get_remote_server_key()
    finally:
        transport.close()

    if host_key is None:
        raise RuntimeError(f"Could not retrieve host key from {ssh_host}:{ssh_port}")

    host_keys = paramiko.HostKeys()
    if _KNOWN_HOSTS_PATH.exists():
        host_keys.load(str(_KNOWN_HOSTS_PATH))

    lookup_key = f"[{ssh_host}]:{ssh_port}" if ssh_port != 22 else ssh_host
    host_keys.add(lookup_key, host_key.get_name(), host_key)

    _KNOWN_HOSTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    host_keys.save(str(_KNOWN_HOSTS_PATH))
    logging.info(f"Added known_hosts entry for {lookup_key} ({host_key.get_name()})")


def refresh_known_host(ssh_host: str, ssh_port: int = 22) -> None:
    """Remove stale entry and re-fetch the current host key for ssh_host."""
    logging.info(f"Refreshing known_hosts for {ssh_host}:{ssh_port} ...")
    remove_known_host(ssh_host, ssh_port)
    add_known_host(ssh_host, ssh_port)

