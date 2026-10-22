import math

#Eulers knäckningsfall

def Euler_Ncr(L, E, I, fall, visa=True):

    # Steg 1: Bestäm knäcklängdskoefficienten (k)
    if fall == 1:
        # Ledat-Ledat: k = 1.0
        k = 1.0
    elif fall == 2:
        # Fast-Fri: k = 2.0
        k = 2.0
    elif fall == 3:
        # Fast-Ledat: k = 0.7
        k = 0.7
    elif fall == 4:
        # Fast-Fast: k = 0.5
        k = 0.5
    else:
        raise ValueError(f"Fel: Ange knäckningsfall mellan 1-4. (Du angav {fall})")
    
    L_cr = k * L
    
    N_cr = (math.pi**2 * E * I) / (L_cr**2)
    
    N_cr_kN = N_cr / 1000

    return N_cr

# Exempel användning
# N_cr = Euler_Ncr(L=5000, E=210000, I=4970000, fall=1)


def λ_y(fyd, A, N_y_cr):
    val = math.sqrt((A * fyd / N_y_cr))
    if val <= 0.2:
        print("Försumma instabilitet")
    return val

def λ_z(fyd, A, N_z_cr):
    val = math.sqrt((A * fyd / N_z_cr))
    if val <= 0.2:
        print("Försumma instabilitet")
    return val

def λ_y_tvk4(fyd, A_eff, N_cr):
    val = math.sqrt((A_eff * fyd / N_cr))
    return val

def λ_z_tvk4(fyd, A_eff, N_cr):
    val = math.sqrt((A_eff * fyd / N_cr))
    return val


# Exempel använing
# λ_z = λ_z(fyd, A, N_cr)
# print(f"λz = {λ_z:.3f}")


def C_mi_1(N_Ed, N_cr, Ψ=None):
    if Ψ is not None:
        val1 = 0.79 + 0.21 * Ψ + 0.36 * (Ψ - 0.33) * (N_Ed / N_cr)
    return val1

def C_mi_2(N_Ed, N_cr, Ψ=None, δ=None, L=None, I=None, E=None, M_max=None):
    val2 = 1 + (((math.pi**2 * E * I * abs(δ)) / (L**2 * M_max)) - 1) * (N_Ed / N_cr)
    return val2

def C_mi_3(N_Ed, N_cr):
    val3 = 1 - 0.18*(N_Ed/N_cr) 
    return val3      
             
def C_mi_4(N_Ed, N_cr):
    val4 = 1 + 0.03 * (N_Ed / N_cr)
    return val4

# Exempel
# C_mz = C_mi_1(N_Ed, N_cr, 0)
# print(f"C_mz = {C_mz:.3f}")

def Φ_y(α, λ_y):
    val = 0.5 * (1 + α*(λ_y - 0.2) + λ_y**2)
    return val

def Φ_z(α, λ_z):
    val = 0.5 * (1 + α*(λ_z - 0.2) + λ_z**2)
    return val

# Exempel
# Φ_z = kb.böjknäckning.Φ_z(α, λ_z)
# print(f"Φ_z = {Φ_z:.3f}")

def χ_y(Φ_y, λ_y):
    χ = 1 / (Φ_y + math.sqrt(Φ_y**2 - λ_y**2))
    val = min(χ, 1)
    return val

def χ_z(Φ_z, λ_z):
    χ = 1 / (Φ_z + math.sqrt(Φ_z**2 - λ_z**2))
    val = min(χ, 1)
    return val

# Exempel

# χ_z = kb.böjknäckning.χ_z(Φ_z, λ_z)
# print(f"χ_z = {χ_z:.3f}")



# Enligt EN 1993-1-1 kapitel ????
def k_yy(C_my, C_yy, N_Ed, N_cr, χ_y, tvk):
    if tvk == 1 or 2:
        val = C_my / (1 - χ_y * (N_Ed / N_cr)) * C_yy
    if tvk == 3 or 4:
        val = C_my / (1 - χ_y * (N_Ed / N_cr))
    else:
        print("felaktning tvärsnittsklass")
    return val

def k_zz(C_mz, N_Ed, N_cr, χ_z, tvk, C_zz=0):
    if tvk == 1 or 2:
        val = C_mz / (1 - χ_z * (N_Ed / N_cr)) * C_zz
    if tvk == 3 or 4:
        val = C_mz / (1 - χ_z * (N_Ed / N_cr))
    else:
        print("felaktning tvärsnittsklass")
    return val

def C_yy(W_y_pl, W_y_el, C_my, λ, N_Ed, N_rk):
    v = W_y_pl / W_y_el
    w_y = min(v, 1.5)
    val = 1 + (w_y - 1)*((2 - (1.6 / w_y) * C_my**2 * λ * (1 + λ))) * (N_Ed / N_rk)
    max(val, (W_y_el / W_y_pl))
    return val

def C_zz(W_z_pl, W_z_el, C_mz, λ_z, N_Ed, N_rk):
    v = W_z_pl / W_z_el
    w_z = min(v, 1.5)
    val = 1 + (w_z - 1)*((2 - (1.6 / w_z) * C_mz**2 * λ_z * (1 + λ_z))) * (N_Ed / N_rk)
    max(val, (W_z_el / W_z_pl))
    return val
