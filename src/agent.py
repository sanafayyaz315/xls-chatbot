import re
import json
import os
import inspect
import asyncio
from dotenv import load_dotenv
from llm import LLM
from tool_registry import TOOLS
from config import SYSTEM_PROMPT_TEMPLATE_EXCEL, MAX_ITERATIONS, STOP_WORDS
from utils import load_file

class Agent():
    def __init__(self,
                 llm,
                 system_prompt,                
                 stop_words,
                 known_actions,
                 data=None,
                 max_iterations=10,
                 
                 ):
        self.llm = llm
        self.system_prompt = system_prompt
        self.data = data
        self.stop_words = stop_words
        self.known_actions = known_actions
        self.max_iterations = max_iterations
        self.messages = []
        self.messages.append({"role": "system", "content": self.system_prompt})

    async def generate(self, prompt):
        stop = False
        response = ""
        stop_word_ind = None

        for chunk in self.llm.stream(prompt):
            response += chunk
            yield chunk

            for word in self.stop_words:
                if word in response[-20:]: # check for stop words in the last 20 characters (not words or subwords, characters). Doing this because PAUSE is represented as two tokwns [PA, USE] so cannot do token by token compaison with stop words. Instead checking if stop words exist in the last 20 characters of the response or not.
                    stop_word_ind = response[-20:].find(word) # index of the first character of stop word
                    stop = True
                    # response = response[:stop_word_ind + len(word)]
                    break
            if stop:
                break

        print(f"\nstop word found at {stop_word_ind}")
    
    def parse_action(self, response):
        pattern = r'```json\s*(\{.*?\})\s*```'         # Match ```json { ... } ```
        match = re.search(pattern, response, re.DOTALL)
        if not match:
            raise ValueError("No valid JSON block found after 'Action:'")
        json_str = match.group(1)

        try:
            data = json.loads(json_str)
            if "action" not in data or "action_input" not in data:
                raise ValueError("Missing'action' or 'action_input' fields. Produce Action in correct format.")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parsing error: {e}")

        action = data["action"]
        action_input = data["action_input"]

        return action, action_input
        
    def execute_tool(self, action, action_input):

        func = TOOLS[action]
        if action == "execute_pandas":
            observation = func(action_input=action_input, df=self.data)
            return observation
        if action == "get_schema":
            observation = func(df=self.data)
            return observation

        observation = func(action_input)
        return observation
    
    async def run(self, message):
        
        next_prompt = message

        for _ in range(self.max_iterations):
            self.messages.append({"role": "user", "content": next_prompt})
            # collect streaming reponse from the llm
            response = ""
            async for chunk in self.generate( self.messages):
                yield ("response", chunk)
                response += chunk  
            # append response to messages
            self.messages.append({"role": "assistant", "content": response})

            # parse response
            if "Action" in response:
                try: # try-except to check if Action block is correctly generated and is parseable
                    action, action_input = self.parse_action(response)
                except Exception as e:
                    observation = (
                        "Error: Failed to parse action from response.\n"
                        "Carefully review the `Thought`, `Action`, `Action Input` format.\n" 
                        f"Details: {str(e)}"
                    )
                    next_prompt = f"{observation}\n"
                    yield ("observation", next_prompt)
                    continue

                # check whether action is valid or not
                if action not in self.known_actions:
                    observation = f"Action '{action}' not available in the set of tools."
                else:
                    try:
                        observation = self.execute_tool(action, action_input)
                    except Exception as e:
                        observation = f"Error: Failed to execute tool: `{action}`. Details: {str(e)}"
                next_prompt = f"\nObservation: {observation}\n"
                yield ("observation", next_prompt)

            elif "Final Answer:" in response:
                break # Exit loop if final answer is provided

            else:
                observation = "Missing `Action` or `Final Answer` in response."

        return
    
if __name__ == "__main__":
    
    from utils import load_file, preprocess_data
    from tool_registry import TOOLS
    from config import SYSTEM_PROMPT_TEMPLATE_EXCEL, MAX_ITERATIONS, STOP_WORDS
    from config import (
        API_KEY,
        MODEL
        )
    
    stop_words = STOP_WORDS
    load_dotenv()
    max_iterations = MAX_ITERATIONS
    
    llm = LLM(api_key=API_KEY, model=MODEL)
    system_prompt = SYSTEM_PROMPT_TEMPLATE_EXCEL
    prompt = system_prompt.format(file_intent="")

    df = load_file("data/customer_sales.csv")
    df = preprocess_data(df)

    agent = Agent(llm,
                 system_prompt,  
                 data=df,              
                 stop_words=stop_words,
                 known_actions=TOOLS,
                 max_iterations=10)
    
    async def main(agent, message):        
        response = ""
        async for kind, chunk in agent.run(message):
            if kind == "response":
                response += chunk
                print(chunk, end="", flush=True)
            elif kind == "observation":
                print("\n", chunk, flush=True)

        print("\n----------------------FINAL RESPONSE-----:")
        print(response[response.find("Final Answer"):])

    message = "What is the total amount spent by Jennifer Miller?"
    message = "What products have Jennifer Miller and Jennifer Adams bought?"
    message = "WHich customer has spent the most? and what is their spending amount?"
    message = "Which product was sold the most times and what is the total revenue for that product?"

    asyncio.run(main(agent, message))

        
        