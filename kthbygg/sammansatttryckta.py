
import math


# Effektivt tröghetsmoment för fackverksuppbyggda bärverksdelar
def I_eff(h_0,A_ch):
    val = 0.5 * h_0**2 * A_ch
    return val




def S_v(a, h_0, A_ch, n, E, A, A_d, A_V, d):
    if a == a:
        S_v_val = 0
        # Bla bla bla

    return S_v_val



# Tabell 6.8 effektivitetsfaktor

def μ(L, h_0, A_ch, I_ch):

    I_1 = 0.5 * h_0**2 * A_ch + 2 * I_ch
    i_0 = math.sqrt(I_1/(2*A_ch))
    λ = L / i_0

    if λ >= 150:
        val = 0.0
    elif 75 <= λ < 150:
        val = 2 - (λ / 75)
    else:
        val = 1.0
    return val

# Exempel användning
# μ = kb.sammansattatryckta.μ(L, h_0, A_ch, I_ch)