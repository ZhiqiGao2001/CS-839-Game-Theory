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


def run_tests_game_1(testing_agent, N_test=500, structured=True):
    """
    Run tests for a given number of messages and a mode (structured or unstructured).
    Returns a dictionary with the success and failure counts for each message type.
    """
    results = {}  # Dictionary keyed by message_type with {"success": count, "failure": count}
    for i in tqdm(range(N_test), desc="Testing", unit="message"):
        # Generate a random message using the provided mode (structured or unstructured)
        (message_content, correct_response), message_type = game_1.random_message(structured=structured)
        # Get the agent's response according to the mode
        llm_response = testing_agent.making_response(message_content, structured=structured)
        # Initialize the result entry for this message type if needed
        if message_type not in results:
            results[message_type] = {"success": 0, "failure": 0}
        # Check if the agent's response matches the correct response
        if dict_matches_string(llm_response, correct_response):
            results[message_type]["success"] += 1
        else:
            results[message_type]["failure"] += 1
    return results


def game_1_run(N_count=100, model_name='gpt-4o', save=False):
    prompt = (game_1.protocol_system_message, game_1.default_system_message)
    testing_agent = CooperativeAgent_game_simple("role", model_name=model_name, prompt_=prompt)

    # content, correct_response = game_1.gather_message(structured=False)
    # print("Incoming message:", content)
    # print("Correct response:", correct_response)
    # # Get the agent's response
    # llm_response = testing_agent.making_response(content, structured=False)
    # print("LLM response:", llm_response)
    # # Check if the agent's response matches the correct response
    # if dict_matches_string(llm_response, correct_response):
    #     print("Success!")
    # else:
    #     print("Failure!")
    #
    # exit()
    # Run tests for both structured and unstructured messages.
    structured_results = run_tests_game_1(testing_agent, N_test=N_count, structured=True)
    unstructured_results = run_tests_game_1(testing_agent, N_test=N_count, structured=False)

    # Combine the results into one dictionary for comparison.
    overall_results = {
        "structured": structured_results,
        "unstructured": unstructured_results
    }

    # Print out the results
    print("Test results (success/failure counts by message type):")
    print(overall_results)
    # save the result to a json file
    # First, open the file in read mode to load the data.
    if save:
        target_path = "test_results_game_1.json"
        # Check if the file exists and create it if not.
        save_result(target_path, model_name, overall_results)


def save_result(target_path, model_name, overall_results):
    if not os.path.exists(target_path):
        with open(target_path, "w") as f:
            json.dump({}, f, indent=4)
    with open(target_path, "r") as f:
        data = json.load(f)

        # Update the data.
    data[model_name] = overall_results

    # Then, open the file in write mode to save the updated data.
    with open(target_path, "w") as f:
        json.dump(data, f, indent=4)


def run_tests_game_2(testing_agent, N_test=500, structured=True):
    """
    Run tests for game_2 for a given number of messages and mode (structured or unstructured).
    Returns a dictionary with the success and failure counts for each message type.
    """
    results = {}  # Dictionary keyed by message_type with {"success": count, "failure": count}
    for i in tqdm(range(N_test), desc="Testing Game 2", unit="message"):
        # Generate a random message using the provided mode (structured or unstructured)
        (message_content, correct_response), message_type = game_2.random_message(structured=structured)
        # Get the agent's response according to the mode
        llm_response = testing_agent.making_response(message_content, structured=structured)
        # Initialize the result entry for this message type if needed
        if message_type not in results:
            results[message_type] = {"success": 0, "failure": 0}
        # Check if the agent's response matches the correct response
        if dict_matches_string(llm_response, correct_response):
            results[message_type]["success"] += 1
        else:
            results[message_type]["failure"] += 1
            print("LLM response:", llm_response)
            print("Correct Ver:", correct_response)
    return results


def game_2_run(N_count=100, model_name='gpt-4o', save=False):
    """
    Run the full testing suite for game_2 using both structured and unstructured messages.
    """
    # Initialize the testing agent for game_2
    prompt = (game_2.protocol_system_message, game_2.default_system_message)
    testing_agent = CooperativeAgent_game_simple("role", model_name=model_name, prompt_=prompt)

    # Run tests for both structured and unstructured messages.
    unstructured_results = run_tests_game_2(testing_agent, N_test=N_count, structured=False)
    structured_results = run_tests_game_2(testing_agent, N_test=N_count, structured=True)

    # Combine the results into one dictionary for comparison.
    overall_results = {
        "structured": structured_results,
        "unstructured": unstructured_results
    }

    # Print out the results.
    print("Test results (success/failure counts by message type) for Game 2:")
    print(overall_results)

    # Save the result to a json file if required.
    if save:
        target_path = "test_results_game_2.json"
        save_result(target_path, model_name, overall_results)


if __name__ == "__main__":
    # Create an instance of the testing agent.
    # game_1_run(N_count=10, model_name='gpt-4o-mini', save=True)
    game_2_run(N_count=10, model_name='gpt-4o', save=True)