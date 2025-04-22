import json
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import os



def analyze_failures(failure_file):
    """Analyze failures from a game test JSON file."""
    # Load the failure data
    with open(failure_file, 'r', encoding='utf-8') as f:
        failures = json.load(f)

    if not failures:
        print(f"No failures found in {failure_file}")
        return None

    # Create a DataFrame for easier analysis
    df = pd.DataFrame(failures)

    # Extract expected vs. actual ACTION values
    df['expected_action'] = df['expected'].apply(lambda e: e['ACTION'])
    df['got_action']      = df['got'].apply(lambda g: g['ACTION'])

    # --- FULL CONFUSION MATRIX ON ALL PREDICTIONS ---
    print("\nFull Confusion Matrix (All predictions):")
    full_cm = pd.crosstab(
        df['expected_action'],
        df['got_action'],
        margins=True,
        margins_name='Total'
    )
    print(full_cm)

    print("\nFull Percentage Matrix (% by expected action):")
    full_pct = pd.crosstab(
        df['expected_action'],
        df['got_action'],
        normalize='index'
    ).round(2) * 100
    print(full_pct)
    # -----------------------------------------------

    # Add a column for response format type, handling direct dict objects
    def determine_format_type(response):
        if isinstance(response, dict):
            return 'dict_object'
        elif isinstance(response, str):
            if response.startswith('{') or response.startswith('```'):
                return 'dict_string'
            elif response.startswith('ACTION_TEMPLATE'):
                return 'template'
            else:
                return 'other'
        else:
            return 'unknown'

    df['resp_format'] = df['got'].apply(determine_format_type)

    # Basic statistics
    total_failures = len(df)
    failure_by_type = df['message_type'].value_counts()
    failure_by_format = df['resp_format'].value_counts()

    print(f"\nTotal failures: {total_failures}")
    print("\nFailures by message type:")
    print(failure_by_type)
    print("\nFailures by response format:")
    print(failure_by_format)

    # Generate statistics dataframe
    stats_df = pd.DataFrame({
        'Count': failure_by_type,
        'Percentage': (failure_by_type / total_failures * 100).round(2)
    })
    stats_df['Cumulative_Percentage'] = stats_df['Percentage'].cumsum().round(2)
    stats_df['Percentage'] = stats_df['Percentage'].map(lambda x: f"{x}%")
    stats_df['Cumulative_Percentage'] = stats_df['Cumulative_Percentage'].map(lambda x: f"{x}%")

    print("\nFailure Statistics:")
    print(stats_df)

    # Response format statistics
    format_stats = pd.DataFrame({
        'Count': failure_by_format,
        'Percentage': (failure_by_format / total_failures * 100).round(2)
    })
    format_stats['Percentage'] = format_stats['Percentage'].map(lambda x: f"{x}%")

    print("\nResponse Format Statistics:")
    print(format_stats)

    # Analyze specific failure modes
    action_mismatches = []
    field_mismatches = {
        'ACTION': [],
        'LOCATION.COORDINATE': [],
        'LOCATION.AREA': [],
        'RESOURCE.TYPE': [],
        'RESOURCE.QUANTITY': [],
        'STRUCTURE': []
    }

    for _, row in df.iterrows():
        expected = row['expected']
        got = row['got']
        try:
            # Parse templated and string formats into dicts
            if row['resp_format'] == 'template':
                dict_str = got.replace('ACTION_TEMPLATE = ', '')
                got = eval(dict_str)
            elif row['resp_format'] == 'dict_string':
                text = got.strip('`')
                try:
                    got = json.loads(text)
                except:
                    got = eval(text)

            # Check action mismatches
            if row['got_action'] != row['expected_action']:
                action_mismatches.append({
                    'message_type': row['message_type'],
                    'message': row['incoming'],
                    'expected_action': row['expected_action'],
                    'got_action': row['got_action']
                })

            # If action matches, check fields
            elif got['LOCATION']['COORDINATE'] != expected['LOCATION']['COORDINATE']:
                field_mismatches['LOCATION.COORDINATE'].append({
                    'message_type': row['message_type'],
                    'message': row['incoming'],
                    'expected': expected['LOCATION']['COORDINATE'],
                    'got': got['LOCATION']['COORDINATE']
                })
            # (similar blocks for AREA, RESOURCE.TYPE, RESOURCE.QUANTITY, STRUCTURE...)
        except Exception as e:
            print(f"Error parsing {row['incoming']}: {e}")

    # Mismatch-based analysis (optional)
    if action_mismatches:
        am_df = pd.DataFrame(action_mismatches)
        print("\nAction mismatches (counts):")
        print(am_df.groupby(['expected_action', 'got_action']).size())

    # Return summary dict
    return {
        'total_failures': total_failures,
        'failure_stats': stats_df,
        'format_stats': format_stats,
        'confusion_matrix': full_cm,
        'full_percentage_matrix': full_pct
    }



