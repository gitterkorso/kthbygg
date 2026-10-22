import math
fyd = 275

# Tvärsnittsklassning enligt EN 1993-1-1 tabell 5.2.
# Alla funktioner skriver ut klassningen och returnerar klassen (1-4).


def epsilon(fyd):
    ε = math.sqrt(235 / fyd)
    return ε


def _andel_tryckt(αc, c):
    # α är den tryckta andelen av c och måste ligga i intervallet 0 < α ≤ 1
    α = αc / c
    if not 0 < α <= 1:
        raise ValueError(f"α = αc/c måste ligga mellan 0 och 1 (du angav αc = {αc}, c = {c}, α = {α:.3f})")
    return α


def tryck_inre(c, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if c/t <= 33*ε:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {33*ε:.2f} = 33·ε")
       return 1
    elif c/t <= 38*ε:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {38*ε:.2f} = 38·ε")
       return 2
    elif c/t <= 42*ε:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {42*ε:.2f} = 42·ε")
     return 3
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {42*ε:.2f} = 42·ε")
      return 4




def böj_inre(c, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if c/t <= 72*ε:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {72*ε:.2f} = 72·ε")
       return 1
    elif c/t <= 83*ε:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {83*ε:.2f} = 83·ε")
       return 2
    elif c/t <= 124*ε:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {124*ε:.2f} = 124·ε")
     return 3
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {124*ε:.2f} = 124·ε")
      return 4



def tryck_böj_inre(c, t, f_y, αc, ψ):
    # Klassificering av tryckt plåt enligt Eurokod 3 (EN 1993-1-1 Tabell 5.2a)
    # för inre element utsatta för tryck och böjning.
    # αc är tryckt längd vid plastisk spänningsfördelning (klass 1 och 2),
    # ψ är spänningskvoten σ2/σ1 vid elastisk spänningsfördelning (klass 3).

    # Materialparameter
    ε = math.sqrt(235 / f_y)

    # Geometrisk parameter
    α = _andel_tryckt(αc, c)
    print(f"α = {α:.3f} (förhållandet mellan tryckt zon och hela plåthöjden)")

    print(f"ε = {ε:.3f} (materialparameter för stål med f_y = {f_y} MPa)\n")

    # Klass 1 och 2 enligt Eurokod 3 tabell 5.2a
    if α > 0.5:
        gräns_1 = 396 * ε / (13 * α - 1)
        gräns_2 = 456 * ε / (13 * α - 1)
        text_1, text_2 = "396·ε/(13·α-1)", "456·ε/(13·α-1)"
    else:
        gräns_1 = 36 * ε / α
        gräns_2 = 41.5 * ε / α
        text_1, text_2 = "36·ε/α", "41.5·ε/α"

    if c/t <= gräns_1:
        print(f"Klass 1 (plastisk böjstyvhet får användas)\n"
              f"→ c/t = {c/t:.2f} ≤ {gräns_1:.2f} = {text_1}\n")
        return 1
    if c/t <= gräns_2:
        print(f"Klass 2 (plastisk böjstyvhet får användas)\n"
              f"→ c/t = {c/t:.2f} ≤ {gräns_2:.2f} = {text_2}\n")
        return 2

    # Klass 3 eller 4 beroende på ψ
    if ψ > -1:
        gräns_3 = 42 * ε / (0.67 + 0.33 * ψ)
        text_3 = "42·ε/(0.67+0.33·ψ)"
    else:
        gräns_3 = 62 * ε * (1 - ψ) * math.sqrt(-ψ)
        text_3 = "62·ε·(1-ψ)·√(−ψ)"

    if c/t <= gräns_3:
        print(f"Klass 3 (begränsad till elastisk böjstyvhet)\n"
              f"→ c/t = {c/t:.2f} ≤ {gräns_3:.2f} = {text_3}\n")
        return 3
    print(f"Klass 4 (reduktion av tvärsnitt behövs!)\n"
          f"→ c/t = {c/t:.2f} > {gräns_3:.2f} = {text_3}\n")
    return 4





def tryck_frikant(c, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if c/t <= 9*ε:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {9*ε:.2f} = 9·ε")
       return 1
    elif c/t <= 10*ε:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {10*ε:.2f} = 10·ε")
       return 2
    elif c/t <= 14*ε:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {14*ε:.2f} = 14·ε")
     return 3
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {14*ε:.2f} = 14·ε")
      return 4





def tip_tryck_frikant(c, t, fyd, αc, kσ):
    # calculations
    ε = math.sqrt(235/fyd)

    # α är den tryckta andelen av c (0 < α ≤ 1)
    α = _andel_tryckt(αc, c)

    # klassificering
    if c/t <= 9*ε/α:
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {9*ε/α:.2f} = 9·ε/α")
       return 1
    elif c/t <= 10*ε/α:
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {10*ε/α:.2f} = 10·ε/α")
       return 2
    elif c/t <= 21*ε*math.sqrt(kσ):
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")
     return 3
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")
      return 4







def tip_drag_frikant(c, t, fyd, αc, kσ):
    # calculations
    ε = math.sqrt(235/fyd)

    # α är den tryckta andelen av c (0 < α ≤ 1)
    α = _andel_tryckt(αc, c)

    # klassificering
    if c/t <= (9*ε)/(α*math.sqrt(α)):
       print(f"Klass 1 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {(9*ε)/(α*math.sqrt(α)):.2f} = 9·ε/(α·√α)")
       return 1
    elif c/t <= (10*ε)/(α*math.sqrt(α)):
       print(f"Klass 2 (plastisk böjstyvhet får användas) c/t = {c/t:.2f} ≤ {(10*ε)/(α*math.sqrt(α)):.2f} = 10·ε/(α·√α)")
       return 2
    elif c/t <= 21*ε*math.sqrt(kσ):
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) c/t = {c/t:.2f} ≤ {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")
     return 3
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs!) c/t = {c/t:.2f} > {21*ε*math.sqrt(kσ):.2f} = 21·ε·√(kσ)")
      return 4








def vinkelstång(h, b, t, fyd):
    # Tryckt vinkelstång (tabell 5.2 blad 3). Klass 3 kräver att båda villkoren
    # är uppfyllda, annars klass 4. h/t kontrolleras för det längsta benet.
    ε = math.sqrt(235/fyd)
    h_max = max(h, b)

    villkor_h = h_max/t <= 15*ε
    villkor_bh = (b+h)/(2*t) <= 11.5*ε

    print(f"h/t = {h_max/t:.2f} {'≤' if villkor_h else '>'} {15*ε:.2f} = 15·ε")
    print(f"(b+h)/(2·t) = {(b+h)/(2*t):.2f} {'≤' if villkor_bh else '>'} {11.5*ε:.2f} = 11.5·ε")

    if villkor_h and villkor_bh:
       print("Klass 3 (begränsad till elastisk böjstyvhet)")
       return 3
    else:
       print("Klass 4 (reduktion av tvärsnitt behövs!)")
       return 4




def cirkulärt_rör(d, t, fyd):
    # calculations
    ε = math.sqrt(235/fyd)

    # klassificering
    if d/t <= 50*ε**2:
       print(f"Klass 1 (plastisk böjstyvhet får användas) d/t = {d/t:.2f} ≤ {50*ε**2:.2f} = 50·ε²")
       return 1
    elif d/t <= 70*ε**2:
       print(f"Klass 2 (plastisk böjstyvhet får användas) d/t = {d/t:.2f} ≤ {70*ε**2:.2f} = 70·ε²")
       return 2
    elif d/t <= 90*ε**2:
     print(f"Klass 3 (begränsad till elastisk böjstyvhet) d/t = {d/t:.2f} ≤ {90*ε**2:.2f} = 90·ε²")
     return 3
    else:
      print(f"Klass 4 (reduktion av tvärsnitt behövs! SE 1993-1-6) d/t = {d/t:.2f} > {90*ε**2:.2f} = 90·ε²")
      return 4




if __name__ == "__main__":
    tryck_inre(100, 3, fyd)
    böj_inre(100, 3, fyd)
    tryck_böj_inre(378, 10, 235, 350, ψ=-1)
    tryck_frikant(20, 3, fyd)
    tip_tryck_frikant(80, 3, fyd, 78, 4.0)
    tip_drag_frikant(80, 2, fyd, 78, 4.0)
    vinkelstång(100, 60, 4, fyd)
    cirkulärt_rör(100, 1, fyd)
