class TunnelConfig:
    def __init__(self, name, description, ssh_host, ssh_port, remote_host, remote_port, local_port, enabled=True, tags=None):
        self.name = name
        self.description = description
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.enabled = enabled
        self.tags = tags or []

class TunnelStatus:
    def __init__(self, name, description, ssh_host, ssh_port, remote_host, remote_port, local_port, enabled, tags, active):
        self.name = name
        self.description = description
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.enabled = enabled
        self.active = active
        self.tags = tags