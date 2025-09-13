#!/usr/bin/env python3
"""
Startup script for FastAPI server
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path to access Django models
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'regisbridge.settings.base')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
