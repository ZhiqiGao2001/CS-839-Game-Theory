import argparse
import json
import os
import sys
import time
import re
import openai
import tiktoken

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from levels.utils import convert_to_prompt
from overcooked import World
from utils.llm import chat_llm, chat_llm_vicuna, prepend_history, rules
from agents.llm_agent import LLMAgent, extract_action, extract_broadcast


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def extract_actions(text):
    # List of action types
    action_types = ["noop", "goto", "put", "activate", "get"]
    
    # Pattern for the actions
    pattern = r'((' + '|'.join(action_types) + r')_agent\d+(_[a-zA-Z0-9_]+)?)'
    
    matches = re.findall(pattern, text)
    
    # Extracting just the full action names from the returned tuples
    actions = [match[0] for match in matches]
    return actions



def main(model, num_agents, level_to_run, args):
    NUM_AGENTS = num_agents
    alphas = [ 1.0, 1.5, 2.0, 2.5, 3.0 ]
    if level_to_run == 'all':
        levels = [  
                    'level_0',
                    'level_1',
                    'level_2',
                    'level_3',
                    'level_4',
                    'level_5',
                    'level_6',
                    'level_7',
                    'level_8',
                    'level_9',
                    'level_10',
                    'level_11', 
                    'level_12']
    else:
        levels = [level_to_run]

    for level in levels:
        save_file_name = f'result_{level}_{NUM_AGENTS}_{model}_{"struct" if args.structured else "nl"}.json'
        if os.path.exists(save_file_name):
            with open(save_file_name, 'r') as f:
                table = json.load(f)
        else:
            table = {}
        
        for alpha in alphas :
            if str(alpha) in table.keys():
                continue
            env = World(recipe_filename='./assets/recipe.json', task_filename='./assets/tasks_level_final.json',
                         level=level, use_task_lifetime_interval_oracle=True,
                        alpha=alpha, beta=2.5, num_agents=NUM_AGENTS, override_agent=True)

            max_episode = 3
            max_steps = env.max_steps

            total = 0
            success = 0
            failed = 0

            total_action_histories = []
            total_action_success_histories = []
            total_prompts = []
            for eps_id in range(max_episode):
                obs = env.reset()
                agents = [LLMAgent(i, model, env, bc_str=args.structured) for i in range(NUM_AGENTS)]

                goal = env.task
                step = 0
                done = False
                action_histories = []
                action_success_histories = []

                while (step < max_steps):
                    plan = []
                    for agent in agents:
                        parts = agent.step(obs, agents).split('_')
                        parts.insert(1, 'agent' + str(agent.id_env_agents))
                        plan.append("_".join(parts))
                        
                    # synchronize the agents
                    for agent in agents:
                        agent.sync()

                    if plan:
                        obs, done, info = env.step(plan)
                    action_histories.append(plan)
                    # if with_feedback:
                    #     feedback = '-execution error messages:\n  --  ' + str(env.feedback) + '\n'
                    #     suggestions = '-execution suggestions:\n  --  ' + str(env.suggestions) + '\n'

                    print(info['action_success'])
                    action_success_histories.append(env.action_success_history)
                    step += 1

                total += env.success_count + env.failed_count + len(env.task_manager._current_task_list)
                success += env.success_count
                failed += env.failed_count
                total_action_histories.append(action_histories)
                total_action_success_histories.append(env.action_success_history)

            table[alpha] = {
                'total' : total,
                'success' : success,
                'failed': failed,
                'alpha': alpha,
                'noop_count': env.noop_count,
                'action_history': total_action_histories,
                'action_success_history': total_action_success_histories,
                'prompt_history': total_prompts
            }
            with open(save_file_name, 'w') as fp:
                json.dump(table, fp)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="invoking GPT")

    # Add the arguments
    parser.add_argument('--model_name', metavar='model_name', type=str, choices=['gpt-4', 'gpt-4-azure', 'gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'vicuna', 'claude-2', 'palm-2'], help='model to use')
    parser.add_argument('--num_agents', metavar='num_agents', type=int, required=True ,help='number of agents')
    parser.add_argument('--level', metavar='level', type=str, required=True ,help='level of the game')
    parser.add_argument('--structured', action='store_true', default=False, help='use structured prompt')
    # Parse the arguments
    args = parser.parse_args()

    main(
        model = args.model_name,
        num_agents = int(args.num_agents), 
        level_to_run = args.level,
        args = args
    )