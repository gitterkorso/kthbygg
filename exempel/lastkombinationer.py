from kthbygg import Lastkomb


# Signerade lasteffekter i kN/m, positiv effekt är ogynnsam för sökt maximum.
# Faktorerna är exempelvärden; ange värden för aktuella lastkategorier.
# Endast oberoende, samtidigt möjliga laster ska ingå i samma anrop.
indata = dict(G=10, Q=[2, 4], psi_0=[0.7, 0.6],
              psi_1=[0.5, 0.2], psi_2=[0.3, 0.1])


if __name__ == "__main__":
    # Tabellen: egentyngd, trafik, vind och temperatur.
    # gamma_G=1.35, gamma_Q=1.5, xi=0.89 och gamma_d=1.
    # Ursprunglig 6.10a med reducerade variabla laster.
    # M och N redovisas per samma huvudlastfall vid samtidig kontroll.
    for namn, g, q, enhet in (
        ("Moment M", 150, [225, 10, 35], "kNm"),
        ("Normalkraft N", 100, [55, 2, 70], "kN"),
    ):
        print(f"\n{namn}: Q_1 = trafik, Q_2 = vind, Q_3 = temperatur")
        Lastkomb.skriv_formler(
            G=g, Q=q, psi_0=[0.4, 0.3, 0.6],
            variabel_i_610a=True, enhet=enhet,
        )

    # 6.11: välj huvudlastens faktor enligt aktuell olyckssituation.
    Lastkomb.skriv_formler(**indata, kombination="6.11", A_d=5,
                          olycka_huvudlast="psi_1", enhet="kN/m")

    # 6.12: A_Ed är redan dimensionerande jordbävningseffekt.
    Lastkomb.skriv_formler(**indata, kombination="6.12", A_Ed=5, enhet="kN/m")

    # 6.14 karakteristisk, 6.15 frekvent, 6.16 kvasipermanent.
    for nummer in ("6.14", "6.15", "6.16"):
        Lastkomb.skriv_formler(**indata, kombination=nummer, enhet="kN/m")

    # Samma indata kan användas för beräkning utan utskrift.
    resultat = Lastkomb.lastkomb(**indata, kombination="6.15")
    print(resultat["dimensionerande"])

    # 6.13: kontrollera en beräknad deformation mot dess gräns, båda i mm.
    # Lastkombinationens kN/m måste först omsättas till deformation med en modell.
    kontroll = Lastkomb.kontroll_613(E_d=12, C_d=15, skriv=True, enhet="mm")
