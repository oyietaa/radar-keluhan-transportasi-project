import json
from pathlib import Path
from bot.engine import ChatbotEngine

BASE = Path(__file__).resolve().parent.parent
TEMA = json.loads((Path(__file__).parent / "tema_bot.json").read_text(encoding="utf-8"))
ENGINE = ChatbotEngine(TEMA)

def _baca(*bagian):
    return json.loads(Path(BASE, *bagian).read_text(encoding="utf-8"))

def h_sentimen():
    r = _baca("ringkasan.json")
    p = r["persen_sentimen"]
    return (f"Dari {r['total_ulasan']:,} ulasan (prediksi model): positif {p['positif']}%, "
            f"netral {p['netral']}%, negatif {p['negatif']}%.")

def h_tema():
    r = _baca("ringkasan.json")
    urut = sorted(r["jumlah_per_tema"].items(), key=lambda x: -x[1])
    teks = f"Tema terbesar: {urut[0][0]} ({urut[0][1]:,} ulasan)"
    if len(urut) > 1:
        teks += f", disusul {urut[1][0]} ({urut[1][1]:,} ulasan)"
    return teks + f". Ada juga {r['ulasan_singkat']:,} ulasan singkat yang tidak ikut clustering."

def h_rating():
    return f"Rata-rata rating {_baca('ringkasan.json')['rata_rata_rating']} dari 5."

def h_jumlah():
    r = _baca("ringkasan.json")
    return f"Ada {r['total_ulasan']:,} ulasan yang dianalisis."

def h_status():
    try:
        log = _baca("log_pipeline.json")[-1]
    except (FileNotFoundError, IndexError):
        r = _baca("ringkasan.json")
        return (f"Belum ada catatan pipeline otomatis. Data terakhir dihitung "
                f"pada {r['diperbarui']}.")
    return (f"Pembaruan terakhir {log['waktu']}: {log['status']}, "
            f"{log['baru']} ulasan baru.")

def h_mae():
    m = _baca("models", "metrik.json")
    return (f"MAE adalah rata-rata selisih mutlak tebakan dan nilai asli 'membantu'. "
            f"MAE model {m['regresi_mae']}, sedangkan selalu menebak 0 memberi "
            f"{m['mae_tebak_nol']}, jadi model tidak lebih baik dari tebakan sederhana.")

def h_r2():
    m = _baca("models", "metrik.json")
    return (f"R2 menunjukkan seberapa baik model menjelaskan data. Nilai model "
            f"{m['regresi_r2']}, mendekati 0, artinya tidak lebih baik daripada "
            f"menebak rata-rata. Nilai negatif berarti lebih buruk dari rata-rata.")

DINAMIS = {"sentimen": h_sentimen, "tema": h_tema, "rating": h_rating,
           "jumlah_data": h_jumlah, "status_pipeline": h_status,
           "arti_mae": h_mae, "arti_r2": h_r2}

def jawab(pesan):
    hasil = ENGINE.reply(pesan)
    fungsi = DINAMIS.get(hasil["intent"])
    if fungsi is not None:
        try:
            hasil["reply"] = fungsi()
        except FileNotFoundError:
            hasil["reply"] = "Data ringkasan belum tersedia. Jalankan pipeline terlebih dahulu."
    return hasil