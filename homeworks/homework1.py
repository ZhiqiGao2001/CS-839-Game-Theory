import nashpy as nash
import numpy as np
import matplotlib.pyplot as plt


def prisoners_dilemma():
    # 囚徒困境博弈：
    # 策略：deny, confess
    # 支付矩阵（行玩家）：
    #      deny   confess
    # deny   -2     -3
    # confess 0      -3
    # 支付矩阵（列玩家）：
    #      deny   confess
    # deny   -2      0
    # confess -3     -3
    A = np.array([[-2, -3], [0, -3]])
    B = np.array([[-2, 0], [-3, -3]])
    game = nash.Game(A, B)
    print("囚徒困境的纳什均衡：")
    for eq in game.support_enumeration():
        print(eq)


def insist_accept_game():
    # 坚持-接受博弈：
    # 策略：insist, accept
    # 行玩家支付矩阵：
    #         insist   accept
    # insist     0       10
    # accept     1        0
    # 列玩家支付矩阵：
    #         insist   accept
    # insist     0        1
    # accept    10        0
    A = np.array([[0, 10], [1, 0]])
    B = np.array([[0, 1], [10, 0]])
    game = nash.Game(A, B)
    print("坚持-接受博弈的纳什均衡：")
    for eq in game.support_enumeration():
        print(eq)


def hawk_dove_game():
    # 鹰鸽博弈：
    # 策略：dove, hawk（这里我们把第一行设为 dove，第二行设为 hawk）
    # 支付矩阵（行玩家）：
    #           hawk   dove
    # dove       0      2
    # hawk      -2      4
    # 注意：这里对应的支付值为：
    # 当行玩家选择 dove 且列玩家选择 hawk时，行玩家获得 0，列玩家获得 4；
    # 当行玩家选择 dove 且列玩家选择 dove时，双方各获得 2；
    # 当行玩家选择 hawk 且列玩家选择 hawk时，双方各获得 -2；
    # 当行玩家选择 hawk 且列玩家选择 dove时，行玩家获得 4，列玩家获得 0。
    A = np.array([[0, 2], [-2, 4]])
    B = np.array([[4, 2], [-2, 0]])
    game = nash.Game(A, B)
    print("鹰鸽博弈的纳什均衡：")
    for eq in game.support_enumeration():
        print(eq)


def penalty_shot_game():
    A = np.array([[-1, 1], [1, -1]])
    B = np.array([[1, -1], [-1, 1]])
    game = nash.Game(A, B)
    for eq in game.support_enumeration():
        print(eq)


def part1():
    prisoners_dilemma()
    print("\n----------------------\n")
    insist_accept_game()
    print("\n----------------------\n")
    hawk_dove_game()
    print("\n----------------------\n")
    penalty_shot_game()


