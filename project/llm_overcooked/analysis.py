import os
import numpy as np
import json
import matplotlib.pyplot as plt
import re
import pandas as pd
import seaborn as sns
import textwrap

from collections import Counter
from overcooked import World

result_files = [
    'result_level_0_2_gpt-4o_struct.json',
    'result_level_0_2_gpt-4o_nl.json',
    'result_level_3_3_gpt-4o_struct.json',
    'result_level_3_3_gpt-4o_nl.json',
]
alphas = [1.0, 1.5, 2.0, 2.5, 3.0]

def draw(prefix, files):
    valid_count_list, noop_count_list = [], []
    for file in files:
        with open(file, 'r') as f:
            table = json.load(f)

        alphas = list(table.keys())
        alphas.sort(key=lambda x: float(x))

        valid_count, noop_count = [], []
        for alpha in alphas:
            valid = 0
            noop = 0
            tot = 0
            for action_history, action_success_history in zip(table[alpha]['action_history'], table[alpha]['action_success_history']):
                for actions, successes in zip(action_history, action_success_history):
                    for action, success in zip(actions, successes):
                        if success == True:
                            valid += 1
                            if action.startswith("noop"):
                                noop += 1
                        tot += 1
            valid_count.append(valid)
            noop_count.append(noop)
        
        valid_count_list.append(valid_count)
        noop_count_list.append(noop_count) 
    
    print(f"Valid count for {prefix}:", valid_count_list)
    print(f"Noop count for {prefix}:", noop_count_list)

    x = np.arange(len(alphas))
    width = 0.35

    valid_minus_noop1 = [v - n for v, n in zip(valid_count_list[0], noop_count_list[0])]
    valid_minus_noop2 = [v - n for v, n in zip(valid_count_list[1], noop_count_list[1])]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, noop_count_list[0], width, label='noop (Structured)', color="#AED6F1")
    ax.bar(x - width/2, valid_minus_noop1, width, bottom=noop_count_list[0], label='valid (Structured)', color="#5DADE2")

    ax.bar(x + width/2, noop_count_list[1], width, label='noop (NL)', color="#F9E79F")
    ax.bar(x + width/2, valid_minus_noop2, width, bottom=noop_count_list[1], label='valid (NL)', color="#F4D03F")

    ax.set_xlabel('Alpha')
    ax.set_ylabel('Count')
    ax.set_title('Statistics of valid actions for: ' + prefix)
    ax.set_xticks(x)
    ax.set_xticklabels([f'{a}' for a in alphas])
    ax.legend()

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('figs/' + prefix + '_valid-noop-count.png', dpi=300)

def replay(level, num_agents, files):
    output = ""
    for file in files:
        with open(file, 'r') as f:
            table = json.load(f)

        alphas = list(table.keys())
        alphas.sort(key=lambda x: float(x))

        for alpha in alphas:
            env = World(recipe_filename='./assets/recipe.json', task_filename='./assets/tasks_level_final.json',
                         level=level, use_task_lifetime_interval_oracle=True,
                         alpha=float(alpha), beta=2.5, num_agents=num_agents, override_agent=True)
            max_episode = 3
            max_steps = env.max_steps

            feedback_histories_list = []
            feedback_categories = {}
            for eps_id in range(max_episode):
                obs = env.reset()

                step = 0
                feedback_histories = []

                while (step < max_steps):
                    plan = table[alpha]['action_history'][eps_id][step]

                    if plan:
                        obs, done, info = env.step(plan)
                    feedback_histories.append(env.feedback)
                    if env.feedback:
                        for feedback in env.feedback:
                            if feedback not in feedback_categories:
                                feedback_categories[feedback] = 0
                            feedback_categories[feedback] += 1

                    step += 1
                
                feedback_histories_list.append(feedback_histories)

            output += f"Feedback categories for {file} with alpha {alpha}:\n"
            for feedback, count in feedback_categories.items():
                output +=  f"{feedback}: {count}\n"
            output += "-" * 50 + '\n'
    return output

