import argparse
import logging

from src.warnings_config import suppress_warnings

suppress_warnings()

from src.bastion import register_public_key_on_bastion
from src.config import load_environment_variables, load_tunnels
from src.ssh_tunnel_service import start_ssh_tunnels
from src.tunnels import get_ssh_tunnels_status, print_ssh_tunnels_status


def parse_tags(tags_arg: str | None) -> list[str]:
    """Parse a comma-separated tags string into a list of tag strings.

    Example:
        parse_tags("cri,snapshot") -> ["cri", "snapshot"]
        parse_tags(None)           -> []
    """
    if not tags_arg:
        return []
    return [tag.strip() for tag in tags_arg.split(",") if tag.strip()]


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="SSH Tunnels CLI")
    subparsers = parser.add_subparsers(dest="resource", required=True)

    # `tunnels` resource
    tunnels_parser = subparsers.add_parser("tunnels", help="Manage SSH tunnels")
    tunnels_subparsers = tunnels_parser.add_subparsers(dest="action", required=True)

    # `tunnels status` command
    status_parser = tunnels_subparsers.add_parser("status", help="Show the status of SSH tunnels")
    status_parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Comma-separated list of tags to filter tunnels (e.g. --tags=cri,snapshot)",
    )

    # `tunnels start` command
    start_parser = tunnels_subparsers.add_parser("start", help="Start SSH tunnels")
    start_parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Comma-separated list of tags to filter tunnels (e.g. --tags=cri,snapshot)",
    )

    # `tunnels repair` command — re-registers the local public key on all bastions
    repair_parser = tunnels_subparsers.add_parser(
        "repair",
        help="Re-register local public key on bastion hosts (fixes authentication failures)",
    )
    repair_parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Comma-separated list of tags to filter tunnels (e.g. --tags=cri,snapshot)",
    )

    args = parser.parse_args()

    if args.resource == "tunnels" and args.action == "status":
        tags = parse_tags(args.tags)
        tunnels = load_tunnels(tags)
        statuses = get_ssh_tunnels_status(
            tunnels=tunnels
        )
        print_ssh_tunnels_status(statuses)

    elif args.resource == "tunnels" and args.action == "start":
        tags = parse_tags(args.tags)
        env = load_environment_variables()
        tunnels = load_tunnels(tags)
        start_ssh_tunnels(
            tunnels=tunnels,
            ssh_user=env.ssh_user,
            ssh_key_path=env.ssh_key_path,
            ssh_key_passphrase=env.ssh_key_passphrase,
        )

    elif args.resource == "tunnels" and args.action == "repair":
        tags = parse_tags(args.tags)
        env = load_environment_variables()
        tunnels = load_tunnels(tags)
        statuses = get_ssh_tunnels_status(
            tunnels=tunnels
        )
        failed_tunnels = [tunnel for tunnel in statuses if tunnel.enabled and not tunnel.active]
        logging.info(f"Found {len(failed_tunnels)} failed tunnels that may require bastion key re-registration.")
        # Deduplicate — many tunnels share the same bastion
        seen_hosts: set[tuple[str, int]] = set()
        for tunnel in failed_tunnels:
            key = (tunnel.ssh_host, tunnel.ssh_port)
            if key in seen_hosts:
                continue
            seen_hosts.add(key)
            register_public_key_on_bastion(
                ssh_host=tunnel.ssh_host,
                ssh_user=env.ssh_user,
                ssh_key_path=env.ssh_key_path,
                ssh_key_passphrase=env.ssh_key_passphrase,
                ssh_pub_key_path=env.ssh_pub_key_path,
                ssh_port=tunnel.ssh_port
            )


if __name__ == "__main__":
    main()
