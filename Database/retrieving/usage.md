# Usage Manual for `example.py`

## Prerequisites
Before running the `example.py` script, ensure you have Docker (Desktop) installed and properly set up on your machine.

## Running the File in Docker

1. **Navigate to the Docker Setup Directory**:
    Open your terminal and navigate to the `docker_setup` directory where the Docker configuration files are located.

    ```sh
    cd /Database/docker_setup
    ```

2. **Start the Docker Container**:
    Run the `start_docker.bat` script to start the Docker container with the PostgreSQL database.

    ```sh
    start_docker.bat
    ```

    on Windows or on Unix 

    ```sh
    start_docker
    ```


## Running `example.py`

1. **Navigate to the `Database/retrieving` Directory**:
    Open your terminal and navigate to the `Database/retrieving` directory where the `example.py` script is located.

    ```sh
    cd /Database/retrieving
    ```

2. **Run the `example.py` Script**:
    Execute the `example.py` script to initialize the database and find the closest questions to a given question.

    ```sh
    python example.py
    ```

3. **Output**:
    The script will print the closest questions and their answers to the given question.

    ```plaintext
    Closest questions to 'How much is the tuition fees?':
    Question: [Question Text] with answer: [Answer Text]
    ...
    ```