__API_VERSION__ = '1.6.1'
__API_REFERENCE__ = 'https://github.com/fabric-testbed/fabric-core-api'

from pathlib import Path

from dotenv import load_dotenv

# load environment variables
env_path = Path('../../') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)
