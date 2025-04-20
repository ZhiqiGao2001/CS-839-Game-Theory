import json
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt


def analyze_failures(failure_file):
    """Analyze failures from a game test JSON file."""
    # Load the failure data
    with open(failure_file, 'r', encoding='utf-8') as f:
        failures = json.load(f)

    if not failures:
        print(f"No failures found in {failure_file}")
        return

    # Create a DataFrame for easier analysis
    df = pd.DataFrame(failures)

    # Add a column for response format type
    df['resp_format'] = df['got'].apply(lambda x: 'dict' if x.startswith('{') or x.startswith('```')
    else 'template' if x.startswith('ACTION_TEMPLATE')
    else 'other')

    # Basic statistics
    total_failures = len(failures)
    failure_by_type = df['message_type'].value_counts()
    failure_by_format = df['resp_format'].value_counts()

    print(f"Total failures: {total_failures}")
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

    # Format as percentages with % sign
    stats_df['Percentage'] = stats_df['Percentage'].apply(lambda x: f"{x}%")
    stats_df['Cumulative_Percentage'] = stats_df['Cumulative_Percentage'].apply(lambda x: f"{x}%")

    print("\nFailure Statistics:")
    print(stats_df)

    # Response format statistics
    format_stats = pd.DataFrame({
        'Count': failure_by_format,
        'Percentage': (failure_by_format / total_failures * 100).round(2)
    })
    format_stats['Percentage'] = format_stats['Percentage'].apply(lambda x: f"{x}%")

    print("\nResponse Format Statistics:")
    print(format_stats)

    # Analyze specific failure modes
    action_mismatches = []
    for _, row in df.iterrows():
        expected = row['expected']
        got_str = row['got']

        try:
            # Extract the action from the response
            if row['resp_format'] == 'template':
                # Extract dictionary from template string
                dict_str = got_str.replace('ACTION_TEMPLATE = ', '')
                got = eval(dict_str)
            elif row['resp_format'] == 'dict':
                if got_str.startswith('```'):
                    # Remove markdown code block formatting
                    lines = got_str.strip().split('\n')
                    if lines[0].startswith('```'):
                        lines = lines[1:]
                    if lines[-1].startswith('```'):
                        lines = lines[:-1]
                    got_str = '\n'.join(lines)
                try:
                    got = json.loads(got_str)
                except:
                    got = eval(got_str)
            else:
                got = {'ACTION': 'unknown'}

            # Record action mismatches
            if got['ACTION'] != expected['ACTION']:
                action_mismatches.append({
                    'message_type': row['message_type'],
                    'message': row['incoming'],
                    'expected_action': expected['ACTION'],
                    'got_action': got['ACTION']
                })
        except Exception as e:
            print(f"Error parsing response: {e}")
            continue

    # Analyze action mismatches
    if action_mismatches:
        am_df = pd.DataFrame(action_mismatches)
        mismatch_counts = am_df.groupby(['expected_action', 'got_action']).size()
        print("\nAction mismatches:")
        print(mismatch_counts)

        # Create a cross-tabulation of expected vs. actual actions
        confusion_matrix = pd.crosstab(
            am_df['expected_action'],
            am_df['got_action'],
            margins=True,
            margins_name='Total'
        )

        print("\nConfusion Matrix (Expected vs. Actual Actions):")
        print(confusion_matrix)

        # Calculate percentages within each expected action
        percentage_matrix = pd.crosstab(
            am_df['expected_action'],
            am_df['got_action'],
            normalize='index'
        ).round(2) * 100

        print("\nPercentage Matrix (% of times each expected action was classified as something else):")
        print(percentage_matrix)

        # Look for patterns in messages for each type of mismatch
        print("\nCommon message patterns for each mismatch type:")
        for (expected, got), group in am_df.groupby(['expected_action', 'got_action']):
            print(f"\nExpected {expected}, Got {got} ({len(group)} instances):")
            for msg in group['message'][:5]:  # Show first 5 examples
                print(f"  - '{msg}'")

    # Analyze REPEAT failures specifically (model should classify as REPEAT but doesn't)
    repeat_failures = am_df[am_df['expected_action'] == 'REPEAT'] if len(action_mismatches) > 0 else pd.DataFrame()
    if not repeat_failures.empty:
        print("\nAnalysis of messages that should be REPEAT but aren't:")

        # Calculate statistics for REPEAT errors
        repeat_error_stats = repeat_failures.groupby('got_action').size().reset_index()
        repeat_error_stats.columns = ['Misclassified_As', 'Count']
        repeat_error_stats['Percentage'] = (repeat_error_stats['Count'] / len(repeat_failures) * 100).round(2)
        repeat_error_stats['Percentage'] = repeat_error_stats['Percentage'].apply(lambda x: f"{x}%")

        print("\nREPEAT Error Statistics:")
        print(repeat_error_stats)

        for action, group in repeat_failures.groupby('got_action'):
            keywords = []
            for msg in group['message']:
                words = msg.lower().split()
                keywords.extend(words)
            common_words = Counter(keywords).most_common(10)
            print(f"\nIncorrectly classified as {action}:")
            print(f"  Common words: {common_words}")
            print(f"  Example messages:")
            for msg in group['message'][:3]:
                print(f"    - '{msg}'")

    return {
        'total_failures': total_failures,
        'failure_stats': stats_df,
        'format_stats': format_stats,
        'confusion_matrix': confusion_matrix if action_mismatches else None,
        'percentage_matrix': percentage_matrix if action_mismatches else None,
        'repeat_error_stats': repeat_error_stats if not repeat_failures.empty else None
    }


