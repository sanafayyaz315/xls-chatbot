# Chat with Excel Agent

A lightweight Python-based agent that lets you **converse with your Excel or CSV files** using natural language. Built without any abstraction-heavy frameworks like LangChain — this is **pure Python logic** with a clean conversational interface via [Chainlit](https://www.chainlit.io/).

## Features

- Upload `.csv` or `.xlsx` files through a user-friendly UI
- Ask questions about your data in natural language
- Converts questions to `pandas` code on the fly
- Dynamically executes the code and returns the result
- Handles errors gracefully (e.g., missing columns, syntax issues)
- No external agent frameworks – minimal, fast, transparent

## 🛠️ Tech Stack

| Component      | Description                        |
|----------------|------------------------------------|
| **Python**     | Core backend logic                 |
| **Pandas**     | Data manipulation and querying     |
| **Chainlit**   | Conversational UI (frontend + server)

## Installation

1. Clone the repo and set up a virtual environment:

```bash
git clone https://github.com/sanafayyaz315/xls-chatbot.git

cd xls-chatbot

pip install -r requirements.txt
```

2. Create a .env file in the root directory with the following content:

```bash
# OpenAI model config
MODEL="gpt-3.5-turbo"
API_KEY="your-openai-api-key"

# Chainlit database (optional, if you're using persistent sessions)
CHAINLIT_DB_NAME="chainlit"
CHAINLIT_DB_USER="chainlit"
CHAINLIT_DB_HOST="localhost"
CHAINLIT_DB_PORT="25434"
CHAINLIT_DB_PASSWORD="password"
CHAINLIT_AUTH_SECRET="your-auth-secret"

# Misc
TEMPLATE_DIR=../templates
MAX_ITERATIONS="10"
```

3. Setup Chainlit Database

```
cd database
docker compose up -d
```

4. Create schema for the chainlit database using this script [script](/database/scripts/chainlit_schema.sql).
## Usage
Run the app
```
cd src
chainlit run main.py
```
This will start the app at http://localhost:8000/

Apload a csv/excel file (one file per thread for now) and chat with it. 

## Data
A script to create dummy sales data can be found in the [data.py](src/data.py) file.

### Author
Built with ❤️ Sana Fayyaz

[![Watch Demo](docs/sample.gif)](docs/sample.mp4)