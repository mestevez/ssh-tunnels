import logging
from pathlib import Path

import paramiko

from src.known_hosts import refresh_known_host


def register_public_key_on_bastion(
    ssh_host: str,
    ssh_user: str,
    ssh_key_path: str,
    ssh_key_passphrase: str,
    ssh_pub_key_path: str,
    ssh_port: int = 22,
) -> None:
    """Push the local public key into ~/.ssh/authorized_keys on the bastion.

    Fully OS-independent: uses paramiko directly with no subprocess calls.
    Equivalent to what ssh-keys.sh was doing manually:
      ssh user@bastion "mkdir -p ~/.ssh && grep -qxF '<pubkey>' authorized_keys || echo '<pubkey>' >> authorized_keys"
    """
    pub_key_path = Path(ssh_pub_key_path).expanduser()
    if not pub_key_path.exists():
        raise FileNotFoundError(f"Public key not found: {pub_key_path}")

    pub_key_content = pub_key_path.read_text().strip()

    # Refresh known_hosts via paramiko (no ssh-keyscan subprocess)
    refresh_known_host(ssh_host, ssh_port)

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    key_path = str(Path(ssh_key_path).expanduser())
    passphrase = ssh_key_passphrase or None

    logging.info(f"Connecting to bastion {ssh_host} to register public key ...")
    client.connect(
        hostname=ssh_host,
        port=ssh_port,
        username=ssh_user,
        key_filename=key_path,
        passphrase=passphrase,
        allow_agent=True,   # fall back to ssh-agent if key_filename auth fails
        look_for_keys=True, # also search ~/.ssh for usable keys
    )

    try:
        # This command runs on the remote bastion (always Linux),
        # so Unix shell syntax here is intentional and OS-independent locally.
        remote_cmd = (
            "mkdir -p ~/.ssh && "
            "touch ~/.ssh/authorized_keys && "
            "chmod 700 ~/.ssh && "
            "chmod 600 ~/.ssh/authorized_keys && "
            f"grep -qxF '{pub_key_content}' ~/.ssh/authorized_keys || "
            f"echo '{pub_key_content}' >> ~/.ssh/authorized_keys"
        )
        _, stdout, stderr = client.exec_command(remote_cmd)
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            logging.info(f"Public key successfully registered on {ssh_host}")
        else:
            error = stderr.read().decode().strip()
            raise RuntimeError(
                f"Failed to register public key on {ssh_host}: {error}"
            )
    finally:
        client.close()
