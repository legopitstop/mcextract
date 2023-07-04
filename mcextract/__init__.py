__version__ = '1.0.0'

from .server import Server, Status, StatusEvent
from .client import CTkClient

if __name__== '__main__':
    app=Server.from_args()
    app.run()