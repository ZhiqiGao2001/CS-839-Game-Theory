import json
import time
from openai import OpenAI
import ast
from tqdm import tqdm
import os

import game_1
import game_2


def dict_matches_string(s, d):
    """
    Given a string `s` containing a dictionary (either as a standalone literal
    like "{...}", with an assignment, e.g., "VAR = { ... }", or wrapped in code blocks
    such as triple backticks), and a dictionary `d`, return True if every key-value pair in `d`
    matches the corresponding entries in the parsed dictionary from `s`, otherwise return False.
    """
    try:
        s = s.strip()

        # Remove code block markers if present (e.g., ```json ... ```).
        if s.startswith("```"):
            lines = s.splitlines()
            # Remove first line if it starts with ```
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line if it ends with ```
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            s = "\n".join(lines).strip()

        # If the string starts with a curly brace, assume it's just the dictionary literal.
        if s[0] == "{":
            dict_str = s
        else:
            # Otherwise, split on the first '=' and use the part after it.
            parts = s.split('=', 1)
            if len(parts) < 2:
                return False
            dict_str = parts[1].strip()

        try:
            # Try to parse using ast.literal_eval first.
            parsed_dict = ast.literal_eval(dict_str)
        except Exception:
            # If that fails, try using json.loads.
            parsed_dict = json.loads(dict_str)
    except Exception as e:
        # If there's an error in parsing, return False.
        return False

    def is_subset(small, big):
        """
        Recursively check if every key-value pair in `small` is present in `big`.
        For nested dictionaries, the check is performed recursively.
        """
        if isinstance(small, dict) and isinstance(big, dict):
            for k, v in small.items():
                if k not in big:
                    return False
                if not is_subset(v, big[k]):
                    return False
            return True
        elif isinstance(small, list) and isinstance(big, list):
            # For lists, require the lists to be equal.
            return small == big
        else:
            return small == big

    return is_subset(d, parsed_dict)


class CooperativeAgent_game_simple:
    def __init__(self, role, model_name='gpt-4o', config_path='config.json', prompt_=("structured", "unstructured")):
        self.role = role
        self.model_name = model_name
        # Load API key from configuration file
        with open(config_path, 'r', encoding="utf-8") as f:
            keys = json.load(f)
            self.openai_api_key = keys.get("openai_api_key", None)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.structured_message = prompt_[0]
        self.unstructured_message = prompt_[1]

    def making_response(self, incoming_message, structured=False):
        # Send the message to the OpenAI API and get a response
        if structured:
            system_prompt = self.structured_message
        else:
            system_prompt = self.unstructured_message
        prompt_detail = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": incoming_message},
        ]

        response_llm = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=prompt_detail,
        )
        content = response_llm.choices[0].message.content
        return content


def run_tests_game_1(testing_agent, N_test=500, structured=True, save_failures=False, fail_file=None):
    results = {}
    failures = []
    for _ in tqdm(range(N_test), desc=f"Game1 {'Structured' if structured else 'Unstructured'}"):
        (msg, correct), mtype = game_1.random_message(structured=structured)
        resp = testing_agent.making_response(msg, structured=structured)
        ok = dict_matches_string(resp, correct)

        results.setdefault(mtype, {"success":0,"failure":0})
        if ok:
            results[mtype]["success"] += 1
        else:
            results[mtype]["failure"] += 1
            if save_failures:
                failures.append({
                    "message_type": mtype,
                    "incoming": msg,
                    "expected": correct,
                    "got": resp
                })

    if save_failures and fail_file:
        with open(fail_file, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2)
    return results

def game_1_run(N_count=100, model_name='gpt-4o', save=False):
    prompt = (game_1.protocol_system_message, game_1.default_system_message)
    agent = CooperativeAgent_game_simple("role", model_name=model_name, prompt_=prompt)

    # Structured
    struct_results = run_tests_game_1(
        agent, N_test=N_count, structured=True,
        save_failures=True,
        fail_file="results/game1_structured_failures.json"
    )
    # Unstructured
    unstruct_results = run_tests_game_1(
        agent, N_test=N_count, structured=False,
        save_failures=True,
        fail_file="results/game1_unstructured_failures.json"
    )

    overall = {"structured": struct_results, "unstructured": unstruct_results}
    print("Game 1 results:", overall)
    if save:
        with open("test_results_game_1.json","w") as f:
            json.dump({model_name: overall}, f, indent=2)

def run_tests_game_2(testing_agent, N_test=500, structured=True, save_failures=False, fail_file=None):
    results = {}
    failures = []
    for _ in tqdm(range(N_test), desc=f"Game2 {'Structured' if structured else 'Unstructured'}"):
        (msg, correct), mtype = game_2.random_message(structured=structured)
        resp = testing_agent.making_response(msg, structured=structured)
        ok = dict_matches_string(resp, correct)

        results.setdefault(mtype, {"success":0,"failure":0})
        if ok:
            results[mtype]["success"] += 1
        else:
            results[mtype]["failure"] += 1
            if save_failures:
                failures.append({
                    "message_type": mtype,
                    "incoming": msg,
                    "expected": correct,
                    "got": resp
                })

    if save_failures and fail_file:
        with open(fail_file, "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2)
    return results

def game_2_run(N_count=100, model_name='gpt-4o', save=False):
    prompt = (game_2.protocol_system_message, game_2.default_system_message)
    agent = CooperativeAgent_game_simple("role", model_name=model_name, prompt_=prompt)

    # Unstructured
    unstruct_results = run_tests_game_2(
        agent, N_test=N_count, structured=False,
        save_failures=True,
        fail_file="results/game2_unstructured_failures.json"
    )
    # Structured
    struct_results = run_tests_game_2(
        agent, N_test=N_count, structured=True,
        save_failures=True,
        fail_file="results/game2_structured_failures.json"
    )

    overall = {"structured": struct_results, "unstructured": unstruct_results}
    print("Game 2 results:", overall)
    if save:
        with open("test_results_game_2.json","w") as f:
            json.dump({model_name: overall}, f, indent=2)


if __name__ == "__main__":
    # Run and save both summary + detailed failures
    game_1_run(N_count=10, model_name='gpt-4o', save=True)
    # game_2_run(N_count=100, model_name='gpt-4o', save=True)
