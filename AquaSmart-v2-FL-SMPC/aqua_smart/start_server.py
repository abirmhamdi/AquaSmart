"""
AquaSmart server launcher.
IMPORTANT: Do NOT import numpy/sklearn before this script starts uvicorn.
           The asyncio event loop must be created before any BLAS code runs
           (Windows IOCP + OpenMP thread pool conflict).
"""
import sys, os, asyncio

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

# Start uvicorn with the app passed as a string.
# Uvicorn will import app.main AFTER asyncio starts (inside srv.serve()),
# which is the correct order: event loop first, BLAS second.
import uvicorn

print("=" * 55)
print("  AquaSmart - Intelligent Fish Feeding System")
print("  http://localhost:8000")
print("=" * 55)

uvicorn.run(
    'app.main:app',
    host='0.0.0.0',
    port=8000,
    reload=False,
    log_level='info',
)
