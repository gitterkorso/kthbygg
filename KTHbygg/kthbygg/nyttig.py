
import numpy as np

def α_A(A, ψ_0, A_0, byggnad_typ="bostäder"):
    A = np.array(A)
    α = (5/7) * ψ_0 + A_0 / A
    return np.minimum(α, 1.0) 