def generate_visualizations(stats, prefix):
    """Generate visualizations from the failure statistics."""
    if not stats:
        return

    # Failure type pie chart
    failure_counts = stats['failure_stats']['Count']
    plt.figure(figsize=(10, 6))
    plt.pie(failure_counts, labels=failure_counts.index, autopct='%1.1f%%')
    plt.title('Failures by Message Type')
    plt.savefig(f'results/{prefix}failure_types_pie.png')
    plt.close()

    # Response format bar chart
    format_counts = stats['format_stats']['Count']
    plt.figure(figsize=(10, 6))
    format_counts.plot(kind='bar', color='skyblue')
    plt.title('Failures by Response Format')
    plt.xlabel('Format Type')
    plt.ylabel('Count')
    plt.savefig(f'results/{prefix}format_failures_bar.png')
    plt.close()

    # Confusion matrix heatmap
    if stats['confusion_matrix'] is not None:
        conf_matrix = stats['confusion_matrix'].iloc[:-1, :-1]  # Remove totals
        plt.figure(figsize=(10, 8))
        plt.imshow(conf_matrix, cmap='Blues')
        plt.colorbar(label='Count')
        plt.xticks(range(len(conf_matrix.columns)), conf_matrix.columns, rotation=45)
        plt.yticks(range(len(conf_matrix.index)), conf_matrix.index)
        plt.xlabel('Predicted Action')
        plt.ylabel('Expected Action')
        plt.title('results/Action Confusion Matrix')

        # Add text annotations
        for i in range(len(conf_matrix.index)):
            for j in range(len(conf_matrix.columns)):
                plt.text(j, i, conf_matrix.iloc[i, j],
                         ha="center", va="center", color="white" if conf_matrix.iloc[i, j] > 3 else "black")

        plt.tight_layout()
        plt.savefig(f'results/{prefix}confusion_matrix.png')
        plt.close()


if __name__ == "__main__":
    game_1_structured, game_1_unstructured = "results/game1_structured_failures.json", "results/game1_unstructured_failures.json"
    game_1_prefix_structured = "game1_structured_"
    game_1_prefix_unstructured = "game1_unstructured_"
    print("Analyzing unstructured failures...")
    unstruct_stats = analyze_failures(game_1_unstructured)

    print("\nAnalyzing structured failures...")
    struct_stats = analyze_failures(game_1_structured)

    # Generate visualizations
    if unstruct_stats and unstruct_stats['total_failures'] > 0:
        print("\nGenerating visualizations for unstructured failures...")
        generate_visualizations(unstruct_stats, game_1_prefix_unstructured)
        generate_visualizations(struct_stats, game_1_prefix_structured)


    game_2_structured, game_2_unstructured = "results/game2_structured_failures.json", "results/game2_unstructured_failures.json"
    game_2_prefix_structured = "game2_structured_"
    game_2_prefix_unstructured = "game2_unstructured_"
    print("Analyzing unstructured failures...")
    unstruct_stats = analyze_failures(game_2_unstructured)
    print("\nAnalyzing structured failures...")
    struct_stats = analyze_failures(game_2_structured)
    # Generate visualizations
    if unstruct_stats and unstruct_stats['total_failures'] > 0:
        print("\nGenerating visualizations for unstructured failures...")
        generate_visualizations(unstruct_stats, game_2_prefix_unstructured)
        generate_visualizations(struct_stats, game_2_prefix_structured)
    print("Analysis and visualizations complete.")
