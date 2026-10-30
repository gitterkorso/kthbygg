# dubbelsymetriskt I tvärsnitt
def dubbel_I(b, t_b, t_h, h):

    K_w = (b**3 * h**2 * t_b) / 24

    W_w = b**2 * h * t_b / 6

    Z_w = (b**2*h*t_b) / 4

    return K_w, W_w, Z_w

# Enkelsymetriskt I tvärsnitt
def Enkelt_I(b_ö, t_ö, t_h, b_u, t_u, h):

    I_ö = t_ö * b_ö**3 / 12

    I_u = t_u * b_u**3 / 12

    h_ö = (I_u / (I_ö + I_u)) * h

    h_u = h - h_ö

    K_w = I_ö * h_ö**2 + I_u * h_u**2

    # Plastiskt välvmotstånd
    Z_w = min((h*b_ö**2*t_ö)/4, (h*b_u**2*t_u)/4)

    # Elastiskt välvmotstånd
    W_w = min((2*K_w) / (b_ö * h_ö), 2*K_w/(b_u * h_u))

    return Z_w, W_w, K_w 
