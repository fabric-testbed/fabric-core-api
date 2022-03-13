__API_VERSION__ = '1.0.0'
__API_REFERENCE__ = 'https://github.com/fabric-testbed/core-api'

from logging.config import dictConfig
from pathlib import Path

from dotenv import load_dotenv

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# load environment variables
env_path = Path('../../') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)
