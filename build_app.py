import subprocess
import os
import sys
from dotenv import load_dotenv
import argparse

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="🛠 Run build FW script",
        usage="%(prog)s board_name"
    )

    parser.add_argument(
        "board_name", help="Zephyr board_name"
    )

    args = parser.parse_args(argv)

    return args

if __name__ == "__main__":

    args = parse_args(sys.argv[1:])

    load_dotenv()

    app_path = os.environ["APP_PATH"]
    board_root = os.environ["ZEPHYR_BOARD_ROOT"]
    prj_conf_path = os.path.join(app_path, "prj.conf")
    build_path = os.environ["BUILD_DIR"]
    board_name = args.board_name

    print("🛠 Running build FW...\n")

    build_command = [
        f"west",
        f"build",
        f"-b",
        f"{board_name}",
        f"{app_path}",
        f"--no-sysbuild",
        f"--build-dir",
        f"{build_path}",
        f"--pristine=auto",
        f"--",
        f"-DBOARD_ROOT={board_root}",
        f"-DZEPHYR_TOOLCHAIN_VARIANT=zephyr",
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
