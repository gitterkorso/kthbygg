# följer standard SS-EN-10219
import math
from IPython.display import display, Math
import sympy as smp
from sympy import init_printing
init_printing(use_latex='mathjax')



def cirkel(D, T, print_output=True):
    if not all(math.isfinite(v) and v > 0 for v in (D, T)):
        raise ValueError("D och T måste vara ändliga och positiva.")
    if D <= 2*T:
        raise ValueError("Ogiltig cirkel: D måste vara > 2*T (positiv innerdiameter).")
    d = D - 2*T
    A_s = math.pi * D / 1000

    A = (math.pi * (D**2 - d**2)) / 4

    M = 0.00785 * A

    I = math.pi * (D**4 - d**4) / 64

    i = math.sqrt(I/A)

    W_el = (2 * I) / D

    W_pl = (D**3 - d**3) / 6

    I_t = 2 * I

    C_t = 2 * W_el

    if print_output:
        print(f"D = {D:.2f} [mm]")
        print(f"T = {T:.2f} [mm]")
        print(f"d = {d:.2f} [mm]")
        print(f"A_s = {A_s:.2f} [m²/m]")
        print(f"A = {A:.2f} [mm²]")
        print(f"M = {M:.2f} [kg/m]")
        print(f"I = {I:.2f} [mm⁴]")
        print(f"i = {i:.2f} [mm]")
        print(f"W_el = {W_el:.2f} [mm³]")
        print(f"W_pl = {W_pl:.2f} [mm³]")
        print(f"I_t = {I_t:.2f} [mm⁴]")
        print(f"C_t = {C_t:.2f} [mm³]")

    return d, A_s, A, M, I, i, W_el, W_pl, I_t, C_t

# Exempel på användning
# d, A_s, A, M, I, i, W_el, W_pl, I_t, C_t = cirkel(30, 2)






