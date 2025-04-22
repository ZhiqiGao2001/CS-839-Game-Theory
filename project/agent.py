import json
import ast
from openai import OpenAI
from tqdm import tqdm

import game_1
import game_2
from project import game_3


def parsing_dict(string):
    try:
        s = string.strip()

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
            return parsed_dict

        except Exception:
            # If that fails, try using json.loads.
            parsed_dict = json.loads(dict_str)
            return parsed_dict
    except Exception as e:
        # If there's an error in parsing, return False.
        return False
    return parsed_dict


def dict_matches_string(s, d):
    """
    Given a string `s` containing a dictionary (either as a standalone literal
    like "{...}", with an assignment, e.g., "VAR = { ... }", or wrapped in code blocks
    such as triple backticks), and a dictionary `d`, return True if every key-value pair in `d`
    matches the corresponding entries in the parsed dictionary from `s`, otherwise return False.
    """
    parsed_dict = parsing_dict(s)

    def is_subset(small, big):
        """
        Recursively check if every key-value pair in `small` is present in `big`,
        comparing both keys and string values case‑insensitively.
        """
        # Dict vs Dict
        if isinstance(small, dict) and isinstance(big, dict):
            # Build a lookup of big’s keys in lowercase → original value
            big_lower = {
                (k.casefold() if isinstance(k, str) else k): v
                for k, v in big.items()
            }
            for k, v in small.items():
                key_norm = k.casefold() if isinstance(k, str) else k
                if key_norm not in big_lower:
                    return False
                if not is_subset(v, big_lower[key_norm]):
                    return False
            return True

        # List vs List: require same length and each element subset‑matches
        if isinstance(small, list) and isinstance(big, list):
            if len(small) != len(big):
                return False
            return all(is_subset(a, b) for a, b in zip(small, big))

        # String vs String: compare case‑insensitive
        if isinstance(small, str) and isinstance(big, str):
            return small.casefold() == big.casefold()

        # Fallback to direct equality for other types
        return small == big

    return is_subset(d, parsed_dict)

class CooperativeAgent_game_simple:
    def __init__(self, role, model_name='gpt-4o', config_path='config.json', prompt_=(None, None)):
        self.role = role
        self.model_name = model_name
        with open(config_path, 'r', encoding='utf-8') as f:
            keys = json.load(f)
        self.openai_client = OpenAI(api_key=keys.get('openai_api_key'))
        self.structured_message, self.unstructured_message = prompt_

    def making_response(self, incoming_message, structured=False):
        system_prompt = self.structured_message if structured else self.unstructured_message
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": incoming_message},
        ]
        resp = self.openai_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return resp.choices[0].message.content


def run_tests_game(template_module, run_func, testing_agent, N_test=500, structured=True, save_failures=False, fail_file=None):
    results = {}
    failures = []
    for _ in tqdm(range(N_test), desc=f"{run_func.__name__} {'Structured' if structured else 'Unstructured'}"):
        (msg, correct), mtype = template_module.random_message(structured=structured)
        resp = testing_agent.making_response(msg, structured=structured)
        ok = dict_matches_string(resp, correct)
        results.setdefault(mtype, {"success": 0, "failure": 0})
        if ok:
            results[mtype]["success"] += 1
        else:
            results[mtype]["failure"] += 1
            if save_failures:
                failures.append({
                    "message_type": mtype,
                    "incoming": msg,
                    "expected": correct,
                    "got": parsing_dict(resp)
                })
    if save_failures and fail_file:
        with open(fail_file, 'w', encoding='utf-8') as f:
            json.dump(failures, f, indent=2)
    return results


def game_1_run(N_count=100, model_name='gpt-4o', save=False):
    prompt = (game_1.protocol_system_message, game_1.default_system_message)
    agent = CooperativeAgent_game_simple('game1', model_name, prompt_=prompt)
    struct = run_tests_game(game_1, game_1_run, agent, N_test=N_count, structured=True,
                             save_failures=save,
                             fail_file=f'results/game1_structured_failures_{model_name}.json')
    unstruct = run_tests_game(game_1, game_1_run, agent, N_test=N_count, structured=False,
                               save_failures=save,
                               fail_file=f'results/game1_unstructured_failures_{model_name}.json')
    print('Game 1:', {'structured': struct, 'unstructured': unstruct})
    if save:
        with open(f'test_results_game_1_{model_name}.json','w') as f:
            json.dump({'game1': {'structured': struct, 'unstructured': unstruct}}, f, indent=2)


def game_2_run(N_count=100, model_name='gpt-4o', save=False):
    prompt = (game_2.protocol_system_message, game_2.default_system_message)
    agent = CooperativeAgent_game_simple('game2', model_name, prompt_=prompt)
    # Unstructured then structured
    unstruct = run_tests_game(game_2, game_2_run, agent, N_test=N_count, structured=False,
                               save_failures=save,
                               fail_file=f'results/game2_unstructured_failures_{model_name}.json')
    struct = run_tests_game(game_2, game_2_run, agent, N_test=N_count, structured=True,
                             save_failures=save,
                             fail_file=f'results/game2_structured_failures_{model_name}.json')
    print('Game 2:', {'structured': struct, 'unstructured': unstruct})
    if save:
        with open(f'test_results_game_2_{model_name}.json','w') as f:
            json.dump({'game2': {'structured': struct, 'unstructured': unstruct}}, f, indent=2)


def run_tests_game_3(testing_agent, N_test=500, structured=True, save_failures=False, fail_file=None):
    return run_tests_game(game_3, run_tests_game_3, testing_agent,
                          N_test=N_test, structured=structured,
                          save_failures=save_failures, fail_file=fail_file)


def game_3_run(N_count=100, model_name='gpt-4o', save=False):
    prompt = (game_3.protocol_system_message, game_3.default_system_message)
    agent = CooperativeAgent_game_simple('game3', model_name, prompt_=prompt)
    # Test both modes
    struct = run_tests_game(game_3, game_3_run, agent, N_test=N_count, structured=True,
                            save_failures=save,
                            fail_file=f'results/game3_structured_failures_{model_name}.json')
    unstruct = run_tests_game(game_3, game_3_run, agent, N_test=N_count, structured=False,
                              save_failures=save,
                              fail_file=f'results/game3_unstructured_failures_{model_name}.json')
    print('Game 3:', {'structured': struct, 'unstructured': unstruct})
    if save:
        with open(f'test_results_game_3_{model_name}.json','w') as f:
            json.dump({'game3': {'structured': struct, 'unstructured': unstruct}}, f, indent=2)


if __name__ == '__main__':
    N_count = 200
    game_1_run(N_count=N_count, model_name='gpt-4o-mini', save=True)
    game_2_run(N_count=N_count, model_name='gpt-4o-mini', save=True)
    game_3_run(N_count=N_count, model_name='gpt-4o-mini', save=True)
    game_1_run(N_count=N_count, model_name='gpt-4o', save=True)
    game_2_run(N_count=N_count, model_name='gpt-4o', save=True)
    game_3_run(N_count=N_count, model_name='gpt-4o', save=True)
