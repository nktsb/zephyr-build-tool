import argparse
import subprocess
import os
import re
import sys
import venv
import shutil
import json

PYTHON = "python" if sys.platform == "win32" else "python3"
RUN_ENV_SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

def check_tool(tool_name, install_instruction):
    if shutil.which(tool_name):
        return True
    else:
        print(f"❌ {tool_name} is not installed. Install it using:\n> {install_instruction}")
        return False

def check_system_dependencies():

    dependencies = []

    if sys.platform == "linux":
        dependencies = [
            ("git", "sudo apt install git"),
            ("cmake", "sudo apt install cmake"),
            ("ninja", "sudo apt install ninja-build"),
            ("ccache", "sudo apt install ccache"),
            ("dtc", "sudo apt install device-tree-compiler"),
            ("wget", "sudo apt install wget"),
        ]
    elif sys.platform == "darwin":  # macOS
        dependencies = [
            ("git", "brew install git"),
            ("cmake", "brew install cmake"),
            ("ninja", "brew install ninja"),
            ("ccache", "brew install ccache"),
            ("dtc", "brew install dtc"),
            ("wget", "brew install wget"),
        ]
    elif sys.platform == "win32":
        dependencies = [
            ("git", "winget install Git.Git"),
            ("python", "winget install python"),
            ("cmake", "winget install Kitware.CMake"),
            ("ninja", "winget install Ninja-build.Ninja"),
            ("dtc", "winget install oss-winget.dtc"),
            ("wget", "winget install wget"),
            ("7z", "winget install 7zip.7zip"),
        ]

    all_installed = True
    for tool, instruction in dependencies:
        if not check_tool(tool, instruction):
            all_installed = False

    if not all_installed:
        sys.exit(1)

    print("✅ System dependencies check")

def run_command_in_venv(venv_path, 
                        command, 
                        zephyr_env=None, 
                        env=os.environ.copy(),
                        return_out=False):

    if sys.platform == "win32":
        venv_activate_path = os.path.join(venv_path, "Scripts", "activate.bat")
        if (zephyr_env != None):
            zephyr_activate_path = os.path.join(zephyr_env, "zephyr", "zephyr-env.cmd")
            activate_command = f"{venv_activate_path} && {zephyr_activate_path}"
        else:
            activate_command = f"{venv_activate_path}"

        command_str = f"cmd /c \"{activate_command} && {command}\""

    else:
        venv_activate_path = os.path.join(venv_path, "bin", "activate")
        if (zephyr_env != None):
            zephyr_activate_path = os.path.join(zephyr_env, "zephyr", "zephyr-env.sh")
            activate_command = f"source {venv_activate_path} && source {zephyr_activate_path}"
        else:
            activate_command = f"source {venv_activate_path}"

        command_str = f"bash -c '{activate_command} && {command}'"

    try:

        kwargs = {}
        if return_out:
            kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        result = subprocess.run(command_str, shell=True, check=True, env=env, **kwargs)

        if return_out:
            return result.stdout, result.stderr
        else:
            return True, None

    except subprocess.CalledProcessError as e:
        return None, e


def run_script_in_venv(venv_path, 
                       zephyr_env_path, 
                       script_path, 
                       script_args=None, 
                       env=os.environ.copy()):

    if script_args is None:
        script_args = []

    command_list = [PYTHON, script_path] + script_args
    command = " ".join(command_list)
    res, err = run_command_in_venv(venv_path, command, zephyr_env_path, env)
    if err:
        print("❌ Failed run script in venv")
        sys.exit(1)