def RHS(H, B, T, print_output=True):
    if not all(math.isfinite(v) and v > 0 for v in (H, B, T)):
        raise ValueError("H, B och T måste vara ändliga och positiva.")

    if B <= 2*T or H <= 2*T:
        raise ValueError(f"Ogiltig RHS: B eller H måste vara > 2*T ! (du angav B={B}, H={H}, T={T})")
    
    if T <= 6:
        r_o = 2 * T
        r_i = 1 * T
    elif T <= 10:
        r_o = 2.5 * T
        r_i = 1.5 * T
    else:
        r_o = 3.0 * T
        r_i = 2 * T
    
    if min(H, B) < 2*r_o or min(H, B) - 2*T < 2*r_i:
        raise ValueError("Ogiltig RHS: hörnradierna ryms inte inom tvärsnittets mått.")

    A_s = (2) * (H + B - 4 * r_o + math.pi * r_o) / 10**3

    A = (2 * T * (B + H - 2 * T) - (4 - math.pi) * (r_o**2 - r_i**2))

    M = 0.7850 * A / 100

    R_c = (r_o + r_i)/2

    A_g = (1 - math.pi/4) * r_o**2

    A_ξ = (1 - math.pi/4) * r_i**2

    h_g_major = H/2 - (10 - 3*math.pi)/(12 - 3*math.pi) * r_o 

    h_g_minor = B/2 - (10 - 3*math.pi)/(12 - 3*math.pi) * r_o 

    h_ξ_major = (H - 2*T)/2 - (10 - 3*math.pi)/(12 - 3*math.pi) * r_i  

    h_ξ_minor = (B - 2*T)/2 - (10 - 3*math.pi)/(12 - 3*math.pi) * r_i  

    I_g = ((1/3) - (math.pi/16) - (1/(3*(12 - 3*math.pi)))) * r_o**4

    I_ξξ = ((1/3) - (math.pi/16) - (1/(3*(12 - 3*math.pi)))) * r_i**4

    h = 2 * ((B - T) + (H - T)) - 2 * R_c * (4 - math.pi)

    A_h = (B - T) * (H - T) - R_c**2 * (4 - math.pi)

    I_y = ((B*H**3 / 12) - (((B - 2 * T) * (H - 2 * T)**3) / 12) - 4 * (I_g + A_g * h_g_major**2) + 4 * (I_ξξ + A_ξ * h_ξ_major**2))

    I_z = ((H*B**3 / 12) - (((H - 2 * T) * (B - 2 * T)**3) / 12) - 4 * (I_g + A_g * h_g_minor**2) + 4 * (I_ξξ + A_ξ * h_ξ_minor**2))

    i_y = math.sqrt(I_y/A)

    i_z = math.sqrt(I_z/A)

    W_y_pl = ((B*H**2 / 4) - (((B - 2*T)*(H - 2*T)**2) / 4) - 4 * (A_g*h_g_major)  + 4 * (A_ξ*h_ξ_major))

    W_z_pl = ( (H*B**2 / 4) - (((H - 2*T)*(B - 2*T)**2) / 4) - 4 * (A_g*h_g_minor) + 4 * (A_ξ*h_ξ_minor))

    W_y_el = (2*I_y / H)

    W_z_el = (2*I_z / B)
  
    K = 2*A_h*T / h

    I_t = ((T**3 * h) / 3 + 2*K*A_h) 

    C_t = I_t / (T + K/T) 

    if print_output is True or print_output == "print":
        print(f"A = {A:.0f} [mm²]")
        print(f"A_s = {A_s:.3f} [m²/m]")  
        print(f"M = {M:.1f}[kg/m]")
        print(f"I_y = {I_y:.0f} [mm⁴]")
        print(f"I_z = {I_z:.0f} [mm⁴]")
        print(f"i_y = {i_y:.2f} [mm]")
        print(f"i_z = {i_z:.2f} [mm]")
        print(f"W_y_pl = {W_y_pl:.0f} [mm³]")
        print(f"W_z_pl = {W_z_pl:.0f} [mm³]")
        print(f"W_y_el = {W_y_el:.0f} [mm³]")
        print(f"W_z_el = {W_z_el:.0f} [mm³]")
        print(f"I_t = {I_t:.0f} [mm⁴]")
        print(f"r_o = {r_o:.4f} [mm]")
        print(f"r_i = {r_i:.4f} [mm]")
        print(f"C_t = {C_t:.0f} [mm³]")

    elif print_output == "display":
        display(Math(r"KKR \quad (Rectangular \quad Hollow \quad Section)\quad med \quad måtten: H = " + f" {H} " + r" [mm], B = " + f" {B} " + r" [mm], T = " + f" {T} " + r" [mm]"))
        display(Math(r"A = " + f" {A:.3f}" + r" \ [mm^2]"))
        display(Math(r"A_s = " + f" {A_s:.3f}" + r" \ [m^2/m]"))
        display(Math(r"M = " + f" {M:.3f}" + r" \ [kg/m]"))
        display(Math(r"I_y = " + f" {I_y:.3f}" + r" \ [mm^4]"))
        display(Math(r"I_z = " + f" {I_z:.3f}" + r" \ [mm^4]"))
        display(Math(r"i_y = " + f" {i_y:.3f}" + r" \ [mm]"))
        display(Math(r"i_z = " + f" {i_z:.3f}" + r" \ [mm]"))
        display(Math(r"W_{y,pl} = " + f" {W_y_pl:.3f}" + r" \ [mm^3]"))
        display(Math(r"W_{z,pl} = " + f" {W_z_pl:.3f}" + r" \ [mm^3]"))
        display(Math(r"W_{y,el} = " + f" {W_y_el:.3f}" + r" \ [mm^3]")) 
        display(Math(r"W_{z,el} = " + f" {W_z_el:.3f}" + r" \ [mm^3]"))
        display(Math(r"I_t = " + f" {I_t:.3f}" + r" \ [mm^4]"))
        display(Math(r"r_o = " + f" {r_o:.3f}" + r" \ [mm]"))   
        display(Math(r"r_i = " + f" {r_i:.3f}" + r" \ [mm]"))
        display(Math(r"C_t = " + f" {C_t:.3f}" + r" \ [mm^3]"))

    return A, I_y, I_z, i_y, i_z, W_y_pl, W_z_pl, W_y_el, W_z_el, I_t, r_o, r_i, A_s, M

