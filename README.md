# 🛠 Zephyr Build Tool

Zephyr Build Tool is a set of Python scripts designed to automate the setup of development environments for Zephyr RTOS projects. It streamlines the configuration process by managing:

- Setting up a Python virtual environment with environment variables
- Creating .env
- Cloning Zephyr RTOS sources
- Installing and configuring the Zephyr SDK and toolchains
- Running custom scripts inside the prepared environment
- Building zephyr RTOS projects
- Installing extra requirements in venv for your scripts

## 📦 Features

- Easy Zephyr RTOS setup
- Configurable via a single JSON file
- Modular environment setup: python venv, .env, zephyr environment, zephyr toolchain
- Script runner with full argument forwarding

## 🚀 Quick Start

### 1. Install system dependencies

- git
- python3
- cmake
- ninja
- ccache (for Linux & Macos)
- dtc
- wget
- 7zip (for Windows)

### Linux:
```console
sudo apt install --no-install-recommends git cmake ninja-build ccache device-tree-compiler wget
```

### MacOS:
```console
brew install python3 cmake ninja ccache dtc wget
```

### Windows:
```console
winget install Git.Git python Kitware.CMake Ninja-build.Ninja oss-winget.dtc wget 7zip.7zip
```

### 2. ⚙️ Creating settings file

Prepare a settings.json file like:

```json
{
	"company_name": "ypur-company",
	"project_name": "your-project",
	"app_path": "app",

	"venv_path": ".venv",
	"manifest_url": "https://github.com/nrfconnect/sdk-nrf",
	"manifest_version": "v2.9.1",
	"zephyr_env_path": ".zephyr_env",
	"zephyr_sdk_version": "0.16.8",
	"zephyr_boards_path": "app",

	"build_path": "build"
}
```

* You can use `"manifest_path"` with path to local `west.yml` file instead of
`"manifest_url"` and `"manifest_version"`.
* Note: It works only with 4.2.0+ Zephyr versions *

* extra_requirements_path: Allows you to install additional Python modules into your virtual environment.


### 3. 🏗 Run the environment setup and build firmware script

```console
python run_env.py --env all --set settings.json --run build_app.py -- board_name
```

Sample output:
```console
✅ Python virtual envirornment check
✅ .env file check
✅ System dependencies check
✅ Zephyr virtual envirornment check
✅ Toolchain check: /Users/nktsb/zephyr-sdk-0.16.8
                                                                         
 _   _  ___  _   _ _ __       ___ ___  _ __ ___  _ __   __ _ _ __  _   _ 
| | | |/ _ \| | | | '__|____ / __/ _ \| '_ ` _ \| '_ \ / _` | '_ \| | | |
| |_| | (_) | |_| | | |_____| (_| (_) | | | | | | |_) | (_| | | | | |_| |
 \__, |\___/ \__,_|_|        \___\___/|_| |_| |_| .__/ \__,_|_| |_|\__, |
 |___/                                          |_|                |___/ 

🛠 Running build FW...
```

Arguments:

* --env : Select environment components to prepare (dall, venv-dotenv, dotenv-only)
* --set : Path to the JSON settings file
* --run : Script to run inside the prepared environment
* -- : Separator for script arguments

### 4. Run your custom script

```console
python run_env.py --env venv-dotenv --set settings.json --run your_script.py -- [your_script args]
```

## ⚙️ Repository Structure

* run_env.py – Main environment setup and runner script
* build_app.py – Zephyr RTOS based project builder
* clean_app.py – Clean project build output
* requirements.txt – Python main dependencies
* banner.py – Banner printer

## 🤝 Contributing

Feel free to open issues or pull requests with ideas, improvements, or fixes.

## 📄 License

Licensed under the MIT License.