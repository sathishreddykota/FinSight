import os
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from backend.api.main import app

# For Vercel Functions
async def handler(request):
    """ASGI handler for Vercel Functions"""
    return app
