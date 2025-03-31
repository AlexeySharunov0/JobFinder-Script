# Learning System

A powerful and interactive desktop application designed to streamline online learning using Python, PyQt6, and MySQL. This system allows students to enroll in courses, track progress, complete assignments, and export data, providing a seamless learning experience.

## Features
- **User Authentication:** Secure login and registration.
- **Course Management:** View and enroll in courses.
- **Schedule Tracking:** Access and manage student schedules.
- **Assignment Management:** Submit and track assignment progress.
- **Progress Tracking:** View course completion status and grades.
- **Data Export:** Export student progress to Excel.
- **Interactive UI:** Tkinter-based graphical interface for smooth navigation.

## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.10+ (Check version with `python --version`)
- MySQL Server (Check installation with `mysql --version`)
- Virtual Environment (Recommended for dependency isolation)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/learning-system.git
cd learning-system
```

### Step 2: Set Up a Virtual Environment
Create and activate a virtual environment to manage dependencies:
```bash
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

Verify that the virtual environment is active:
```bash
which python   # On macOS/Linux
where python   # On Windows
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⚠ **Potential Issues & Fixes:**
- If `spacy` fails to install, use:
  ```bash
  pip install --no-cache-dir spacy==3.7.5
  ```
- If `scikit-learn` or `scipy` throw compatibility errors:
  ```bash
  pip install --upgrade scikit-learn scipy
  ```
- If `PyQt6` installation fails:
  ```bash
  pip install PyQt6==6.8.1 --no-cache-dir
  ```

### Step 4: Configure the MySQL Database
1. **Start MySQL Server**
   - On Linux:
     ```bash
     sudo systemctl start mysql
     ```
   - On macOS (Homebrew):
     ```bash
     brew services start mysql
     ```
   - On Windows (Command Prompt as Administrator):
     ```bash
     net start MySQL80
     ```

2. **Create the Database**
   ```sql
   CREATE DATABASE OnlineLearningSystem;
   ```

3. **Update Database Credentials**
   Open `db/connection.py` and configure:
   ```python
   DATABASE_CONFIG = {
       'host': 'localhost',
       'user': 'your_username',
       'password': 'your_password',
       'database': 'OnlineLearningSystem'
   }
   ```

4. **Run Migrations (if needed)**
   If using schema migrations, run:
   ```bash
   python db/migrate.py
   ```

### Step 5: Run the Application
Ensure MySQL is running, then start the application:
```bash
python main.py
```

If execution fails due to missing permissions:
```bash
chmod +x main.py
./main.py   # On macOS/Linux
```

## Troubleshooting
### `ModuleNotFoundError`
If you encounter missing module errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### MySQL Connection Issues
- Verify credentials in `db/connection.py`.
- Ensure MySQL Server is running (`mysql -u your_username -p`).
- Check firewall and database permissions.

### UI Not Displaying Properly
- Ensure PyQt6 is correctly installed:
  ```bash
  pip install PyQt6==6.8.1
  ```
- If running on Wayland (Linux), switch to X11:
  ```bash
  export QT_QPA_PLATFORM=xcb
  ```

### `ImportError: DLL load failed` (Windows)
Ensure dependencies match your Python architecture (32-bit vs. 64-bit):
```bash
python -c "import platform; print(platform.architecture())"
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License

MIT License - see LICENSE file for details.

