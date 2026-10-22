# Här har vi formler från eurokoden beaktande vippning

import math


def hjälp():
    print("Vippning är en form av instabilitet som kan uppstå i balkar och pelare när de utsätts för böjning. För att bedöma vippningsfaktorn (χ_LT) enligt Eurokod 3, följ dessa steg:")
    print("1. Bestäm tvärsnittstyp. För valsade och ekvivalenta använda 6.3.2.3. Annars avnänd generella metoden 6.3.2.2")


# Vippningskurva enligt 6.3.2.2
def Generella_Vippningskurva(section_type, h, b):
 # Bestämmer bucklingskurva enligt tabellen
    ratio = h / b
    
    if section_type.lower() == "valsad-I":
        if ratio <= 2:
            curve = "a"
            print("Knäckningskurva a -> α_LT = 0.21")
        else:
            curve = "b"
            print("Knäckningskurva b -> α_LT = 0.34")
    elif section_type.lower() == "svetsad-I":
        if ratio <= 2:
            curve = "c"
            print("Knäckningskurva c -> α_LT = 0.49")
        else:
            curve = "d"
            print("Knäckningskurva d -> α_LT = 0.76")
    else:
        return None  # okänt tvärsnitt
    
    # Imperfektionsfaktor enligt kurva
    alpha_values = {
        "a": 0.21,
        "b": 0.34,
        "c": 0.49,
        "d": 0.76
    }

    return alpha_values[curve]




# Vippningskurva enligt 6.3.2.3
def Vippningskurva(section_type, h, b):
    # Bestämmer bucklingskurva enligt tabellen
    ratio = h / b
    
    if section_type.lower() == "valsad":
        if ratio <= 2:
            curve = "b"
            print("Knäckningskurva b -> α_LT = 0.34")
        else:
            curve = "c"
            print("Knäckningskurva c -> α_LT = 0.49")
    elif section_type.lower() == "svetsad":
        if ratio <= 2:
            curve = "c"
            print("Knäckningskurva c -> α_LT = 0.49")
        else:
            curve = "d"
            print("Knäckningskurva d -> α_LT = 0.76")
    else:
        return None  # okänt tvärsnitt
    
    # Imperfektionsfaktor enligt kurva
    alpha_values = {
        "a": 0.21,
        "b": 0.34,
        "c": 0.49,
        "d": 0.76
    }
   
    return alpha_values[curve]




# Beräkningsmetod enligt 6.3.2.3

# λ_LT
def λ_LT(fyd, W_y_pl, M_cr):
    val = math.sqrt((fyd * W_y_pl) / M_cr)
    return val


# Φ_LT
def Φ_LT(α_LT, λ_LT, β):
    # Begränsning för β
    if β <= 0.75:
        β_kalk = 0.75
    else:
        β_kalk = β
    
    # Begränsning för λ_LT0
    if λ_LT >= 0.4:
        λ_LT0 = 0.4
    else: 
        λ_LT0 = λ_LT
    
    Φ_LT_value = 0.5 * (1 + α_LT * (λ_LT - λ_LT0) + β_kalk * λ_LT**2)
    
    return Φ_LT_value


# χ_LT
def χ_LT(Φ_LT, λ_LT, β):
    # Begränsning för β
    if β <= 0.75:
        β_kalk = 0.75
    else:
        β_kalk = β
    
    # Beräkna χ_LT
    χ_LT_value = 1 / (Φ_LT + math.sqrt(Φ_LT**2 - (β_kalk * λ_LT**2)))
    
    # Applicera begränsningar
    χ_LT_value = min(χ_LT_value, 1.0)
    χ_LT_value = min(χ_LT_value, 1 / λ_LT**2)
    
    return χ_LT_value


def f_faktor(k_c, λ_LT):
    # Beräknar f enligt: f = 1 - 0.5*(1 - k_c) * (1 - 2*(λ_LT - 0.8)**2) men <= 1.0
    f = 1 - 0.5 * (1 - k_c) * (1 - 2.0 * (λ_LT - 0.8)**2)
    return min(f, 1.0)

def χ_LT_mod(χ_LT, f):
    # χ_LT_mod = χ_LT / f men <= 1.0
    value = χ_LT / f
    return min(value, 1.0)




# Momentbärförmåga med avseende vippning
def M_b_Rd(χ_LT_mod, W_y_pl, f_yd):
    
    M_b_Rd_value = χ_LT_mod * W_y_pl * f_yd
    
    return M_b_Rd_value







#κ = 1.0 # Forked boundary condition factor
# if doubble symmetry, use t_z = 0
#t_z = 0
#β = (t_z / 2) * math.sqrt(B_z / C_w)
#k = math.sqrt(C / C_w)
#π = math.pi
#L = 4000

#print(f"β = {β:.3f}")
#print(f"k = {k:.8f}")


#M_cr = κ * π * (math.sqrt(B_z * C) / L) * (((κ * π * β) / ( k * L)) + math.sqrt(1 + ((κ * π) / (k * L))**2 * (1 + β**2)))
#display(Math(r"M_{cr} = " + f"{M_cr/1e6:.2f}" + " kNm"))
#print(M_cr)