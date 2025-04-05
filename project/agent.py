import json
import time
from openai import OpenAI
import ast
from tqdm import tqdm
import game_1
import os

def dict_matches_string(s, d):
    """
      Given a string `s` containing a dictionary (either as a standalone literal
      like "{...}" or with an assignment, e.g., "VAR = { ... }")
      and a dictionary `d`, return True if every key-value pair in `d` matches the corresponding
      entries in the parsed dictionary from `s`, otherwise return False.
      """
    try:
        s = s.strip()
        # If the string starts with a curly brace, assume it's just the dictionary literal.
        if s[0] == "{":
            dict_str = s
        else:
            # Otherwise, split on the first '=' and use the part after it.
            parts = s.split('=', 1)
            if len(parts) < 2:
                return False
            dict_str = parts[1].strip()
        # Convert the string representation of the dict into a Python dictionary.
        parsed_dict = ast.literal_eval(dict_str)
    except Exception as e:
        # If there's an error in parsing, return False.
        return False

    def is_subset(small, big):
        """
        Check recursively if every key-value pair in `small` is present in `big`.
        For nested dictionaries, the check is performed recursively.
        """
        if isinstance(small, dict) and isinstance(big, dict):
            for k, v in small.items():
                if k not in big:
                    return False
                if not is_subset(v, big[k]):
                    return False
            return True
        else:
            return small == big

    return is_subset(d, parsed_dict)


class CooperativeAgent_game1:
    def __init__(self, role, model_name='gpt-4o', config_path='config.json'):
        self.role = role
        self.model_name = model_name
        # Load API key from configuration file
        with open(config_path, 'r', encoding="utf-8") as f:
            keys = json.load(f)
            self.openai_api_key = keys.get("openai_api_key", None)
        self.openai_client = OpenAI(api_key=self.openai_api_key)

    def making_response(self, incoming_message, structured=False):
        # Send the message to the OpenAI API and get a response
        if structured:
            system_prompt = game_1.protocol_system_message
        else:
            system_prompt = game_1.default_system_message
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


def run_tests(testing_agent, N_test=500, structured=True):
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


if __name__ == "__main__":
    # Create an instance of the testing agent.
    N_count = 100
    model_name = 'gpt-4o-mini'
    testing_agent = CooperativeAgent_game1("role", model_name=model_name)

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
    structured_results = run_tests(testing_agent, N_test=N_count, structured=True)
    unstructured_results = run_tests(testing_agent, N_test=N_count, structured=False)

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
    if not os.path.exists("test_results_game_1.json"):
        with open("test_results_game_1.json", "w") as f:
            json.dump({}, f, indent=4)
    with open("test_results_game_1.json", "r") as f:
        data = json.load(f)

    # Update the data.
    data[model_name] = overall_results

    # Then, open the file in write mode to save the updated data.
    with open("test_results_game_1.json", "w") as f:
        json.dump(data, f, indent=4)