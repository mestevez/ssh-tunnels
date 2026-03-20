class EnvironmentConfig:
    def __init__(self, ssh_user, ssh_password, ssh_key_path, ssh_pub_key_path, ssh_key_passphrase):
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_key_path = ssh_key_path
        self.ssh_pub_key_path = ssh_pub_key_path
        self.ssh_key_passphrase = ssh_key_passphrase
