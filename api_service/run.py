"""
API server entry point.
"""

from app.main import create_app
from app.config import config

if __name__ == '__main__':
    app = create_app()
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║     EmberAlert API Server                    ║
    ║     http://{config.HOST}:{config.PORT}                   ║
    ╚══════════════════════════════════════════════╝
    """)
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )