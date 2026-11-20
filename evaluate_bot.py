import csv
import sys
from bot.jawab import ENGINE

berkas = sys.argv[1] if len(sys.argv) > 1 else "evaluasi_bot.csv"
with open(berkas, encoding="utf-8") as f:
    data = [(r["kalimat"], r["intent"]) for r in csv.DictReader(f)]

hasil = []
for kalimat, harapan in data:
    tebakan, skor = ENGINE.classify(kalimat)
    hasil.append((kalimat, harapan, tebakan or "fallback", skor))

benar = sum(1 for _, h, t, _ in hasil if h == t)
print(f"Berkas {berkas}")
print(f"Akurasi: {benar}/{len(hasil)} = {benar / len(hasil):.1%}")
for kalimat, harapan, tebakan, skor in hasil:
    if harapan != tebakan:
        print(f'- "{kalimat}" -> {tebakan} ({skor:.2f}), seharusnya {harapan}')