# Installation

## Create a virtual environment

```bash
python3 -m venv ./venv
source ./venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Set up environment

### Environment variables
Clone the `config/config.env.example` file to `config/config.env` and fill in the required environment variables.

- `SSH_USER`: The username for SSH connections to the remote server.
- `SSH_KEY_PATH`: The file path to the SSH private key used for authentication. (e.g., `~/.ssh/id_rsa`)
- `SSH_KEY_PASSPHRASE`: The passphrase for the SSH private key, if applicable. If the key does not have a passphrase, this can be left empty.


### Tunnels configuration
TODO

## Run the application

### Show available commands
```bash
python -m src.main --help
```

### Show tunnel status (filtered by tags)
```bash
python -m src.main tunnels status --tags=cri
```

### Start tunnels (filtered by tags)
```bash
python -m src.main tunnels start --tags=cri
```

### Repair tunnels (filtered by tags)
```bash
python -m src.main tunnels repair --tags=cri
```