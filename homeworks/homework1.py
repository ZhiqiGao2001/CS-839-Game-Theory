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


def part1():
    prisoners_dilemma()
    print("\n----------------------\n")
    insist_accept_game()
    print("\n----------------------\n")
    hawk_dove_game()


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

if __name__ == '__main__':
    # part1()
    part2()