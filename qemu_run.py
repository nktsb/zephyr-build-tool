import os
from dotenv import load_dotenv
import subprocess
import time
import signal
import sys

def run_west_qemu_with_signal_and_check(timeout=60):
    load_dotenv()
    west_build_command = [
        "west",
        "build",
        "--build-dir",
        os.environ.get("BUILD_DIR", "build"),
        "-t",
        "run",
    ]

    proc = subprocess.Popen(west_build_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    test_success = False

    start_time = time.time()

    try:
        for line in proc.stdout:
            print(line, end='')

            if "PROJECT EXECUTION SUCCESSFUL" in line:
                test_success = True
                break
            elif "PROJECT EXECUTION FAILED" in line:
                break

            if time.time() - start_time > timeout:
                print("\n⏰ Timeout reached, stopping QEMU...")
                break

        time.sleep(2)
        proc.send_signal(signal.SIGINT)
        proc.wait(timeout=5)

    except subprocess.TimeoutExpired:
        print("QEMU did not stop in time, killing...")
        proc.kill()
    except Exception as e:
        print(f"Unexpected error: {e}")
        proc.kill()
    finally:
        proc.stdout.close()

    if test_success:
        print("\n✅ Tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed or no success message found.")
        sys.exit(1)

if __name__ == "__main__":
    run_west_qemu_with_signal_and_check()
