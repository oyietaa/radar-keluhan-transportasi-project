import json
from datetime import datetime
from pathlib import Path
from bot.engine import ChatbotEngine
from config import RETENSI_BULAN, RETENSI_MAKS

BASE = Path(__file__).resolve().parent.parent
TEMA = json.loads((Path(__file__).parent / "tema_bot.json").read_text(encoding="utf-8"))
ENGINE = ChatbotEngine(TEMA)
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

def _baca(*bagian):
    return json.loads(Path(BASE, *bagian).read_text(encoding="utf-8"))

def _angka(x, desimal=0):
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def _waktu(teks):
    try:
        d = datetime.fromisoformat(teks)
    except (TypeError, ValueError):
        return str(teks)
    return f"{d.day} {BULAN[d.month - 1]} {d.year} pukul {d:%H.%M} WIB"

def h_sentimen():
    r = _baca("ringkasan.json")
    p = r["persen_sentimen"]
    return (f"Dari {_angka(r['total_ulasan'])} ulasan (prediksi model): positif "
            f"{_angka(p['positif'], 1)}%, netral {_angka(p['netral'], 1)}%, "
            f"negatif {_angka(p['negatif'], 1)}%.")

def h_tema():
    r = _baca("ringkasan.json")
    urut = sorted(r["jumlah_per_tema"].items(), key=lambda x: -x[1])
    teks = f"Tema terbesar: {urut[0][0]} ({_angka(urut[0][1])} ulasan)"
    if len(urut) > 1:
        teks += f", disusul {urut[1][0]} ({_angka(urut[1][1])} ulasan)"
    return teks + f". Ada juga {_angka(r['ulasan_singkat'])} ulasan singkat yang tidak ikut clustering."

def h_rating():
    return f"Rata-rata rating {_angka(_baca('ringkasan.json')['rata_rata_rating'], 2)} dari 5."

def h_jumlah():
    return f"Ada {_angka(_baca('ringkasan.json')['total_ulasan'])} ulasan yang dianalisis."

def h_status():
    try:
        log = _baca("log_pipeline.json")[-1]
    except (FileNotFoundError, IndexError):
        r = _baca("ringkasan.json")
        return f"Belum ada catatan pipeline otomatis. Data terakhir dihitung pada {_waktu(r['diperbarui'])}."
    teks = f"Pembaruan terakhir {_waktu(log['waktu'])}: {log['status']}, {log['baru']} ulasan baru."
    if log["status"] == "gagal" and log.get("pesan"):
        teks += f" Penyebab: {log['pesan']}"
    return teks

def h_mae():
    m = _baca("models", "metrik.json")
    return (f"MAE adalah rata-rata selisih mutlak tebakan dan nilai asli 'membantu'. MAE model "
            f"{_angka(m['regresi_mae'], 2)}, sedangkan selalu menebak 0 memberi "
            f"{_angka(m['mae_tebak_nol'], 2)}.")

def h_r2():
    m = _baca("models", "metrik.json")
    return (f"R2 menunjukkan seberapa baik model menjelaskan data. Nilai model "
            f"{_angka(m['regresi_r2'], 3)}. Nilai mendekati 0 berarti tidak lebih baik daripada "
            f"menebak rata-rata, dan nilai negatif berarti lebih buruk dari rata-rata.")

def h_regresi():
    m = _baca("models", "metrik.json")
    banding = ("tidak lebih baik daripada" if m["regresi_mae"] >= m["mae_tebak_nol"]
               else "lebih baik daripada")
    return (f"Model regresi (jumlah kata dan rating) {banding} menebak 0 untuk semua ulasan: "
            f"MAE {_angka(m['regresi_mae'], 2)} melawan {_angka(m['mae_tebak_nol'], 2)}, "
            f"R2 {_angka(m['regresi_r2'], 3)}. {_angka(m['persen_membantu_nol'], 1)}% ulasan memang "
            f"tidak punya 'membantu', dan faktor lain di luar dua fitur itu kemungkinan lebih berpengaruh.")

def h_masa_simpan():
    return (f"Data disimpan paling lama {RETENSI_BULAN} bulan atau paling banyak "
            f"{_angka(RETENSI_MAKS)} ulasan, mana yang tercapai lebih dulu. Ulasan yang lebih lama "
            f"dihapus otomatis oleh pipeline, dan berkas mentah yang lebih dari 60 hari juga dihapus.")

def h_daftar_tema():
    r = _baca("ringkasan.json")
    urut = sorted(r["jumlah_per_tema"].items(), key=lambda x: -x[1])
    daftar = "; ".join(f"{n} ({_angka(j)})" for n, j in urut)
    return (f"Tema yang ditemukan: {daftar}. Ulasan yang lebih pendek dari 4 kata "
            f"({_angka(r['ulasan_singkat'])} ulasan) tidak dikelompokkan.")

DINAMIS = {"sentimen": h_sentimen, "tema": h_tema, "rating": h_rating,
           "jumlah_data": h_jumlah, "status_pipeline": h_status,
           "arti_mae": h_mae, "arti_r2": h_r2, "hasil_regresi": h_regresi,
           "masa_simpan": h_masa_simpan, "daftar_tema": h_daftar_tema}

def jawab(pesan):
    hasil = ENGINE.reply(pesan)
    fungsi = DINAMIS.get(hasil["intent"])
    if fungsi is not None:
        try:
            hasil["reply"] = fungsi()
        except FileNotFoundError:
            hasil["reply"] = "Data ringkasan belum tersedia. Jalankan pipeline terlebih dahulu."
    return hasil