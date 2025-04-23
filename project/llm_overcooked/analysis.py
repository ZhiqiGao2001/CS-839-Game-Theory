import numpy as np
import json
import matplotlib.pyplot as plt

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


if __name__ == "__main__":
    level_0 = [result_files[0], result_files[1]]
    level_3 = [result_files[2], result_files[3]]

    draw('level_0', level_0)
    draw('level_3', level_3)