def part2():
    # Create three subplots for the three games
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # -------------------------------
    # Game 1: Prisoner's Dilemma
    # Here, the coordinates (x, y) represent the probability that the column and row players choose "confess"
    # Pure strategy Nash equilibria: (confess, confess) -> (1, 1),
    #                                (deny, confess) -> (0, 1),
    #                                (confess, deny) -> (1, 0)
    ax = axes[0]
    ax.set_title("Prisoner's Dilemma")
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel("Probability of confess for column player")
    ax.set_ylabel("Probability of confess for row player")
    ax.grid(True)

    # Mark pure strategy equilibrium points
    pd_ne_points = [(1, 1), (0, 1), (1, 0)]
    for i, point in enumerate(pd_ne_points):
        ax.plot(point[0], point[1], 'ro', markersize=10,
                label="Pure strategy equilibrium" if i == 0 else "")

    ax.legend()

    # -------------------------------
    # Game 2: Insist-Accept Game
    # Here, assume the coordinates represent the probability that a player chooses "insist".
    # Then the pure strategy equilibria are: (insist, accept) -> (1, 0) and (accept, insist) -> (0, 1).
    # The mixed equilibrium is: (10/11, 10/11).
    ax = axes[1]
    ax.set_title("Insist-Accept Game")
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel("Probability of insist for column player")
    ax.set_ylabel("Probability of insist for row player")
    ax.grid(True)

    # Mark pure strategy equilibrium points
    ia_pure_points = [(1, 0), (0, 1)]
    for i, point in enumerate(ia_pure_points):
        ax.plot(point[0], point[1], 'ro', markersize=10,
                label="Pure strategy equilibrium" if i == 0 else "")

    # Mark the mixed equilibrium point
    ia_mixed_point = (10 / 11, 10 / 11)
    ax.plot(ia_mixed_point[0], ia_mixed_point[1], 'bs', markersize=10, label="Mixed equilibrium")
    ax.legend()

    # -------------------------------
    # Game 3: Hawk-Dove Game
    # Here, assume the coordinates represent the probability that a player chooses "hawk".
    # Then the pure strategy equilibria are: (hawk, dove) -> (1, 0) and (dove, hawk) -> (0, 1).
    # The mixed equilibrium is: (0.5, 0.5).
    ax = axes[2]
    ax.set_title("Hawk-Dove Game")
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.set_xlabel("Probability of hawk for column player")
    ax.set_ylabel("Probability of hawk for row player")
    ax.grid(True)

    # Mark pure strategy equilibrium points
    hd_pure_points = [(1, 0), (0, 1)]
    for i, point in enumerate(hd_pure_points):
        ax.plot(point[0], point[1], 'ro', markersize=10,
                label="Pure strategy equilibrium" if i == 0 else "")

    # Mark the mixed equilibrium point
    hd_mixed_point = (0.5, 0.5)
    ax.plot(hd_mixed_point[0], hd_mixed_point[1], 'bs', markersize=10, label="Mixed equilibrium")
    ax.legend()

    plt.tight_layout()
    plt.savefig("part2.png")
    plt.show()