def normalize_pattern(sentence):
    sentence = re.sub(r'agent\d+', 'agent', sentence)
    sentence = re.sub(r'blender\d+|storage\d+|servingtable\d+|pot\d+|mixer\d+|chopboard\d+|pan\d+|fryer\d+|steamer\d+|oven\d+', 'tool', sentence)
    sentence = re.sub(r'salmonMeatcake|salmonSashimi|tunaSashimi|cookedRice|salmon|flour|rice|tuna', 'item', sentence)
    return sentence.strip()

def parse_failure_data(file_path):
    data = []
    alpha, config = None, None

    pattern_set = set()
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            header_match = re.match(r"Feedback categories for (.+?) with alpha ([\d.]+):", line)
            if header_match:
                config, alpha = header_match.groups()
                config = 'Structured' if 'struct' in config else 'NL'
                alpha = float(alpha)
            elif line == '--------------------------------------------------' or not line:
                continue
            else:
                normalized_cat = normalize_pattern(line.split(':')[0]).strip()
                if normalized_cat:
                    normalized_cat = normalized_cat[0].upper() + normalized_cat[1:]
                pattern_set.add(normalized_cat)
                match = re.match(r"(.+): (\d+)", line)
                if match:
                    category, count = match.groups()
                    data.append((config, normalized_cat.strip(), int(count)))

    return pd.DataFrame(data, columns=["Config", "Category", "Count"])

def aggregate_and_plot(df, top_n=20):
    grouped = df.groupby(['Config', 'Category'])['Count'].sum().reset_index()
    
    # Get top N categories overall
    top_categories = grouped.groupby('Category')['Count'].sum().nlargest(top_n).index
    grouped = grouped[grouped['Category'].isin(top_categories)]

    # Pivot for barplot
    pivot_df = grouped.pivot(index='Category', columns='Config', values='Count').fillna(0)

    df_melted = pivot_df.reset_index().melt(id_vars='Category', var_name='Config', value_name='Count')
    df_melted['Category'] = df_melted['Category'].apply(lambda x: '\n'.join(textwrap.wrap(x, width=50)))

    sns.set_theme(style="whitegrid", context="talk")
    plt.figure(figsize=(16, 10))

    # Reorder categories by total count
    category_order = df_melted.groupby('Category')['Count'].sum().sort_values(ascending=False).index

    # Use a color palette that is both vibrant and accessible
    palette = sns.color_palette("Set2", n_colors=df_melted['Config'].nunique())

    # Draw the barplot
    barplot = sns.barplot(
        data=df_melted,
        y='Category',
        x='Count',
        hue='Config',
        order=category_order,
        palette=palette,
        edgecolor='black'
    )

    # Add count labels on the bars
    for container in barplot.containers:
        barplot.bar_label(container, fmt='%d', label_type='edge', fontsize=10, padding=3)

    # Titles and labels
    plt.title('Comparison of NL vs Structured for Each Failure Reason', fontsize=22, weight='bold')
    plt.xlabel('Total Feedback Count', fontsize=16)
    plt.ylabel('Failure Reason Category', fontsize=16)

    # Customize ticks
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=16)

    # Move legend outside plot if many categories
    plt.legend(title='Config Type', title_fontsize=14, fontsize=12, loc='lower right')

    # Clean layout
    plt.tight_layout()
    plt.savefig('figs/feedbacks_aggregated.png', dpi=300, bbox_inches='tight')

def draw_feedback():
    file_path = 'feedbacks.txt'
    df_failures = parse_failure_data(file_path)
    aggregate_and_plot(df_failures)

if __name__ == "__main__":
    level_0 = [result_files[0], result_files[1]]
    level_3 = [result_files[2], result_files[3]]

    # draw('level_0', level_0)
    # draw('level_3', level_3)

    if not os.path.exists("feedbacks.txt"):
        output = replay(level='level_0', num_agents=2, files=level_0)
        output += replay(level='level_3', num_agents=3, files=level_3)
        with open('feedbacks.txt', 'w') as f:
            f.write(output)
    draw_feedback()