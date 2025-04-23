import os
import sys
import time
import json
import openai
import re

from utils.llm import chat_llm, prepend_history, rules
from levels.utils import convert_to_prompt

def broadcast_protocol(structured=True):
    prompt = "Here is the broadcast protocol:\n"
    prompt += "In a cooperative multi-agent game, after each agent selects its action, it broadcasts a message to all other agents including its intention for next steps. Other agents use received messages to update their decisions for the next step. In this sense, agents have better cooperation towards the goal of the game.\n"
    if structured:
        prompt += "1. The broadcast message should be structured in the following format:\n"
        prompt += "((id)task, ingredient, location) or None\n"
        prompt += "id: the index of the current task shown in the 'current dishes' of the game state (start from 0).\n"
        prompt += "task: the name of the task, i.e. The name of your current targeted dish.\n"
        prompt += "ingredient: the name of the ingredient (of your targeted dish) that you are going to aquire.\n"
        prompt += "location: the location that you intend to go.\n"
        prompt += "2. Whenever you generate broadcast message, you are telling your intention in the next step.\n"
        prompt += "3. When you receive other agents' broadcast messages, you should interpret them in the same way and make your decision accordingly.\n"
        prompt += "4. The id in the broadcast you receive in this step always refer to the last 'current dishes' state.\n"
    else:
        prompt += "1. The broadcast message should be in natural language.\n"
        prompt += "2. Whenever you generate broadcast message, you are telling your intention in the next step. Including currently which task you are on, which ingredient you are preparing, where are you planning to go and necessary explanations.\n"
        prompt += "3. When you receive other agents' broadcast messages, you should notice that they are generated based on the previous game state.\n"

    prompt += "\n"
    return prompt

def game_instruction_prompt(env, self_agent):
    prompt = ""
    prompt += f"In this game, there are totally {len(env.agents)} agents available: "
    prompt += ", ".join([agent.name for agent in env.agents]) + "\n"
    prompt += f"Your name is {self_agent.name}.\n"
    prompt += "In each step, you should plan your action based on the given information and come up with a broadcast message (following the broadcast protocol) for other agents in next step.\n"
    prompt += "Several previous steps of the game are provided and then comes the current step that you need to work on.\n"
    prompt += "Your output should be in this format:\n"
    prompt += "-action:\nactions to take\n\n-broadcast:\nbroadcast message\n"
    # prompt += "The action should be in the format consistent with examples: ActionName_Place (Only except for \'get\', the format should be: ActionName_Item_Place)\n"

    prompt += "\n"
    return prompt

def extract_action(text):
    # List of action types
    action_types = ["noop", "goto", "put", "activate", "get"]
    
    # Pattern for the actions
    pattern = r'-action:\s*((' + '|'.join(action_types) + r')(_[a-zA-Z0-9_]+)?)'
    
    matches = re.findall(pattern, text)
    
    # Extracting just the full action names from the returned tuples
    actions = [match[0] for match in matches]

    if len(actions) != 1:
        raise ValueError(f"Expected exactly one action, but got {len(actions)}: {actions}")
    
    return actions[0]

def extract_broadcast(text):
    # Pattern to match the broadcast message
    pattern = r'-broadcast:\s*([\s\S]*?)(?:\n-\w+:|$)'

    match = re.search(pattern, text)
    if match:
        msg = match.group(1).strip()
        # Remove the surrounding braces
        msg = msg.replace("{{", "").replace("}}", "")
        return msg
    else:
        raise ValueError("No broadcast message found in the response.")

class LLMAgent(object):
    def __init__(self, id_env_agents: int, model: str, env, name: str=None, bc_str: bool=True):
        self.id_env_agents = id_env_agents
        self.model = model
        self.env = env
        self.bc_str = bc_str

        self.env_agent = self.env.agents[id_env_agents]
        self.env_agent.name = name if name is not None else f"agent{id_env_agents}"

        if "gpt" in self.model:
            if os.path.exists("./key.txt"):
                openai.api_key = open("./key.txt", "r").read().strip()
            else:
                openai.api_key = os.getenv("OPENAI_API_KEY")
        else:
            raise NotImplementedError(f"Model {self.model} not implemented.")
        
        self.steps = 0
        self.history = []
        self.feedbacks = []
        self.suggestions = []
        self.broadcast = None
        self.broadcast_sync = None

        self.initial_history_len = 0
        self.look_ahead_steps = 5
        self.init_history()

    def init_history(self):
        pre_prompt = ("user", rules(self.env, True) + broadcast_protocol(self.bc_str))
        if self.bc_str:
            example = open("./assets/prompt_structured.txt", "r").read().split('###\n')[1].split('***\n')
        else:
            example = open("./assets/prompt_nl.txt", "r").read().split('###\n')[1].split('***\n')
        example_history = []
        for idx, exp in enumerate(example):
            if idx % 2 == 0:
                example_history.append(("user", exp))
            else:
                example_history.append(("assistant", exp))
        info_prompt = ("user", game_instruction_prompt(self.env, self.env_agent))

        self.history = [pre_prompt] + example_history + [info_prompt]
        self.initial_history_len = len(self.history)

    def collect_broadcast(self, agents):
        self.broadcast_from_others = []
        for agent in agents:
            if agent.id_env_agents != self.id_env_agents:
                self.broadcast_from_others.append([agent.env_agent.name, agent.broadcast])

        prompt = "-peers' broadcast messages:\n"
        for name, broadcast in self.broadcast_from_others:
            prompt += f"{name}: {broadcast}\n"
        prompt += "\n"
        return prompt
    
    def step(self, obs, agents):
        self.steps += 1
        prompt = convert_to_prompt(obs) + self.collect_broadcast(agents)
        # print current prompt
        print(f"Step {self.steps}:\n")

        # cap message length
        if len(self.history) < self.look_ahead_steps + self.initial_history_len:
            self.history = prepend_history(self.history, prompt, verbose=True)
        else:
            self.history = self.history[:self.initial_history_len] + self.history[self.initial_history_len+2:]
            self.history = prepend_history(self.history, prompt, verbose=True)

        reply = chat_llm(self.history, temperature=0.1, model=self.model)
        print("-"*20 + "LLM reply:")
        print(reply)
        print("-"*20)
        try:
            action = extract_action(reply)
        except:
            action = "noop"
        try:
            broadcast = extract_broadcast(reply)
        except:
            broadcast = None

        # update broadcast and history
        self.broadcast_sync = broadcast
        self.history = prepend_history(
            self.history,
            f"-action:\n{action}\n\n-broadcast:\n{broadcast}\n",
            role="assistant", 
            verbose=True
        )

        return action
    
    def sync(self):
        self.broadcast = self.broadcast_sync
        self.broadcast_sync = None
        return self.broadcast
    