# KTHBYGG mot RustyFEM – 15 jämförelsefall

Körbar fil: `C:\Users\GTSA - Infinity\Desktop\RustyFEM\target\release\rustyfem.exe`

Tolerans per grupp: 1e-7 × största referensvärdet + absolut tolerans (1e-9 för förskjutning/rotation, 1e-6 för krafter/moment). Enheter kN, m, rad.

| Fall | Status | Max absolut förskjutnings-/rotationsfel | Max absolut reaktionsfel | Max absolut N/M-fel |
|---|---|---:|---:|---:|
| 01_konsol_punktlast | PASS | 4.34e-19 | 1.78e-15 | 1.8e-09 |
| 02_konsol_moment | PASS | 0 | 1.78e-15 | 1.78e-15 |
| 03_fritt_upplagd | PASS | 1.08e-19 | 3.55e-15 | 4.55e-09 |
| 04_fast_fast_jamn_last | PASS | 0 | 0 | nan |
| 05_konsol_triangellast | PASS | 8.67e-19 | 7.11e-15 | nan |
| 06_kontinuerlig_tva_fack | PASS | 1.36e-20 | 8.88e-16 | nan |
| 07_olika_EI_EA | PASS | 3.33e-13 | 1.42e-13 | 8.98e-10 |
| 08_pelare | PASS | 4.34e-19 | 7.11e-15 | 1.8e-09 |
| 09_sned_konsol | PASS | 3.33e-13 | 2.84e-14 | 4.27e-09 |
| 10_portal_snett_tak | PASS | 4.35e-14 | 2.83e-09 | 3.01e-09 |
| 11_translationsfjadrar | PASS | 4.78e-13 | 3.91e-09 | 3.04e-09 |
| 12_rotationsfjader | PASS | 1.39e-17 | 6.39e-14 | 1.8e-09 |
| 13_fri_varmeutvidgning | PASS | 2.17e-19 | 0 | nan |
| 14_fastlast_uppvarmning | PASS | 0 | 3.55e-15 | nan |
| 15_L_ram_lokala_laster | PASS | 3.33e-12 | 3.13e-13 | nan |

B23 används för mekaniska fall. B21 används för jämn temperatur, där skjuvdeformation inte påverkar lösningen. Temperaturerna skickas som *TEMPERATURE och *EXPANSION, inte som ekvivalenta laster.

Triangellasten jämförs via oberoende Gauss-integrerade nodlaster. Det fallet verifierar nodlösningen och reaktionerna, inte RustyFEM:s hantering av en inbyggd triangellast.

N och M jämförs i tre integrationspunkter per olastat B23-element. Utbrett lastade elements snittkrafter samt temperaturfallens snittkrafter ingår inte i denna jämförelse. RustyFEM B23 rapporterar inte tvärkraft; V kontrolleras separat analytiskt. nan betyder ej jämfört.

Temperaturgradient genom balktvärsnitt stöds inte i den installerade RustyFEM-koden. Gradientfallet verifieras därför analytiskt i test_ram_solver.py, inte mot RustyFEM.

Extra diagnostik: både avkylning mot axialfjäder och fri avkylning av sned stång gav konvergensfel i RustyFEM (15_avkylning_mot_fjader och 15_avkylning_sned_stang, .inp och .log). Dessa räknas inte som godkända jämförelsefall. Fall 15 i tabellen är istället en L-ram med lokala utbredda laster. Avkylning och temperatur + fjäder verifieras analytiskt i KTHBYGG.
