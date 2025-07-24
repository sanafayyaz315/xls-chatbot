import chainlit as cl
import chainlit.data as cl_data
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
import asyncio
import shutil
from agent import Agent
from llm import LLM
from tool_registry import TOOLS
from config import SYSTEM_PROMPT_TEMPLATE_EXCEL, MAX_ITERATIONS, STOP_WORDS
from config import (
        API_KEY,
        MODEL
        )

from config import (
    CHAINLIT_DB_NAME,
    CHAINLIT_DB_USER,
    CHAINLIT_DB_PASSWORD,
    CHAINLIT_DB_HOST,
    CHAINLIT_DB_PORT,
)

conn_info = f"postgresql+asyncpg://{CHAINLIT_DB_USER}:{CHAINLIT_DB_PASSWORD}@{CHAINLIT_DB_HOST}:{CHAINLIT_DB_PORT}/{CHAINLIT_DB_NAME}"
storage_client = None

llm = LLM(api_key=API_KEY, model=MODEL)

import chainlit as cl
import pandas as pd
import os

UPLOAD_DIR = "../uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@cl.data_layer
def get_data_layer():
    return SQLAlchemyDataLayer(
        conninfo=conn_info, 
        storage_provider=storage_client
    )

# to maintain session state
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("llm", llm)
    system_prompt = SYSTEM_PROMPT_TEMPLATE_EXCEL.format(file_intent="")
    cl.user_session.set("system_prompt", system_prompt)
    cl.user_session.set("known_actions", TOOLS)

    files = None

    # Ask the user to upload a file
    while files is None:
        files = await cl.AskFileMessage(
            content="📄 Please upload an Excel or CSV file to begin!",
            accept=[".xlsx", ".xls", ".csv"]
        ).send()

    for file in files:
        # Move the file from temp location to permanent location
        new_path = os.path.join(UPLOAD_DIR, file.name)
        shutil.copy(file.path, new_path)

        # Read the file into pandas
        if file.name.endswith(".csv"):
            df = pd.read_csv(new_path)
        else:
            df = pd.read_excel(new_path)

        # Save df in user session
        cl.user_session.set("df", df)

        await cl.Message(
            content=f"✅ `{file.name}` uploaded successfully! Rows: {df.shape[0]}, Columns: {df.shape[1]}"
        ).send()

@cl.on_message
async def on_message(message: cl.Message):

    try:
        print(message)

        df = cl.user_session.get("df")
        if df is None:
            await cl.Message(content="⚠️ Please upload a file first before asking questions.").send()
            return
        
        llm = cl.user_session.get("llm")
        system_prompt = cl.user_session.get("system_prompt")
        known_actions = cl.user_session.get("known_actions")

        agent = Agent(llm,
                 system_prompt,  
                 data=df,              
                 stop_words=STOP_WORDS,
                 known_actions=TOOLS,
                 max_iterations=MAX_ITERATIONS)
        
        response = ""
        stop_step_stream = False

        # Create a step for streaming intermediate steps
        async with cl.Step(name="Intermediate Steps") as step:
            async for kind, chunk in agent.run(message.content,):
                if kind == "response":
                    response += chunk
                    if not stop_step_stream:
                        if "Final Answer:" not in response[-20:]:
                            await step.stream_token(chunk)
                        else:
                            stop_step_stream = True
                      # stream LLM's thought process
                elif kind == "observation":
                    # Print to terminal and stream to step as a new token line
                    print("\nObservation:", chunk, flush=True)
                    await step.stream_token(f"\n\nObservation:\n{chunk}\n")

        # Extract the final answer
        idx = response.find("Final Answer:")
        if idx != -1:
            final_answer = response[idx:].strip()
        else:
            final_answer = "FE error: Unable to find final answer in response."

        # Send the final answer as a separate message
        await cl.Message(content=final_answer).send()

    except Exception as e:
        await cl.Message(content=f"Error: {str(e)}").send()

@cl.on_chat_end
def end():
    pass

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)
# CMD > chainlit run main.py --host 0.0.0.0 --port 8000 -h