def generate_visualizations(stats, output_dir, game_name=None, model_name=None, is_structured=None):
    """Generate visualizations from the failure statistics."""
    if not stats:
        return

    # Extract metadata from output_dir if not provided explicitly
    if game_name is None or model_name is None or is_structured is None:
        dir_parts = output_dir.split(os.sep)
        if len(dir_parts) >= 2:
            game_name = dir_parts[-2] if game_name is None else game_name
            is_structured = "structured" in dir_parts[-1] if is_structured is None else is_structured

            # Extract model name from the directory name
            if model_name is None and "_" in dir_parts[-1]:
                model_parts = dir_parts[-1].split("_")
                if len(model_parts) > 1:
                    model_name = model_parts[-1]

    # Create caption base and filename prefix
    caption_base = f"{game_name or 'Game'}"
    if model_name:
        caption_base += f" - {model_name}"
    caption_base += f" ({'Structured' if is_structured else 'Unstructured'} Messages)"

    # Create file name prefix with metadata
    structure_type = "structured" if is_structured else "unstructured"
    file_prefix = f"{game_name}_{structure_type}"
    if model_name:
        file_prefix += f"_{model_name}"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Failure type pie chart
    failure_counts = stats['failure_stats']['Count']
    plt.figure(figsize=(10, 6))
    plt.pie(failure_counts, labels=failure_counts.index, autopct='%1.1f%%')
    plt.title(f'Failures by Message Type\n{caption_base}')
    plt.savefig(os.path.join(output_dir, f'{file_prefix}_failure_types_pie.png'))
    plt.close()

    # Response format bar chart
    format_counts = stats['format_stats']['Count']
    plt.figure(figsize=(10, 6))
    format_counts.plot(kind='bar', color='skyblue')
    plt.title(f'Failures by Response Format\n{caption_base}')
    plt.xlabel('Format Type')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'{file_prefix}_format_failures_bar.png'))
    plt.close()

    # Confusion matrix heatmap
    if stats['confusion_matrix'] is not None:
        conf_matrix = stats['confusion_matrix'].iloc[:-1, :-1]  # Remove totals
        plt.figure(figsize=(10, 8))
        plt.imshow(conf_matrix, cmap='Blues')
        plt.colorbar(label='Count')
        plt.xticks(range(len(conf_matrix.columns)), conf_matrix.columns, rotation=45, fontsize=18)
        plt.yticks(range(len(conf_matrix.index)), conf_matrix.index, fontsize=18)
        plt.xlabel('Predicted Action', fontsize=18)
        plt.ylabel('Expected Action', fontsize=18)
        plt.title(f'Action Confusion Matrix\n{caption_base}', fontsize=20)

        # Add text annotations
        for i in range(len(conf_matrix.index)):
            for j in range(len(conf_matrix.columns)):
                plt.text(j, i, conf_matrix.iloc[i, j],
                         ha="center", va="center",
                         color="white" if conf_matrix.iloc[i, j] > 3 else "black",
                         fontsize=20,  # Increased font size from default
                         fontweight='bold')  # Making the text bold for better visibility

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{file_prefix}_confusion_matrix.png'))
        plt.close()

    # Field mismatch visualization
    if 'field_mismatch_stats' in stats and stats['field_mismatch_stats']:
        fields = list(stats['field_mismatch_stats'].keys())
        counts = [stats['field_mismatch_stats'][field]['count'] for field in fields]

        plt.figure(figsize=(12, 6))
        plt.bar(fields, counts, color='salmon')
        plt.title(f'Field-Specific Mismatches\n{caption_base}')
        plt.xlabel('Field')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{file_prefix}_field_mismatches.png'))
        plt.close()


