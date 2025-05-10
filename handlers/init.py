from .start import start_handler
from .login import login_handlers
from .premium import premium_handlers
from .batch import batch_handlers
from .utils import utils_handlers

async def load_handlers(client):
    # Register all handlers
    start_handler(client)
    login_handlers(client)
    premium_handlers(client)
    batch_handlers(client)
    utils_handlers(client)