def ensure_venv(venv_path, extra_requirements_list=None):
    if not os.path.exists(venv_path):
        print(f"📦 Initializing Python virtual environment {venv_path}...\n")
        venv.create(venv_path, with_pip=True)

        requirements_path = os.path.join(RUN_ENV_SCRIPT_PATH, "requirements.txt")

        command = f"pip install -r {requirements_path}"

        if extra_requirements_list:
            for req in extra_requirements_list:
                command += f" -r {os.path.expanduser(req)}"

        res, err = run_command_in_venv(venv_path, command)
    
        if err:
            shutil.rmtree(venv_path)
            print("❌ Python .venv setup failed\n")
            sys.exit(1)

        print(f"🏁 Python virtual environment installed\n")

    else:
        print(f"✅ Python virtual envirornment check")


def ensure_dotenv(company_name,
                  project_name, 
                  dotenv_path,
                  venv_path,
                  zephyr_env_path,
                  app_path,
                  zephyr_boards_path,
                  build_path,
        ):

    abs_zephyr_boards = os.path.abspath(zephyr_boards_path)
    abs_app_path = os.path.abspath(app_path)
    abs_venv_path = os.path.abspath(venv_path)
    abs_zephyr_env_path = os.path.abspath(zephyr_env_path)
    abs_build_path = os.path.abspath(build_path)

    if os.path.exists(dotenv_path):
        print(f"✅ .env file check")
        return

    print("📦 Initalizing .env\n")

    env_vars = {
        "COMPANY_NAME": company_name,
        "PROJECT_NAME": project_name,
        "ZEPHYR_BOARD_ROOT": abs_zephyr_boards,
        "PYTHON_VENV": abs_venv_path,
        "ZEPHYR_ENV": abs_zephyr_env_path,
        "APP_PATH": abs_app_path,
        "ZEPHYR_TOOLCHAIN_VARIANT": "zephyr",
        "BUILD_DIR": abs_build_path
    }

    with open(dotenv_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    print(f"📝 Created .env with default values:")
    for k, v in env_vars.items():
        print(f"\t{k}={v}")
    print(f"🏁 Initialized .env\n")


def ensure_zephyr_env(venv_path,
                      zephyr_env_path,
                      manifest_url,
                      manifest_version,
                      manifest_path=None):

    if not os.path.exists(zephyr_env_path):
        print("📦 Initializing Zephyr virtual environment...\n")

        env = os.environ.copy()
        env.pop("ZEPHYR_BASE", None)

        if manifest_path:
            manifest_arg = f"--mf {manifest_path}"
        else:
            manifest_arg = f"-m {manifest_url} --mr {manifest_version}"

        res, err = run_command_in_venv(venv_path, f"mkdir {zephyr_env_path} && "
                f"cd {zephyr_env_path} && "
                f"west init {manifest_arg} "
                f"&& west update", env=env)
        
        if err:
            shutil.rmtree(zephyr_env_path)
            print("❌ Zephyr environment setup failed\n")
            sys.exit(1)

        print("🏁 Zephyr & nRF-SDK installed!\n")
    else:
        print(f"✅ Zephyr virtual envirornment check")

def check_zephyr_sdk(venv_path, 
                     zephyr_env_path):

    res, err = run_command_in_venv(venv_path, f"west sdk list",
        zephyr_env_path, return_out=True)

    if err:
        return False

    lines = res.splitlines()
    in_installed_section = False

    sdk_path = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("path:"):
            sdk_path = line.split("path:")[1].strip()
            continue
        if stripped == "installed-toolchains:":
            in_installed_section = True
            continue
        if in_installed_section:
            if "arm-zephyr-eabi" in stripped:
                return sdk_path
        if stripped == "available-toolchains:":
            in_installed_section = False
            continue

    return None

def ensure_toolchain(venv_path, 
                     zephyr_env_path,
                     sdk_version):

    sdk_path = check_zephyr_sdk(venv_path, zephyr_env_path)

    if sdk_path:
        print(f"✅ Toolchain check: {sdk_path}")
        return

    print("📦 Initializing toolchain...\n")

    res, err = run_command_in_venv(venv_path, f"west sdk install " +
            f"--toolchains arm-zephyr-eabi --no-hosttools --version {sdk_version}", 
            zephyr_env_path)

    if err:
        print("❌ Toolchain setup failed\n")
        sys.exit(1)

    print("🏁 Toolchain installed\n")


def show_banner():
    banner_path = os.path.join(RUN_ENV_SCRIPT_PATH, "banner.py")
    run_script_in_venv(venv_path, None, banner_path)

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Run script inside prepared environment",
        usage="%(prog)s --env [all venv-dotenv] --set settings.json --run script.py -- [script args ...]"
    )

    parser.add_argument(
        "--env",
        nargs="+",
        choices=["venv-dotenv", "all", "dotenv-only"],
        help="Environment setup components"
    )

    parser.add_argument(
        "--set", dest="settings_json", required=True,
        help="JSON file with project settings"
    )

    parser.add_argument(
        "--req", dest="extra_requirements", required=False, nargs="+",
        help="One or more extra requirements.txt files"
    )

    parser.add_argument(
        "--run", dest="script_to_run", required=False,
        help="Script to run"
    )

    parser.add_argument(
        "script_args", nargs=argparse.REMAINDER,
        help="Arguments to pass to the script (only used if --run is specified)"
    )

    args = parser.parse_args(argv)

    env = set(args.env or [])

    if len(env) > 1:
        print("❌ Only one env mode can be selected: all | venv-dotenv | dotenv-only")
        sys.exit(1)

    args.all = "all" in env
    args.venv_dotenv = "venv-dotenv" in env
    args.dotenv_only = "dotenv-only" in env

    if '--' in args.script_args:
        args.script_args.remove('--')

    return args

