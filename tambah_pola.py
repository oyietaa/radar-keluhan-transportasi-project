import json
from pathlib import Path

BERKAS = Path("bot") / "tema_bot.json"
TAMBAHAN = {
    "perpisahan": ["sampai bertemu", "sampai nanti", "pamit dulu", "cukup dulu"],
    "identitas": ["ini bot apa", "fungsi bot ini", "bot bisa bantu apa saja",
                  "kamu bisa bantu apa"],
    "sentimen": ["sentimen", "komposisi sentimen", "gambaran sentimen",
                 "puas atau kecewa", "persen sentimen netral",
                 "persen sentimen negatif"],
    "tema": ["keluhan paling sering", "tema paling besar", "tema dominan",
             "keluhan sering muncul", "topik keluhan"],
    "rating": ["skor rata rata", "nilai rata rata aplikasi"],
    "jumlah_data": ["besar dataset", "jumlah baris data", "berapa baris"],
    "arti_r2": ["r2 artinya", "r kuadrat negatif"],
    "keterbatasan": ["apa kelemahan model", "keterbatasan analisis",
                     "hasil ini bisa akurat", "batasan analisis"],
}

data = json.loads(BERKAS.read_text(encoding="utf-8"))
for intent in data["intents"]:
    for pola in TAMBAHAN.get(intent["tag"], []):
        if pola not in intent["patterns"]:
            intent["patterns"].append(pola)
BERKAS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("pola ditambahkan")