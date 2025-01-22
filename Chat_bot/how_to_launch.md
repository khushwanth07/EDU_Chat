# How to Launch the Application

Follow these instructions to clone the repository, set up the project, and run the application.

---

## Steps to Launch

1. **Clone the Repository**
   - Clone the repository to your local machine using:
     ```bash
     git clone <repository-url>
     ```

2. **Install Requirements**
   - Navigate to the cloned repository and install the required libraries:
     ```bash
     pip install -r requirements.txt
     ```

3. **Open `launch.py`**
   - Open the `launch.py` file from the repository.

4. **Provide File Paths**
   - Update the `launch.py` file with the paths to the following files:
     - `docker.bat`: Path to the batch file for starting the PostgreSQL Docker container.
     - `initialize.py`: Path to the script for initializing the database(Till the folder containing that file).
     - `bot.py`: Path to the chatbot script(Till the folder containing that file).
     - `Index.html`: Path to the chatbot interface HTML file.

   - Example:
     ```python
     docker_bat_path = r"path\to\docker.bat"
     initialize_script_repo_path = r"path\to\Final"
     bot_script_repo_path = r"path\to\Final"
     html_file_path = r"path\to\Index.html"
     ```

5. **Run `launch.py`**
   - Execute the `launch.py` file to start the entire process:
     ```bash
     python launch.py
     ```

6. **Handle Errors**
   - If you encounter an error stating "No PDF table":
     - Stop the process and re-run the `launch.py` file.
   - If you encounter an error stating "File not found":
     - Check the file paths provided in `launch.py`.
     - Ensure the paths are correct and formatted as raw strings:
       ```python
       path = r"C:\Users\YourUser\path\to\file"
       ```

---

## Final Notes

- Ensure Docker is running before starting the application.
- Double-check all paths before running the `launch.py` script.
- If errors persist, review the logs for more detailed error messages and address them accordingly.

With these steps, your application should launch successfully.