# Exempel på användning
# A, I_y, I_z, i_y, i_z, W_y_pl, W_z_pl, W_y_el, W_z_el, I_t, r_o, r_i, A_s, M = RHS(200,100,5)











def ellips(H, B, T, print_output=True):
    if not all(math.isfinite(v) and v > 0 for v in (H, B, T)):
        raise ValueError("H, B och T måste vara ändliga och positiva.")
    
    if B <= 2*T or H <= 2*T:
        raise ValueError(f"Ogiltig ellips: B eller H måste vara > 2*T ! (du angav B={B}, H={H}, T={T})")
    
    # Beräkna hjälpvariabler enligt Annex A.4
    
    # Area begränsad av mittlinje
    A_m = math.pi * (H - T) * (B - T) / 4  # [mm²]
    
    # Yttre omkrets (approximativ formel från standarden)
    P = (math.pi / 2) * (H + B) * (1 + 0.25 * ((H - B) / (H + B))**2)  # [mm]
    
    # Omkrets vid mittlinje (approximativ formel)
    U = (math.pi / 2) * (H + B - 2 * T) * (1 + 0.25 * ((H - B) / (H + B - 2 * T))**2)  # [mm]
    
    # Yta per längdenhet
    A_s = P / 10**3  # [m²/m]
    
    # Tvärsnittsarea
    A = (math.pi * (H * B - (H - 2*T) * (B - 2*T)) / 4) # [mm²]
    
    # Massa per längdenhet
    M = 0.00785 * A  # [kg/m]
    
    # Tröghetsmoment major axis (yy)
    I_y = (math.pi * (B * H**3 - (B - 2*T) * (H - 2*T)**3) / 64) # [mm⁴]
    
    # Tröghetsmoment minor axis (zz)
    I_z = (math.pi * (H * B**3 - (H - 2*T) * (B - 2*T)**3) / 64)  # [mm⁴]
    
    # Gyrationsradie
    i_y = math.sqrt(I_y / A)  # [mm]
    i_z = math.sqrt(I_z / A)  # [mm]
    
    # Elastiskt motstånd
    W_y_el = 2 * I_y / H  # [mm³]
    W_z_el = 2 * I_z / B  # [mm³]
    
    # Plastiskt motstånd
    W_y_pl = (H**2 * B - (H - 2*T)**2 * (B - 2*T)) / 6  # [mm³]
    W_z_pl = (B**2 * H - (B - 2*T)**2 * (H - 2*T)) / 6  # [mm³]
    
    # Vridtröghet
    I_t = ((U * T**3) / 3 + 4 * A_m**2 * T / U)  # [mm⁴]
    
    # Vridmodul
    C_t = I_t / (T + 2 * A_m / U)  # [mm³]
    
    if print_output:
        print(f"A = {A:.1f} [mm²]")
        print(f"A_s = {A_s:.3f} [m²/m]")
        print(f"M = {M:.1f} [kg/m]")
        print(f"I_y = {I_y:.4f} [mm⁴]")
        print(f"I_z = {I_z:.4f} [mm⁴]")
        print(f"i_y = {i_y:.4f} [mm]")
        print(f"i_z = {i_z:.4f} [mm]")
        print(f"W_y_el = {W_y_el:.4f} [mm³]")
        print(f"W_z_el = {W_z_el:.4f} [mm³]")
        print(f"W_y_pl = {W_y_pl:.4f} [mm³]")
        print(f"W_z_pl = {W_z_pl:.4f} [mm³]")
        print(f"I_t = {I_t:.4f} [mm⁴]")
        print(f"C_t = {C_t:.4f} [mm³]")
    
    return A, I_y, I_z, i_y, i_z, W_y_el, W_z_el, W_y_pl, W_z_pl, I_t, C_t, A_s, M


# Exempel på anvädning
# A, I_yy, I_zz, i_yy, i_zz, W_el_yy, W_el_zz, W_pl_yy, W_pl_zz, I_t, C_t, A_s, M = ellips(100, 30, 3)
