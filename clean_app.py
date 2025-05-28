import shutil
import os
import sys
from dotenv import load_dotenv

if __name__ == "__main__":

    load_dotenv()

    build_path = os.environ["BUILD_DIR"]
    
    print("🧹 Cleaning project...\n")

    try:
        shutil.rmtree(build_path)
        print("🏁 Cleaned successfully\n")
    except FileNotFoundError:
        print("✅ Already cleaned\n")
    except Exception as e:
        print(f"Unexpected error: {e}\n")
        sys.exit(1)
