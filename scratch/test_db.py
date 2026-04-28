import sys
import os
sys.path.append(os.getcwd())
from app.database.db import engine
try:
    with engine.connect() as conn:
        print("Connection success!")
except Exception as e:
    print(f"Connection failed: {e}")
