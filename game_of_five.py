import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from rsome import ro
from rsome import lpg_solver as grb  

def solve_grid_model():
    model = ro.Model('5x5_Grid_Model')

    # 定义决策变量
    x = model.dvar((5, 5), vtype='B')  # 0-1 变量
    y = model.dvar((5, 5), vtype='I')  # 非负整数变量

    # y 的非负约束
    model.st(y >= 0)

    # ==========================================
    # 这里是你指定的核心代码，原封不动保留
    # ==========================================
    direct = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    for i in range(5):
        for j in range(5):
            neighbor_sum = 0
            for d in direct:
                ni, nj = i + d[0], j + d[1]
                if 0 <= ni < 5 and 0 <= nj < 5:
                    neighbor_sum += x[ni, nj]
            model.st(neighbor_sum == 2 * y[i, j] + 1)z
    # ==========================================

    # 目标函数：最小化 sum(x_ij)
    model.min(x.sum())

    # 求解
    print("正在求解...")
    model.solve(grb)

    # 增加安全判断：如果有解才提取，无解则返回 None
    if model.solution.status == 'Optimal':
        x_result = x.get()
        y_result = y.get()
        print(f"求解成功！最优目标函数值: {model.get()}")
        return x_result, y_result
    else:
        print("\n⚠️ 求解失败：模型无解 (Infeasible)！")
        print("原因：在 5x5 的网格中，只要求四周邻居之和为奇数，无法满足所有格子的奇偶性要求。")
        return None, None


def animate_solution(x_grid, y_grid):
    if x_grid is None:
        return

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title("Grid Solution Animation (x_ij)", fontsize=15)

    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 5, 1), minor=True)
    ax.grid(which="minor", color="gray", linestyle='-', linewidth=2)
    ax.tick_params(which="minor", size=0)

    cmap = plt.cm.colors.ListedColormap(['white', '#1f77b4'])
    im = ax.imshow(np.zeros((5, 5)), cmap=cmap, vmin=0, vmax=1)

    texts_x = [[ax.text(j, i, "", ha="center", va="center", color="black", fontsize=14) for j in range(5)] for i in range(5)]
    texts_y = [[ax.text(j, i + 0.25, "", ha="center", va="center", color="red", fontsize=10) for j in range(5)] for i in range(5)]

    def update(frame):
        row = frame // 5
        col = frame % 5
        if frame < 25:
            current_grid = np.copy(im.get_array())
            current_grid[row, col] = x_grid[row, col]
            im.set_array(current_grid)
            texts_x[row][col].set_text(f"x:{int(x_grid[row, col])}")
            texts_y[row][col].set_text(f"y:{int(y_grid[row, col])}")
        return [im] + [texts_x[i][j] for i in range(5) for j in range(5)] + [texts_y[i][j] for i in range(5) for j in range(5)]

    ani = animation.FuncAnimation(fig, update, frames=26, interval=150, blit=True, repeat=False)
    plt.show()


if __name__ == "__main__":
    print("开始求解模型...")
    x_res, y_res = solve_grid_model()
    print("启动动画验证...")
    animate_solution(x_res, y_res)
