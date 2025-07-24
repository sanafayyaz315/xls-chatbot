from dotenv import load_dotenv, find_dotenv
import os
import sys
sys.path.append(os.path.abspath("../src"))
load_dotenv(find_dotenv(), override=True)


API_KEY = os.environ.get("API_KEY")
MODEL = os.environ.get("MODEL")

CHAINLIT_DB_NAME = os.environ.get("CHAINLIT_DB_NAME")
CHAINLIT_DB_USER = os.environ.get("CHAINLIT_DB_USER")
CHAINLIT_DB_PASSWORD = os.environ.get("CHAINLIT_DB_PASSWORD")
CHAINLIT_DB_HOST = os.environ.get("CHAINLIT_DB_HOST")
CHAINLIT_DB_PORT = os.environ.get("CHAINLIT_DB_PORT")

MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS"))

with open("../templates/excel_pandas.txt", "r") as f:
    SYSTEM_PROMPT_TEMPLATE_EXCEL = f.read()

STOP_WORDS = ("PAUSE",)
if __name__ == "__main__":
    print(SYSTEM_PROMPT_TEMPLATE_EXCEL)

