import subprocess
import os
import sys
from dotenv import load_dotenv
import prepare_images

if __name__ == "__main__":

    load_dotenv()

    app_path = os.environ["APP_PATH"]
    board_root = os.environ["ZEPHYR_BOARD_ROOT"]
    zephyr_sdk_path = os.environ["ZEPHYR_SDK_PATH"]
    prj_conf_path = os.path.join(app_path, "prj.conf")
    build_path = os.environ["BUILD_DIR"]

    print("🛠 Running build FW...\n")

    build_command = [
        f"west",
        f"build",
        f"-b",
        f"pocket_adventurer_dev_board",
        f"{app_path}",
        f"--no-sysbuild",
        f"--build-dir",
        f"{build_path}",
        f"--pristine=auto",
        f"--",
        f"-DBOARD_ROOT={board_root}",
        f"-DZEPHYR_TOOLCHAIN_VARIANT=zephyr",
        f"-DZEPHYR_SDK_INSTALL_DIR={zephyr_sdk_path}",
        f"-DCONF_FILE={prj_conf_path}",
    ]

    try:
        subprocess.run(build_command, check=True)
        print("\n🏁 Build completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during build: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)
