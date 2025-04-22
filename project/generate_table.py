import pandas as pd
import json

def parse_to_table(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
    # Step 1: Identify all actions
    all_actions = set()
    for model_data in data.values():
        for msg_type_data in model_data.values():
            all_actions.update(msg_type_data.keys())

    # Step 2: Build rows with MultiIndex columns
    rows = []
    index = []

    for model, types in data.items():
        row = {}
        for action in sorted(all_actions):
            for msg_type in ["structured", "unstructured"]:
                result = types.get(msg_type, {}).get(action)
                if result:
                    total = result["success"] + result["failure"]
                    accuracy = (result["success"] / total) * 100 if total else 0
                else:
                    accuracy = None
                row[(action, msg_type)] = round(accuracy, 2) if accuracy is not None else None
        rows.append(row)
        index.append(model)

    # Step 3: Create the DataFrame
    df = pd.DataFrame(rows, index=index)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    df = df.sort_index(axis=1, level=0)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.expand_frame_repr', False)
    # Step 4: Display the DataFrame
    print("Model names:" + json_path)
    print(df)
    print()


if __name__ == "__main__":
    # Example usage
    parse_to_table('test_results_game_1_gpt-4o.json')
    parse_to_table("test_results_game_2_gpt-4o.json")
    parse_to_table('test_results_game_3_gpt-4o.json')
    parse_to_table('test_results_game_1_gpt-4o-mini.json')
    parse_to_table('test_results_game_2_gpt-4o-mini.json')
    parse_to_table('test_results_game_3_gpt-4o-mini.json')


