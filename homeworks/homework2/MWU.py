import numpy as np

# Define the game payoffs.
# Player 1 strategies: A (index 0) and B (index 1)
# Player 2 strategies: C (index 0) and D (index 1)
#
# Payoffs are given in the order: (u1, u2)
# Game matrix (rows: Player1, columns: Player2):
#      C         D
# A  (1, 0)   (-2, -1)
# B  (-1,-2)   (0, 1)
#
# We will use these payoffs to compute expected payoffs for each strategy.
# For player 1:
#   - payoff for A: 1 * p2(C) + (-2) * p2(D)
#   - payoff for B: (-1) * p2(C) + (0) * p2(D)
# For player 2:
#   - payoff for C: 0 * p1(A) + (-2) * p1(B)
#   - payoff for D: (-1) * p1(A) + (1) * p1(B)

# Parameters
T = 5000           # time horizon
epsilon = 0.05     # learning rate / step size

# Initialize weight vectors (for multiplicative weights) for both players.
# We initialize with uniform weights.
w1 = np.array([1.0, 1.0])
w2 = np.array([1.0, 1.0])

# For tracking the empirical (time-average) strategy
avg_p1 = np.zeros(2)
avg_p2 = np.zeros(2)

# Function to compute the mixed strategy (softmax distribution) from weights
def get_strategy(weights):
    return weights / np.sum(weights)

# Run the multiplicative weights update algorithm
for t in range(1, T+1):
    # Compute current strategies from weights.
    p1 = get_strategy(w1)  # Distribution over A and B for Player 1
    p2 = get_strategy(w2)  # Distribution over C and D for Player 2

    # Record the strategies for averaging
    avg_p1 += p1
    avg_p2 += p2

    # Compute expected payoffs for each pure strategy for each player:
    # For Player 1:
    #   - If play A: payoff_A = 1*p2[0] + (-2)*p2[1]
    #   - If play B: payoff_B = (-1)*p2[0] + (0)*p2[1]
    u1_A = 1.0 * p2[0] + (-2.0) * p2[1]
    u1_B = (-1.0) * p2[0] + (0.0) * p2[1]
    u1 = np.array([u1_A, u1_B])

    # For Player 2:
    #   - If play C: payoff_C = 0*p1[0] + (-2)*p1[1]
    #   - If play D: payoff_D = (-1)*p1[0] + (1)*p1[1]
    u2_C = 0.0 * p1[0] + (-2.0) * p1[1]
    u2_D = (-1.0) * p1[0] + (1.0) * p1[1]
    u2 = np.array([u2_C, u2_D])

    # Update weights using multiplicative weights update rule:
    # w_i(s) <- w_i(s) * exp(epsilon * payoff(s))
    w1 = w1 * np.exp(epsilon * u1)
    w2 = w2 * np.exp(epsilon * u2)

# Compute time-average strategies over all iterations.
avg_p1 /= T
avg_p2 /= T

print("Average strategy for Player 1 over T iterations:")
print("Probability of A: {:.4f}, B: {:.4f}".format(avg_p1[0], avg_p1[1]))
print("Average strategy for Player 2 over T iterations:")
print("Probability of C: {:.4f}, D: {:.4f}".format(avg_p2[0], avg_p2[1]))

# The empirical joint distribution over outcomes is the product of the average strategies
joint_distribution = np.outer(avg_p1, avg_p2)
print("\nEmpirical joint distribution (row: Player1, column: Player2):")
print("        C         D")
print("A:   {:.4f}   {:.4f}".format(joint_distribution[0,0], joint_distribution[0,1]))
print("B:   {:.4f}   {:.4f}".format(joint_distribution[1,0], joint_distribution[1,1]))

# For this game, you are likely to see that the average strategies concentrate on one pure equilibrium.
# For instance, you might see p1 ~ [0,1] and p2 ~ [0,1] which corresponds to the pure outcome (B,D),
# or p1 ~ [1,0] and p2 ~ [1,0] corresponding to (A,C).