import subprocess
import os
import sys
from dotenv import load_dotenv
import argparse

def get_cached_board(build_path):
    cmake_cache_path = os.path.join(build_path, "CMakeCache.txt")
    
    if not os.path.exists(cmake_cache_path):
        return None

    try:
        with open(cmake_cache_path, 'r') as f:
            for line in f:
                if line.startswith('BOARD:STRING='):
                    return line.split('=', 1)[1].strip()

                elif 'BOARD=' in line and not line.startswith('#'):
                    parts = line.split('BOARD=')
                    if len(parts) > 1:
                        return parts[1].split()[0].strip()

    except Exception as e:
        print(f"❗️ Warning: Could not read CMakeCache.txt: {e}")
    
    return None

def ninja_build_is_valid(build_path):
    build_ninja_path = os.path.join(build_path,"build.ninja")
    if os.path.exists(build_ninja_path) and \
            get_cached_board(build_path) == board_name:
            return True
    return False

def run_ninja_build(app_path, build_path):
    ninja_build_command = [
        f"ninja",
        f"-C",
        f"{build_path}"
    ]
    try:
        print("🥷 Running Ninja build...\n")
        subprocess.run(ninja_build_command, env=os.environ.copy(), check=True)
        print("\n🏁 Build completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❗️ Ninja build failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)

def run_west_build(app_path, build_path, board_root, board_name, prj_conf_name, 
                   overlay_files=None, use_sysbuild=False, extra_defines=None):

    if use_sysbuild == True:
        sysbuild_cmd = "--sysbuild"
    else:
        sysbuild_cmd = "--no-sysbuild"

    west_build_command = [
        f"west",
        f"build",
        f"-b",
        f"{board_name}",
        f"{app_path}",
        f"{sysbuild_cmd}",
        f"--build-dir",
        f"{build_path}",
        f"--pristine=auto",
        f"--",
        f"-DBOARD_ROOT={board_root}",
        f"-DZEPHYR_TOOLCHAIN_VARIANT=zephyr",
        f"-DCONF_FILE={prj_conf_name}",
    ]

    if overlay_files:
        overlay_str = ";".join(overlay_files)
        west_build_command.append(f"-DDTC_OVERLAY_FILE={overlay_str}")

    if extra_defines:
        for define in extra_defines:
            if '=' in define:
                west_build_command.append(f"-D{define}")
            else:
                print(f"⚠️ Invalid define format: '{define}' (expected KEY=VALUE)")

    command_str = " ".join(west_build_command)

    print(f"\n🚀 west command:\n{command_str}\n")

    try:
        print("🌅 Running West build...\n")
        subprocess.run(west_build_command, env=os.environ.copy(), check=True)
        print("\n🏁 Build completed successfully.\n")
    except subprocess.CalledProcessError as e:
        print(f"\n❗️ West build failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)

    sys.exit(0)

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="🛠 Run build FW script",
        usage="%(prog)s board_name"
    )

    parser.add_argument(
        "--board_name", help="Zephyr board_name"
    )

    parser.add_argument(
        "--prj_conf", nargs="*", help="One or more Zephyr .conf files"
    )

    parser.add_argument(
        "--overlay", nargs='*', default=[], help="One or more .overlay files"
    )

    parser.add_argument(
        "--sysbuild", action='store_true', help="Use --sysbuild (default is --no-sysbuild)"
    )

    parser.add_argument(
        "--defines", nargs='*', default=[], help="Additional CMake defines in KEY=VALUE format"
    )

    args = parser.parse_args(argv)

    return args

if __name__ == "__main__":

    args = parse_args(sys.argv[1:])

    load_dotenv()

    app_path = os.environ["APP_PATH"]
    board_root = os.environ["ZEPHYR_BOARD_ROOT"]

    if args.prj_conf:
        prj_conf_name = ";".join(args.prj_conf)
    else:
        prj_conf_name = "prj.conf"

    overlay_files = args.overlay
    build_path = os.environ["BUILD_DIR"]
    board_name = args.board_name
    use_sysbuild = args.sysbuild
    extra_defines = args.defines

    print("🛠 Running build FW...\n")

    if ninja_build_is_valid(build_path):
        run_ninja_build(app_path, build_path)
    else:
        run_west_build(app_path, build_path, board_root, board_name, prj_conf_name, 
                       overlay_files, use_sysbuild, extra_defines)

