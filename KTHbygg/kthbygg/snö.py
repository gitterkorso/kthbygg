def μ5(α):

    if α <= 22.5:
        return 0.8 + 0.3 * α / 22.5
    elif α <= 60:
        return 1.76 - 1.1 * α / 37.5
    else:
        return 0.0


def μ2(α):

    if α <= 30:
        return 0.8
    elif α <= 60:
        return 0.8 * (60 - α) / 30
    else:
        return 0.0
    


def μ1(α):

    if α <= 30:
        return 0.8
    elif α <= 60:
        return 0.8 * (60 - α) / 30
    else:
        return 0.0



import numpy as np
import matplotlib.pyplot as plt

# μ5(α)
def μ5_num(α):
    α = np.array(α)
    res = np.zeros_like(α, dtype=float)

    # α ≤ 22.5°
    mask1 = α <= 22.5
    res[mask1] = 0.8 + 0.3 * α[mask1] / 22.5

    # 22.5° < α ≤ 60°
    mask2 = (α > 22.5) & (α <= 60)
    res[mask2] = 1.76 - 1.1 * α[mask2] / 37.5

    return res  # α ≥ 60° blir 0 automatiskt


# μ1(α)
def μ1_num(α):
    α = np.array(α)
    res = np.zeros_like(α, dtype=float)

    # α ≤ 30°
    mask1 = α <= 30
    res[mask1] = 0.8

    # 30° < α ≤ 60°
    mask2 = (α > 30) & (α <= 60)
    res[mask2] = 0.8 * (60 - α[mask2]) / 30

    return res



# --- Huvudfunktion som ritar diagrammet ---
def snö_diagram():
    # --- Plot ---
    α_vals = np.linspace(0, 80, 500)
    μ5_vals = μ5_num(α_vals)
    μ1_vals = μ1_num(α_vals)

    plt.figure(figsize=(8, 5))
    plt.plot(α_vals, μ5_vals, label="μ5(α)")
    plt.plot(α_vals, μ1_vals, label="μ1(α)")
    plt.xlabel("α (degrees)")
    plt.ylabel("μ")
    plt.grid(True)
    plt.legend()
    plt.show()

