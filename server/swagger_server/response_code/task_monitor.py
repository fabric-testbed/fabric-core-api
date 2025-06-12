from time import sleep


def check_sshkey_expiry_and_email(app):
    """Example of how to send server generated events to clients."""
    with app.app_context():
        while True:
            print('*** background_thread ***')
            # sleep(10)
