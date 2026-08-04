from swagger_server.response_code.sshkeys_utils import ssh_key_expiry_check

# ssh key expiry (ske)
def check_sshkey_expiry_and_email(app):
    """Example of how to send server generated events to clients."""
    with app.app_context():
        print("Checking SSH key expiry...")
        ssh_key_expiry_check()
