__version__ = '1.0.0'

from .server import Server

if __name__== '__main__':
    app=Server.from_args()
    app.run()