def process_game_failures(game_name, model_name=None):
    """Process failure analysis for a specific game and model."""
    # Create base directory for this game
    results_dir = f"results/{game_name}"
    os.makedirs(results_dir, exist_ok=True)

    # Define file paths with model name if provided
    model_suffix = f"_{model_name}" if model_name else ""
    structured_file = f"results/{game_name}_structured_failures{model_suffix}.json"
    unstructured_file = f"results/{game_name}_unstructured_failures{model_suffix}.json"

    # Create output directories
    struct_output_dir = os.path.join(results_dir, f"structured{model_suffix}")
    unstruct_output_dir = os.path.join(results_dir, f"unstructured{model_suffix}")

    # Process unstructured failures
    print(f"\nAnalyzing {game_name} unstructured failures{model_suffix}...")
    if os.path.exists(unstructured_file):
        unstruct_stats = analyze_failures(unstructured_file)
        if unstruct_stats and unstruct_stats['total_failures'] > 0:
            print(f"\nGenerating visualizations for {game_name} unstructured failures{model_suffix}...")
            generate_visualizations(unstruct_stats, unstruct_output_dir,
                                   game_name=game_name, model_name=model_name, is_structured=False)
    else:
        print(f"File not found: {unstructured_file}")

    # Process structured failures
    print(f"\nAnalyzing {game_name} structured failures{model_suffix}...")
    if os.path.exists(structured_file):
        struct_stats = analyze_failures(structured_file)
        if struct_stats and struct_stats['total_failures'] > 0:
            print(f"\nGenerating visualizations for {game_name} structured failures{model_suffix}...")
            generate_visualizations(struct_stats, struct_output_dir,
                                   game_name=game_name, model_name=model_name, is_structured=True)
    else:
        print(f"File not found: {structured_file}")

def find_failure_files():
    """Find all failure JSON files in the results directory."""
    game_model_pairs = []
    if os.path.exists("results"):
        for filename in os.listdir("results"):
            if filename.endswith("_failures.json") or "_failures_" in filename:
                # Extract game name and model name
                parts = filename.replace("_failures", "").replace(".json", "").split("_")
                if "structured" in parts or "unstructured" in parts:
                    # Format is game_[un]structured_failures_model.json or game_[un]structured_failures.json
                    game_name = parts[0]
                    model_name = parts[-1] if len(parts) > 2 else None
                    pair = (game_name, model_name)
                    if pair not in game_model_pairs:
                        game_model_pairs.append(pair)
    return game_model_pairs


if __name__ == "__main__":
    # Create main results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)

    # Find all game/model combinations in the results directory
    game_model_pairs = find_failure_files()

    if game_model_pairs:
        print(f"Found {len(game_model_pairs)} game/model combinations to analyze")
        for game_name, model_name in game_model_pairs:
            process_game_failures(game_name, model_name)
    else:
        # Fallback to processing specific games
        print("No failure files found automatically. Processing default games...")
        games = ["game1", "game2", "game3"]
        models = ["gpt-4o", "gpt-4o-mini"]

        for game in games:
            for model in models:
                process_game_failures(game, model)

    print("Analysis and visualizations complete.")