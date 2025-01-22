import os
import subprocess
import time
import webbrowser
import signal
import sys

# Global variable for the chatbot process
chatbot_process = None

# Check if Docker is running
def is_docker_running():
    try:
        subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        print("Docker is not installed or not in PATH.")
    except subprocess.CalledProcessError:
        print("Docker is installed but not running.")
    return False

# Check if the Docker container exists and start it
def start_docker_container():
    container_name = "alina"  # Update with your container name
    docker_bat_path = "path to docker batch file "  # Update this path

    print("Checking if the Docker container exists...")
    try:
        if not is_docker_running():
            raise Exception("Docker is not running. Please start Docker Desktop and try again.")

        # Check if the container exists
        existing_container = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()

        if existing_container:
            print(f"Container '{container_name}' already exists.")
            # Check if the container is running
            running_container = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ).stdout.strip()

            if running_container:
                print(f"Container '{container_name}' is already running.")
            else:
                print(f"Starting the stopped container '{container_name}'...")
                subprocess.run(["docker", "start", container_name], check=True)
                print("Container started.")
        else:
            print(f"Container '{container_name}' does not exist. Creating it...")
            subprocess.run(["start", "/B", docker_bat_path], shell=True)
            time.sleep(10)  # Wait for the container to be ready
            print("Container created and started.")
    except Exception as e:
        print(f"Error managing Docker container: {e}")
        exit(1)

# Run the database initialization script
def initialize_database():
    database_init_folder = "path to initialize.py directory"  # Update this path
    init_script = "initialize.py"

    print("Initializing the database...")
    try:
        os.chdir(database_init_folder)
        subprocess.run(["python", init_script], check=True)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        exit(1)

# Launch the chatbot
def launch_chatbot():
    global chatbot_process
    chatbot_folder = (r"path to bot.py directory")  # Update this path
    chatbot_script = "bot.py"

    print("Launching chatbot...")
    try:
        os.chdir(chatbot_folder)
        chatbot_process = subprocess.Popen(["python", chatbot_script])
        print("Chatbot launched successfully.")
        time.sleep(5)
    except Exception as e:
        print(f"Error launching chatbot: {e}")
        exit(1)

# Open the chatbot interface in the browser
def open_browser():
    html_file_path = (r"path to Index.html file")  # Update this path
    print("Opening the chatbot interface in the browser...")
    try:
        full_path = os.path.abspath(html_file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Cannot find HTML file at {full_path}")

        webbrowser.open_new(f"file://{full_path}")
        print("Browser opened successfully.")
    except Exception as e:
        print(f"Error opening browser: {e}")

# Exit the chatbot process
def stop_chatbot():
    global chatbot_process
    if chatbot_process:
        print("Stopping the chatbot...")
        chatbot_process.terminate()
        chatbot_process.wait()
        print("Chatbot stopped.")

# Graceful exit on script termination
def signal_handler(sig, frame):
    print("\nExiting...")
    stop_chatbot()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signal

    print("Launching the entire workflow...")
    start_docker_container()
    initialize_database()
    launch_chatbot()
    open_browser()

    print("Workflow completed! Press Ctrl+C to exit.")
    try:
        while True:  # Keep the script running until terminated
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)
