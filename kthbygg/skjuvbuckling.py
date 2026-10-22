import sympy as smp
import math

def hjälp():
    print("För att kontrollera om skjuvbuckling ens behöver beaktas, h_w / t_w > 72*ε/η")
    print("\n Skjuvbucklingsrecept: τ_cr (V_cr) => λ_w => χ_w")
    print("\n Patchloadingrecept: ")
    print("\n Brottkriterie: P_Ed ≤ F_Rd = χ_F * l_y * t_w * (f_yw / γ_M1)")
    print(" F_cr => λ_F => χ_F")
    print(" Patch böjmoment interaktion om : η_2 + 0.8 * η_1 ≤ 1.4")
    print(" Interaktion böj-skjuv om: η_3 ≤ 0.5")



# Shear resistance if no shear buckling
def V_pl_Rd(f_yd, γ_M0, A_v):
    V_pl_Rd = A_v * f_yd / (γ_M0 * math.sqrt(3))
    return V_pl_Rd


# Eta = 1.2 enligt Nationella bilagan för stålsorter upp till S460 (vi har S235) för stålsorter över S460 
def eta(f_yd):
    if f_yd > 460:
        η = 1.0
    else:
        η = 1.2
    return η

# funktion samma som ovan fast med η
def η(f_yd):
    if f_yd > 460:
        eta = 1.0
    else:
        eta = 1.2
        return eta


def skjuvbucklingscheck(h_w, t_w, f_yd):
    ε = (235 / f_yd) ** 0.5
    η = eta(f_yd)
    if h_w / t_w > 72*ε/η:
        print("skjuvbuckling behöver beaktas! följ avsnitt 5 i 1993-1-5")
        print(f"h_w / t_w = {h_w / t_w:.1f} > {72*ε/η:.1f} ")
    else:
        print("Ingen hänsyn behöver tas till skjuvbuckling!")
        print(f"h_w / t_w = {h_w / t_w:.1f} ≤ {72*ε/η:.1f} ")


def χ_F(λ_F):
    chi_F = 0.5 / λ_F 
    val = min(1.0, chi_F)
    return val




# ------------------------------------------------------------------------
# Metod 1: Säkra sidan metoden (En förenklad metod som alltid ger säkra sidan)
def λ_w_förenklad(h_w, t_w, ε):
    λ_w = (h_w / (86.4 * ε * t_w))
    return λ_w
# ------------------------------------------------------------------------


# Bucklingskoefficient k_τ
# a är avståndet mellan tväravstyvningar
# I_st är tröghetsmoment för längdavstyvning
# t är plåttjockleken på avstyvningen
def k_τ(h_w, a, I_st=0, t=0):
        if I_st == 0 or t == 0:
            k_τsl = 0
        else:
            k_τsl = max(9 * (h_w / a) * ((I_st / t**3 * h_w)**3)**(1/4), ((2.1/t) * (I_st / h_w)**(1/3)))
    
        if a / h_w > 1:
            k_τ = 5.34 + 4 * (h_w/a)**2 + k_τsl
    
        else:
            k_τ = 4.0 + 5.34 * (h_w / a)**2 + k_τsl
        return k_τ

# ------------------------------------------------------------------------
# Metod 2: λ_w med k_τ beräknas fram
def λ_w(h_w, t_w, ε, k_τ):
    λ_w = (h_w / (37.4 * ε * t_w * (k_τ)**0.5))
    return λ_w
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Metod 3: λ_w med kritisk skjuvspänning τ_cr och k_τ beräknas fram
def τ_cr(t_w, h_w, k_τ, E=210000, ν=0.3):
    τ_cr = (k_τ * (math.pi**2) * E * t_w**2) / ((12 * (1 - ν**2)) * h_w**2)
    return τ_cr

def λ_w_med_τ_cr(f_yw, τ_cr):
    λ_w = (f_yw / (τ_cr * math.sqrt(3)))**0.5
    return λ_w
# ------------------------------------------------------------------------


    





# Funktion för att beräkna χ_w
def χ_w(λ_w, η, styv_ändavstyvning=True):
    if λ_w < 0.83 / η:
        χ = η
    elif λ_w < 1.08:
        χ = 0.83 / λ_w
    else:
        if styv_ändavstyvning:
            χ = 1.37 / (0.7 + λ_w)
        else:
            χ = 0.83 / λ_w
    return χ


# Reduktionsfaktor för positiv effekt från flänsar χ_f

