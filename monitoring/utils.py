from pathlib import Path

from dotenv import load_dotenv

def load_environment():
    script_folder = Path(__file__).resolve().parent
    root_folder = script_folder.parent
    root_env_path = root_folder / ".env"
    load_dotenv(dotenv_path=root_env_path)