def part3_4():
    # Parameter for the logit best response functions
    beta = 5.0

    # Define logit best response functions for each game.
    # They return the probability of choosing the designated strategy.
    # For a given opponent probability 'p', the logit best response is:
    # BR(p) = exp(beta * U1) / (exp(beta * U1) + exp(beta * U2))
    #
    # Game 1: Prisoner's Dilemma
    #   For Blue (or column player), let strategy 1 = "confess" and strategy 2 = "deny".
    #   Expected payoffs:
    #       U(confess) = -3 * (opponent's probability of confess)
    #       U(deny)    = (1 - opponent's probability)*(-2) + (opponent's probability)*(-3) = -2 - opponent's probability
    def br_pd(opponent_prob, beta=beta):
        u_confess = -3 * opponent_prob
        u_deny = -2 - opponent_prob
        exp_confess = np.exp(beta * u_confess)
        exp_deny = np.exp(beta * u_deny)
        return exp_confess / (exp_confess + exp_deny)

    # Game 2: Insist-Accept Game
    #   For Blue, let strategy 1 = "insist" and strategy 2 = "accept".
    #   Expected payoffs:
    #       U(insist) = 10*(1 - opponent_prob)
    #       U(accept) = opponent_prob
    def br_ia(opponent_prob, beta=beta):
        u_insist = 10 * (1 - opponent_prob)
        u_accept = opponent_prob
        exp_insist = np.exp(beta * u_insist)
        exp_accept = np.exp(beta * u_accept)
        return exp_insist / (exp_insist + exp_accept)

    # Game 3: Hawk-Dove Game
    #   For Blue, let strategy 1 = "hawk" and strategy 2 = "dove".
    #   Expected payoffs:
    #       U(hawk) = 4 - 6*opponent_prob
    #       U(dove) = 2 - 2*opponent_prob
    def br_hd(opponent_prob, beta=beta):
        u_hawk = 4 - 6 * opponent_prob
        u_dove = 2 - 2 * opponent_prob
        exp_hawk = np.exp(beta * u_hawk)
        exp_dove = np.exp(beta * u_dove)
        return exp_hawk / (exp_hawk + exp_dove)

    # # Create a grid over [0,1] x [0,1] for plotting the displacement field.
    # grid_points = 20
    # x_vals = np.linspace(0, 1, grid_points)
    # y_vals = np.linspace(0, 1, grid_points)
    # X, Y = np.meshgrid(x_vals, y_vals)
    #
    # # Prepare subplots for the three games
    # fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    #
    # # List the games along with their corresponding best response function and title.
    # games = [
    #     ("Prisoner's Dilemma", br_pd),
    #     ("Insist-Accept Game", br_ia),
    #     ("Hawk-Dove Game", br_hd)
    # ]
    #
    # # Loop over each game to plot its displacement field.
    # for ax, (title, br_func) in zip(axes, games):
    #     # The displacement field is defined as:
    #     # g(x, y) = (BR(y) - x, BR(x) - y)
    #     U_field = br_func(Y) - X  # x-component: improvement for the column player
    #     V_field = br_func(X) - Y  # y-component: improvement for the row player
    #
    #     # Plot the vector field using a quiver plot.
    #     ax.quiver(X, Y, U_field, V_field, color='blue')
    #     ax.set_title(title)
    #     ax.set_xlim(0, 1)
    #     ax.set_ylim(0, 1)
    #     ax.set_xlabel("Column player's probability")
    #     ax.set_ylabel("Row player's probability")
    #     ax.grid(True)
    #
    #     # To check fixed points, we search for a symmetric fixed point on the line x = y,
    #     # i.e. a solution to x = BR(x). Here we approximate it over a fine grid.
    #     x_grid = np.linspace(0, 1, 1000)
    #     diff = np.abs(x_grid - br_func(x_grid))
    #     idx = np.argmin(diff)
    #     fixed_point = x_grid[idx]
    #     # Mark the fixed point as a black dot.
    #     ax.plot(fixed_point, fixed_point, 'ko', markersize=8, label="Fixed Point")
    #     ax.legend()
    #
    # plt.tight_layout()
    # plt.savefig("part3.png")
    # plt.show()

    # -------------------------------
    # Create a grid over [0,1] x [0,1] for plotting
    grid_points = 20
    x_vals = np.linspace(0, 1, grid_points)
    y_vals = np.linspace(0, 1, grid_points)
    X, Y = np.meshgrid(x_vals, y_vals)

    # List the games with their best response functions
    games = [
        ("Prisoner's Dilemma", br_pd),
        ("Insist-Accept Game", br_ia),
        ("Hawk-Dove Game", br_hd)
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for ax, (title, br_func) in zip(axes, games):
        # Displacement field g(x, y) = (BR(y) - x, BR(x) - y)
        U_field = br_func(Y) - X  # Column player's improvement
        V_field = br_func(X) - Y  # Row player's improvement

        # Magnitude of the displacement
        magnitude = np.sqrt(U_field ** 2 + V_field ** 2)

        # Plot the vector field with color-coded magnitudes
        # 'magnitude' is passed as the color array (C)
        q = ax.quiver(X, Y, U_field, V_field, magnitude, cmap='viridis')

        # Add a colorbar showing the magnitude scale
        cbar = fig.colorbar(q, ax=ax)
        cbar.set_label("Displacement magnitude")

        # Optional: identify a symmetric fixed point on x=y
        # (Approximating x = BR(x))
        x_grid = np.linspace(0, 1, 500)
        diff = np.abs(x_grid - br_func(x_grid))
        idx = np.argmin(diff)
        fp = x_grid[idx]
        # Mark this approximate fixed point
        ax.plot(fp, fp, 'ko', markersize=8, label="Approx. fixed point")

        ax.set_title(title)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("Column player's probability")
        ax.set_ylabel("Row player's probability")
        ax.legend()
        ax.grid(True)

    plt.tight_layout()
    plt.savefig("part4.png")
    plt.show()


def part5():
    beta = 5.0  # Logit sensitivity parameter

    def br_insist_accept(p_insist, beta=beta):
        """
        Logit best response for the Insist–Accept game.
        Returns the probability of choosing 'insist' given the opponent's probability of insisting.

        Payoffs:
          U(insist) = 10 * (1 - opponent's probability of insist)
          U(accept) = opponent's probability of insist
        """
        u_insist = 10 * (1 - p_insist)
        u_accept = p_insist
        e_insist = np.exp(beta * u_insist)
        e_accept = np.exp(beta * u_accept)
        return e_insist / (e_insist + e_accept)

    def coordinate_transform(x, y, x_label, y_label):
        """
        Convert (x, y) in the chosen labeling to the internal "insist" probabilities.
        If the axis is labeled 'insist', then the coordinate is used directly.
        If the axis is labeled 'accept', then the internal probability is 1 - coordinate.
        """
        p_insist_col = x if x_label == 'insist' else (1 - x)
        p_insist_row = y if y_label == 'insist' else (1 - y)
        return p_insist_col, p_insist_row

    def inverse_coordinate_transform(p_insist_col, p_insist_row, x_label, y_label):
        """
        Convert from internal "insist" probabilities to the chosen labeling (x, y).
        """
        x_new = p_insist_col if x_label == 'insist' else 1 - p_insist_col
        y_new = p_insist_row if y_label == 'insist' else 1 - p_insist_row
        return x_new, y_new

    def displacement(x, y, x_label, y_label, br_func):
        """
        Given a point (x, y) in the chosen labeling, compute the displacement vector:
          g(x, y) = (next_x - x, next_y - y)
        where next_x and next_y are obtained via the best-response dynamic and then
        transformed back to the chosen coordinate system.
        """
        # Convert (x, y) to internal "insist" probabilities.
        p_insist_col, p_insist_row = coordinate_transform(x, y, x_label, y_label)

        # Compute best responses (next probabilities of 'insist').
        next_col_insist = br_func(p_insist_row)  # Column player's best response.
        next_row_insist = br_func(p_insist_col)  # Row player's best response.

        # Convert back to the chosen labeling.
        next_x, next_y = inverse_coordinate_transform(next_col_insist, next_row_insist, x_label, y_label)

        return next_x - x, next_y - y

    # Compute the symmetric fixed point in internal "insist" space.
    # This approximates the solution to x = br_insist_accept(x)
    x_grid = np.linspace(0, 1, 500)
    diff = np.abs(x_grid - br_insist_accept(x_grid))
    idx = np.argmin(diff)
    fp_insist = x_grid[idx]  # Fixed point in terms of the probability of insisting

    # For a given labeling, the fixed point coordinates are:
    #   If label == 'insist' => coordinate = fp_insist
    #   If label == 'accept' => coordinate = 1 - fp_insist
    def get_fixed_point_coordinates(x_label, y_label, fp_insist):
        fixed_x = fp_insist if x_label == 'insist' else 1 - fp_insist
        fixed_y = fp_insist if y_label == 'insist' else 1 - fp_insist
        return fixed_x, fixed_y

    # Define labelings for the three subplots:
    # 1. x = accept, y = accept
    # 2. x = accept, y = insist
    # 3. x = insist, y = accept
    labelings = [
        ('accept', 'accept'),
        ('accept', 'insist'),
        ('insist', 'accept'),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    grid_points = 20
    x_vals = np.linspace(0, 1, grid_points)
    y_vals = np.linspace(0, 1, grid_points)
    X, Y = np.meshgrid(x_vals, y_vals)

    for ax, (xlbl, ylbl) in zip(axes, labelings):
        # Prepare arrays for the displacement field.
        U = np.zeros_like(X)
        V = np.zeros_like(Y)

        # Compute displacement for each grid point.
        for i in range(grid_points):
            for j in range(grid_points):
                x_ij = X[i, j]
                y_ij = Y[i, j]
                dx, dy = displacement(x_ij, y_ij, xlbl, ylbl, br_insist_accept)
                U[i, j] = dx
                V[i, j] = dy

        # Compute the magnitude of the displacement.
        magnitude = np.sqrt(U ** 2 + V ** 2)

        # Plot the vector field with arrows color-coded by displacement magnitude.
        q = ax.quiver(X, Y, U, V, magnitude, cmap='viridis')

        # Determine and mark the fixed point.
        fixed_x, fixed_y = get_fixed_point_coordinates(xlbl, ylbl, fp_insist)
        print(f"Fixed point for labeling ({xlbl}, {ylbl}): ({fixed_x:.3f}, {fixed_y:.3f})")
        ax.plot(fixed_x, fixed_y, 'ko', markersize=8, label="Approx. fixed point")

        # Set plot titles and labels.
        ax.set_title(f"x = {xlbl}, y = {ylbl}")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel(f"Probability of {xlbl}")
        ax.set_ylabel(f"Probability of {ylbl}")
        ax.grid(True)
        ax.legend()

        # Add a colorbar for the displacement magnitude.
        cbar = fig.colorbar(q, ax=ax)
        cbar.set_label("Displacement magnitude")

    plt.tight_layout()
    plt.savefig("part5.png")
    plt.show()


if __name__ == '__main__':
    part1()
    part2()
    part3_4()
    part5()
