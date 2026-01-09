# följer standard SS-EN-10219
import math

def cirkel(D, T, print_output=True):
    d = D - 2*T
    A_s = math.pi * D / 10**3

    A = (math.pi * (D**2 - d**2)) / (4*10**2)

    M = 0.785 * A

    I = math.pi * (D**4 - d**4) / (64 * 10**4)

    i = math.sqrt(I/A)

    W_el = (2 * I * 10) / D

    W_pl = (D**3 - d**3) / (6 * 10**3)

    I_t = 2 * I

    C_t = 2 * W_el

    if print_output:
        print(f"D = {D:.2f} mm")
        print(f"T = {T:.2f} mm")
        print(f"d = {d:.2f} mm")
        print(f"A_s = {A_s:.2f} m²/m")
        print(f"A = {A:.2f} cm²")
        print(f"M = {M:.2f} kg/m")
        print(f"I = {I:.2f} cm⁴")
        print(f"i = {i:.2f} cm")
        print(f"W_el = {W_el:.2f} cm³")
        print(f"W_pl = {W_pl:.2f} cm³")
        print(f"I_t = {I_t:.2f} cm⁴")
        print(f"C_t = {C_t:.2f} cm³")

    return d, A_s, A, M, I, i, W_el, W_pl, I_t, C_t

# Exempel på användning
# d, A_s, A, M, I, i, W_el, W_pl, I_t, C_t = cirkel(30, 2)






def RHS(H, B, T, print_output=True):

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
    
    A_s = (2) * (H + B - 4 * r_o + math.pi * r_o)

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

    if print_output:
        print(f"A = {A:.0f} [mm²]")
        print(f"A_s = {A_s:.0f} [mm]")  
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
        print(f"C_t = {C_t:.0f} [mm⁶]")

    
    return A, I_y, I_z, i_y, i_z, W_y_pl, W_z_pl, W_y_el, W_z_el, I_t, r_o, r_i, A_s, M

# Exempel på användning
# A, I_y, I_z, i_y, i_z, W_y_pl, W_z_pl, W_y_el, W_z_el, I_t, r_o, r_i, A_s, M = RHS(200,100,5)











def ellips(H, B, T, print_output=True):
    
    if B <= 2*T or H <= 2*T:
        raise ValueError(f"Ogiltig ellips: B eller H måste vara > 2*T ! (du angav B={B}, H={H}, T={T})")
    
    # Beräkna hjälpvariabler enligt Annex A.4
    
    # Area begränsad av mittlinje
    A_m = math.pi * (H - T) * (B - T) / 4  # [mm²]
    
    # Yttre omkrets (approximativ formel från standarden)
    P = math.pi * (1.5 * (H + B) - math.sqrt(H * B))  # [mm]
    
    # Omkrets vid mittlinje (approximativ formel)
    U = math.pi * (1.5 * ((H - T) + (B - T)) - math.sqrt((H - T) * (B - T)))  # [mm]
    
    # Yta per längdenhet
    A_s = P / 10**3  # [m²/m]
    
    # Tvärsnittsarea
    A = (math.pi * (H * B - (H - 2*T) * (B - 2*T)) / 4) / 100  # [cm²]
    
    # Massa per längdenhet
    M = 0.785 * A  # [kg/m]
    
    # Tröghetsmoment major axis (yy)
    I_yy = (math.pi * (B * H**3 - (B - 2*T) * (H - 2*T)**3) / 64) / 10**4  # [cm⁴]
    
    # Tröghetsmoment minor axis (zz)
    I_zz = (math.pi * (H * B**3 - (H - 2*T) * (B - 2*T)**3) / 64) / 10**4  # [cm⁴]
    
    # Gyrationsradie
    i_yy = math.sqrt(I_yy / A)  # [cm]
    i_zz = math.sqrt(I_zz / A)  # [cm]
    
    # Elastiskt motstånd
    W_el_yy = 20 * I_yy / H  # [cm³]
    W_el_zz = 20 * I_zz / B  # [cm³]
    
    # Plastiskt motstånd
    W_pl_yy = (H**2 * B - (H - 2*T)**2 * (B - 2*T)) / (6 * 10**3)  # [cm³]
    W_pl_zz = (B**2 * H - (B - 2*T)**2 * (H - 2*T)) / (6 * 10**3)  # [cm³]
    
    # Vridtröghet
    I_t = ((U * T**3) / 3 + 2 * A_m**2 * T / U) / 10**4  # [cm⁴]
    
    # Vridmodul
    C_t = 10 * I_t / (T + 2 * A_m / U)  # [cm³]
    
    if print_output:
        print(f"A = {A:.1f} [cm²]")
        print(f"A_s = {A_s:.3f} [m²/m]")
        print(f"M = {M:.1f} [kg/m]")
        print(f"I_yy = {I_yy:.4f} [cm⁴]")
        print(f"I_zz = {I_zz:.4f} [cm⁴]")
        print(f"i_yy = {i_yy:.4f} [cm]")
        print(f"i_zz = {i_zz:.4f} [cm]")
        print(f"W_el_yy = {W_el_yy:.4f} [cm³]")
        print(f"W_el_zz = {W_el_zz:.4f} [cm³]")
        print(f"W_pl_yy = {W_pl_yy:.4f} [cm³]")
        print(f"W_pl_zz = {W_pl_zz:.4f} [cm³]")
        print(f"I_t = {I_t:.4f} [cm⁴]")
        print(f"C_t = {C_t:.4f} [cm³]")
    
    return A, I_yy, I_zz, i_yy, i_zz, W_el_yy, W_el_zz, W_pl_yy, W_pl_zz, I_t, C_t, A_s, M


# Exempel på anvädning
# A, I_yy, I_zz, i_yy, i_zz, W_el_yy, W_el_zz, W_pl_yy, W_pl_zz, I_t, C_t, A_s, M = ellips(100, 30, 3)