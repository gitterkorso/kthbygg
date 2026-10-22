import math
fyd = 275


def epsilon(fyd):
    ε = math.sqrt(235 / fyd)
    return ε

def tryck_inre(c, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if c/t <= 33*ε:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {33*ε:.2f} = 33·ε")
    elif c/t <= 38*ε:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {38*ε:.2f} = 38·ε")
    elif c/t <= 42*ε:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {42*ε:.2f} = 42·ε")
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {42*ε:.2f} = 42·ε")




def böj_inre(c, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if c/t <= 72*ε:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {72*ε:.2f} = 72·ε")
    elif c/t <= 83*ε:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {83*ε:.2f} = 83·ε")
    elif c/t <= 124*ε:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {124*ε:.2f} = 124·ε")
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {124*ε:.2f} = 124·ε")



def tryck_böj_inre(c, t, f_y, αc, ψ=0):
    # Klassificering av tryckt plåt enligt Eurokod 3 (EN 1993-1-1 Tabell 5.2a)
    # för inre element utsatta för tryck och böjning.

    # Materialparameter
    ε = math.sqrt(235 / fyd)

    # Geometrisk parameter
    α = αc / c
    print(f"α = {α:.3f} (förhållandet mellan tryckt zon och hela plåthöjden)")

    print(f"ε = {ε:.3f} (materialparameter för stål med f_y = {fyd} MPa)\n")

    # Klassificering enligt Eurokod 3 tabell 5.2a
    if α > 0.5:
        # ---- Fall: α > 0.5 ----
        if c/t <= 396 * ε / (13 * α - 1):
            print(f"Klass 1 (plastisk böjstyvhet får användas)\n"
                  f"→ Elementet är tillräckligt tjockt: c/t = {c/t:.2f} ≤ {396*ε/(13*α - 1):.2f} = 396·ε/(13·α-1)\n")
        elif c/t <= 456 * ε / (13 * α - 1):
            print(f"Klass 2 (plastisk böjstyvhet får användas)\n"
                  f"→ c/t = {c/t:.2f} ≤ {456*ε/(13*α - 1):.2f} = 456·ε/(13·α-1)\n")
        else:
            # Klass 3 eller 4 beroende på ψ
            if ψ > -1:
                if c/t <= 42 * ε / (0.67 + 0.33 * ψ):
                    print(f"Klass 3 (begränsad till elastisk böjstyvhet)\n"
                          f"→ c/t = {c/t:.2f} ≤ {42*ε/(0.67 + 0.33*ψ):.2f} = 42·ε/(0.67+0.33·ψ) \n")
                else:
                    print(f"Klass 4 (reduktion av tvärsnitt behövs!)\n"
                          f"→ c/t = {c/t:.2f} > {42*ε/(0.67 + 0.33*ψ):.2f} = 42·ε/(0.67+0.33·ψ)\n")
            elif ψ <= -1:
                if c/t <= 62 * ε * (1 - ψ) * math.sqrt(-ψ):
                    print(f"Klass 3 (begränsad till elastisk böjstyvhet)\n"
                          f"→ c/t = {c/t:.2f} ≤ {62*ε*(1 - ψ)*math.sqrt(-ψ):.2f} = 62·ε·(1-ψ)·√(−ψ)\n")
                else:
                    print(f"Klass 4 (reduktion av tvärsnitt behövs!)\n"
                          f"→ c/t = {c/t:.2f} > {62*ε*(1 - ψ)*math.sqrt(-ψ):.2f} = 62·ε·(1-ψ)·√(−ψ)\n")
    else:
        # ---- Fall: α ≤ 0.5 ----
        if c/t <= 36 * ε / α:
            print(f"Klass 1 (plastisk böjstyvhet får användas)\n"
                  f"→ c/t = {c/t:.2f} ≤ {36*ε/α:.2f} = 36·ε/α \n")
        elif c/t <= 41.5 * ε / α:
            print(f"Klass 2 (plastisk böjstyvhet får användas)\n"
                  f"→ c/t = {c/t:.2f} ≤ {41.5*ε/α:.2f} = 41.5·ε/α\n")
        else:
            if ψ > -1:
                if c/t <= 42 * ε / (0.67 + 0.33 * ψ):
                    print(f"Klass 3 (begränsad till elastisk böjstyvhet)\n"
                          f"→ c/t = {c/t:.2f} ≤ {42*ε/(0.67 + 0.33*ψ):.2f} = 42·ε/(0.67+0.33·ψ)\n")
                else:
                    print(f"Klass 4 (reduktion av tvärsnitt behövs!)\n"
                          f"→ c/t = {c/t:.2f} > {42*ε/(0.67 + 0.33*ψ):.2f} = 42·ε/(0.67+0.33·ψ)\n")
            elif ψ <= -1:
                if c/t <= 62 * ε * (1 - ψ) * math.sqrt(-ψ):
                    print(f"Klass 3 (begränsad till elastisk böjstyvhet)\n"
                          f"→ c/t = {c/t:.2f} ≤ {62*ε*(1 - ψ)*math.sqrt(-ψ):.2f} = 62·ε·(1-ψ)·√(−ψ)\n")
                else:
                    print(f"Klass 4 (reduktion av tvärsnitt behövs!)\n"
                          f"→ c/t = {c/t:.2f} > {62*ε*(1 - ψ)*math.sqrt(-ψ):.2f} = 62·ε·(1-ψ)·√(−ψ)\n")





def tryck_frikant(c, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if c/t <= 9*ε:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {9*ε:.2f} = 9·ε")
    elif c/t <= 10*ε:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {10*ε:.2f} = 10·ε")
    elif c/t <= 14*ε:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {14*ε:.2f} = 14·ε")
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {14*ε:.2f} = 14·ε")





def tip_tryck_frikant(c, t, fyd, αc, kσ):
    # calculations
    ε = math.sqrt(235/fyd)

    α = c/αc

    # klassificering
    if c/t <= 9*ε/α:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {9*ε/α:.2f} = 10·ε")
    elif c/t <= 10*ε/α:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {10*ε/α:.2f} = 12·ε")
    elif c/t <= 21*ε*math.sqrt(kσ):
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")







def tip_drag_frikant(c, t, fyd, αc, kσ):
    # calculations
    ε = math.sqrt(235/fyd)

    α = c/αc

    # klassificering
    if c/t <= (9*ε)/(α*math.sqrt(α)):
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {(9*ε)/(α*math.sqrt(α)):.2f} = 9·ε/α·√α")
    elif c/t <= (10*ε)/(α*math.sqrt(α)):
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {(10*ε)/(α*math.sqrt(α)):.2f} = 10·ε/α·√α")
    elif c/t <= 21*ε*math.sqrt(kσ):
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")








def vinkelstång_h(h, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if h/t <= 15*ε:
       print(f"Klass 3 (plastisk böjstyvhet får användas) h/t = {h/t:.2f} ≤ {15*ε:.2f} = 15·ε")
    else:
       print(f"Klass 4 (reduktion av tvärsnitt behövs!) h/t = {h/t:.2f} > {15*ε:.2f} = 15·ε")






def vinkelstång_b(h, b, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if (b+h)/(2*t) <= 11.5*ε:
       print(f"Klass 3 (plastisk böjstyvhet får användas) (b+h)/(2*t) = {(b+h)/(2*t):.2f} ≤ {11.5*ε:.2f} = 11.5·ε")
    else:
       print(f"Klass 4 (reduktion av tvärsnitt behövs!) (b+h)/(2*t) = {(b+h)/(2*t):.2f} > {11.5*ε:.2f} = 11.5·ε")





def cirkulärt_rör(d, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)
   
    # klassificering
    if d/t <= 50*ε**2:
       print(f"Klass 1 (plastisk böjstyvhet får användas) d/t = {d/t:.2f} ≤ {50*ε**2:.2f} = 50·ε²")
    elif d/t <= 70*ε**2:
       print(f"Klass 2 (plastisk böjstyvhet får användas) d/t = {d/t:.2f} ≤ {70*ε**2:.2f} = 70·ε²")
    elif d/t <= 90*ε**2:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) d/t = {d/t:.2f} ≤ {90*ε**2:.2f} = 90·ε²")
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs! SE 1993-1-6) d/t = {d/t:.2f} > {90*ε**2:.2f} = 90·ε²")




if __name__ == "__main__":
    tryck_inre(100, 3, fyd)
    böj_inre(100, 3, fyd)
    tryck_böj_inre(378, 10, 235, 350,)
    tryck_frikant(20, 3, fyd)
    tip_tryck_frikant(80, 3, fyd, 78, 4.0)
    tip_drag_frikant(80, 2, fyd, 78, 4.0)
    vinkelstång_h(100, 4, fyd)
    vinkelstång_b(14, 60, 4, fyd)
    cirkulärt_rör(100, 1, fyd)