# a är avståndet mellan tväravstyvningar
def χ_f(M_Ed, a, h_w, b_f, t_f, t_w, f_yw, f_yf, tvk):

    c = a * (0.25 + 1.6*b_f * t_f**2 * f_yf / (t_w * h_w**2 * f_yw))

    # Beräkna M_{f,Ed} momentbärförmåga för flänsarna
    if tvk == 1 or tvk == 2:

        W_pl_f = 2 * (b_f * t_f) * (h_w + t_f) / 2 + (t_w * h_w**2) / 4
        M_f_Rd = W_pl_f * f_yf / 1.0


    elif tvk == 3:
        I_y_f = (b_f * t_f**3) / 12 + b_f * t_f * (h_w / 2 + t_f / 2)**2

        z_max = h_w / 2 + t_f / 2
        
        W_el_f = I_y_f / z_max 

        M_f_Rd = W_el_f * f_yf / 1.0

    elif tvk == 4:
        print("Reducerat tvärsnitt måste användas för flänsarna, χ_f kan inte beräknas")


    # b_f inte mer än 15 * epsilon * t_f på varje sida av webben
    if b_f - t_w > 30 * t_f * math.sqrt(235 / f_yf):
        b_f = 2 * 15 * t_f * math.sqrt(235 / f_yf) + t_w
    else:
        b_f = b_f

    # Kontrollera att momentet i flänsarna inte redan är fullt utnyttjat
    if M_Ed < M_f_Rd:
        print(f"Momentet i flänsarna är inte fullt utnyttjat: M_Ed = {M_Ed/1e6:.2f} < M_f_Rd = {M_f_Rd/1e6:.2f}. χ_f kan beräknas.")
        val = (b_f * t_f**2 * f_yf * math.sqrt(3)) / (c * h_w * t_w * f_yw) * (1 - (M_Ed / M_f_Rd)**2)
    else:
        print(f"Momentet i flänsarna är redan fullt utnyttjat: M_Ed = {M_Ed/1e6:.2f} ≥ M_f_Rd = {M_f_Rd/1e6:.2f}. χ_f kan inte beräknas.")
        val = 0

    if a > 2 * h_w:
        print(f"Vertikala avstyvningar längre från varandra än 2 * h_w ({a:.2f} mm < {2*h_w:.2f} mm). χ_f ger ingen inverkan.")
        val = 0
    
    return val, M_f_Rd




# Reduktionsfaktor för skjuvbuckling
def χ_V(χ_w, χ_f, η):
    val = min(χ_w + χ_f, η)
    return val



def V_c_Rd(f_yw, γ_M1, χ_V, h_w, t_w):
    val = χ_V * h_w * t_w * (f_yw / γ_M1) / math.sqrt(3)
    return val















def plotta_chi_w():
    import matplotlib.pyplot as plt
    import numpy as np

    # Möjliga värden på η
    etas = [1.0, 1.2]

    # Skapa intervall för λ̄w
    λw = np.linspace(0.01, 2.0, 500)  # börjar vid 0.01 för att undvika delning med 0

    plt.figure(figsize=(8, 6))

    # --- Rita kurvor för styv och vek ändavstyvning ---
    for η in etas:
        styv = np.zeros_like(λw)
        vek = np.zeros_like(λw)

        # Styv ändavstyvning
        for i, val in enumerate(λw):
            if val < 0.83 / η:
                styv[i] = η
            elif 0.83 / η <= val < 1.08:
                styv[i] = 0.83 / val
            else:
                styv[i] = 1.37 / (0.7 + val)

        # Vek ändavstyvning
        for i, val in enumerate(λw):
            if val < 0.83 / η:
                vek[i] = η
            else:
                vek[i] = 0.83 / val

        # Plotta båda kurvorna för vald η
        plt.plot(λw, styv, label=fr"Styv (η={η})", linewidth=2)
        plt.plot(λw, vek, '--', label=fr"Vek (η={η})", linewidth=2)

    # --- Lägg till referenskurvan y = 1 / λ² ---
    y = 1 / λw**2
    plt.plot(λw, y, linestyle='-.', linewidth=2, label=r'$χ_w = 1 / \lambda^2$')

    # --- Layout ---
    plt.xlabel(r"Reduktionens slankhet $\bar{\lambda}_w$")
    plt.ylabel(r"Reduktionsfaktor $\chi_w$")
    plt.title(r"Reduktionsfaktor $\chi_w$ för styv och vek ändavstyvning samt $χ_w = 1/\lambda^2$")
    plt.grid(True)
    plt.legend()
    plt.ylim(0, 1.5)
    plt.xlim(0, 2.0)
    plt.tight_layout()
    plt.show()