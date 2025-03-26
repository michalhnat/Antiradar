import asyncio
import sys
import os
import logging

project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(project_root)

from backend.app.services.AsyncRunner import main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

asyncio.run(main())
