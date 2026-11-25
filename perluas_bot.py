import json
from pathlib import Path

BERKAS = Path("bot") / "tema_bot.json"

TAMBAH_POLA = {
    "tema": ["tema ulasan terbanyak", "kategori keluhan utama", "kelompok keluhan terbesar"],
    "rating": ["rata rata ulasan", "rata rata penilaian pengguna", "bintang rata rata aplikasi"],
    "status_pipeline": ["pipeline sudah jalan", "pipeline otomatis berhasil",
                        "kapan pembaruan terakhir berjalan"],
}
INTENT_BARU = [
    {"tag": "sumber_data",
     "patterns": ["data ini dari mana", "sumber data ulasan", "dari mana datanya berasal",
                  "asal data ulasan", "data berasal dari platform apa"],
     "responses": ["Data berupa ulasan pengguna aplikasi Access by KAI di Google Play Store, "
                   "diambil dengan pustaka google-play-scraper. Nama pengguna tidak disimpan."]},
    {"tag": "cara_pipeline",
     "patterns": ["bagaimana pipeline bekerja", "cara kerja pembaruan otomatis",
                  "jelaskan alur pengambilan data", "apa itu pipeline",
                  "langkah pengambilan data otomatis"],
     "responses": ["Pipeline adalah skrip Python yang dijalankan GitHub Actions: mengambil ulasan "
                   "terbaru, membersihkan teks, menambahkan hanya ulasan baru (dicek lewat ID ulasan), "
                   "menebak sentimen dan tema dengan model yang sudah dilatih, menerapkan batas simpan, "
                   "memperbarui ringkasan, lalu mengirim pesan ke Telegram."]},
    {"tag": "jadwal_pipeline",
     "patterns": ["setiap berapa hari data diambil", "jadwal pembaruan data",
                  "seberapa sering data diperbarui", "berapa kali pipeline jalan",
                  "frekuensi pengambilan ulasan"],
     "responses": ["Pembaruan dijadwalkan setiap 3 hari (pukul 07.00 WIB pada tanggal 1, 4, 7, dan "
                   "seterusnya tiap bulan), dengan 500 ulasan terbaru per pengambilan. Pelaksanaan "
                   "bisa tertunda beberapa jam."]},
    {"tag": "masa_simpan",
     "patterns": ["data disimpan berapa lama", "batas simpan data", "kebijakan retensi data",
                  "berapa lama ulasan disimpan", "ulasan lama dihapus kapan"],
     "responses": ["(dinamis)"]},
    {"tag": "hasil_regresi",
     "patterns": ["apakah regresinya bagus", "hasil regresi bagaimana", "seberapa baik model regresi",
                  "regresi bisa memperkirakan membantu", "kesimpulan regresi"],
     "responses": ["(dinamis)"]},
    {"tag": "daftar_tema",
     "patterns": ["sebutkan semua tema keluhan", "ada tema apa saja", "apa saja tema ulasan",
                  "daftar tema", "tema apa yang ditemukan"],
     "responses": ["(dinamis)"]},
]

data = json.loads(BERKAS.read_text(encoding="utf-8"))
per_tag = {i["tag"]: i for i in data["intents"]}
for tag, pola in TAMBAH_POLA.items():
    for p in pola:
        if p not in per_tag[tag]["patterns"]:
            per_tag[tag]["patterns"].append(p)
for baru in INTENT_BARU:
    if baru["tag"] not in per_tag:
        data["intents"].append(baru)
BERKAS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(data["intents"]), "intent")