def load_settings(settings_path):
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        return settings
    except FileNotFoundError:
        print(f"❌ JSON File not found: {settings_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        sys.exit(1)

if __name__ == "__main__":

    args = parse_args(sys.argv[1:])

    settings_json = load_settings(args.settings_json)

    dotenv_path = ".env"

    company_name = settings_json["company_name"]
    project_name = settings_json["project_name"]
    
    app_path = os.path.expanduser(settings_json["app_path"])

    venv_path = os.path.expanduser(settings_json["venv_path"])
    zephyr_env_path = os.path.expanduser(settings_json["zephyr_env_path"])

    extra_requirements_list = args.extra_requirements
    zephyr_boards_path = os.path.expanduser(settings_json["zephyr_boards_path"])

    manifest_path = settings_json.get("manifest_path") or None
    if manifest_path:
        manifest_path = os.path.expanduser(manifest_path)

    build_path = os.path.expanduser(settings_json["build_path"])

    zephyr_sdk_verison = settings_json["zephyr_sdk_version"]
    manifest_version = settings_json.get("manifest_version") or None
    manifest_url = settings_json.get("manifest_url") or None

    ## STEP 1: create/check .env
    ensure_dotenv(company_name,
                  project_name, 
                  dotenv_path,
                  venv_path,
                  zephyr_env_path,
                  app_path,
                  zephyr_boards_path,
                  build_path)

    # STEP 2: create/check .venv
    if args.all or args.venv_dotenv:
        ensure_venv(venv_path, extra_requirements_list)

    ## STEP 4: check dependencies
    if args.all:
        check_system_dependencies()

    ## STEP 3: create/check .zephyr_env
    if args.all:
        ensure_zephyr_env(venv_path,
                          zephyr_env_path,
                          manifest_url,
                          manifest_version,
                          manifest_path)
    else:
        zephyr_env_path = None

    ## STEP 4: create/check toolchain
    if args.all:
        ensure_toolchain(venv_path, 
                         zephyr_env_path,
                         zephyr_sdk_verison)

    show_banner()

    if not args.script_to_run:
        print("🗿 No script to run (.py file not found in arguments)\n")
        exit()

    run_script_in_venv(venv_path, zephyr_env_path, args.script_to_run, args.script_args)