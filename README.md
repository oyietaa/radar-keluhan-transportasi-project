# Radar Keluhan Access by KAI

Dashboard Streamlit untuk menganalisis ulasan aplikasi **Access by KAI** di Google Play Store (sentimen, tema keluhan, regresi), dilengkapi asisten bot di dalam dashboard dan **pipeline otomatis** yang memperbarui data setiap 3 hari lewat GitHub Actions.

- Nama: [isi nama]
- NIM: [isi NIM]
- Project akhir mandiri, digabung untuk dua mata kuliah: **Aplikasi Web** dan **Scripting Language**.
- Repositori: https://github.com/oyietaa/radar-keluhan-transportasi-project

## Pembagian klaim

| Mata kuliah | Bagian project |
|---|---|
| Aplikasi Web | Dashboard Streamlit multipage (6 halaman, filter interaktif, grafik Plotly), analisis sentimen, clustering tema keluhan, regresi, dan asisten bot di dashboard |
| Scripting Language | Pipeline otomatis: pengambilan ulasan, pembersihan, penambahan ulasan baru tanpa duplikat, prediksi, batas simpan data, penjadwalan GitHub Actions, notifikasi Telegram, dan catatan kegagalan |

## Fitur dashboard

| Halaman | Isi |
|---|---|
| Beranda | Ringkasan, tren ulasan per minggu menurut sentimen, tema keluhan |
| Data | Sebaran rating dan panjang ulasan, pratinjau, unduh CSV, catatan pembersihan |
| Sentimen | Komposisi, perbandingan rating dan prediksi, kinerja model, pemeriksaan manual 20 ulasan |
| Tema Keluhan | Ukuran tema, kata dominan, contoh ulasan, keterbatasan |
| Regresi | MAE dan R², grafik aktual-prediksi, formulir estimasi |
| Tanya Bot | Asisten percakapan yang menjawab dari hasil analisis |
| Pipeline | Riwayat pembaruan otomatis |

Filter tanggal, sentimen, dan tema di sidebar berlaku pada Beranda, Data, Sentimen, dan Tema Keluhan. Halaman Regresi memakai data awal yang tetap.

## Cara menjalankan

Butuh Python 3.10 atau lebih baru (dikembangkan dengan Python 3.13).

```
git clone https://github.com/oyietaa/radar-keluhan-transportasi-project.git
cd radar-keluhan-transportasi-project
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS/Linux
python -m pip install -r requirements.txt
streamlit run app.py
```

Dashboard terbuka di `http://localhost:8501`. Dashboard hanya membaca berkas yang sudah ada di repo, jadi tidak perlu internet atau akun apa pun (kecuali untuk memuat huruf dari Google Fonts, yang bersifat kosmetik).

Perintah lain:

| Tujuan | Perintah |
|---|---|
| Menjalankan tes | `python -m pytest -q` |
| Menjalankan pipeline sekali (butuh internet) | `python -m pipeline.jalankan` |
| Mengukur akurasi bot | `python evaluate_bot.py evaluasi_bot_c.csv` |
| Memeriksa konsistensi data dan model | `python audit.py` |
| Melatih ulang model | `python latih_model.py --yakin` |

Peringatan: melatih ulang model mengubah nomor cluster, sehingga `models/tema.json` harus dibuat ulang dengan membaca hasil cluster yang baru. Karena itu skrip meminta `--yakin`.

## Pipeline otomatis

Workflow `.github/workflows/pipeline.yml` berjalan terjadwal (`0 0 */3 * *`, yaitu 00.00 UTC atau 07.00 WIB pada tanggal 1, 4, 7, dan seterusnya) dan dapat dijalankan manual dari tab Actions. Tiap jalan:

1. Mengambil 500 ulasan terbaru dari Play Store dan menyimpan salinan mentah di `data/raw/`.
2. Membersihkan teks dan membuang duplikat berdasarkan ID ulasan.
3. Hanya memproses ulasan yang belum ada di `data/clean/`.
4. Menebak sentimen dan tema dengan model yang sudah dilatih (tanpa dilatih ulang).
5. Menerapkan batas simpan: paling lama 6 bulan atau 10.000 ulasan.
6. Memperbarui `ringkasan.json` dan `log_pipeline.json`, lalu menyimpannya ke repo.
7. Mengirim ringkasan ke Telegram. Bila pengambilan gagal (termasuk hasil kosong), status `gagal` dicatat dan pesan kegagalan dikirim.

Pengaturan di GitHub: **Settings > Secrets and variables > Actions**, buat `TELEGRAM_TOKEN` dan `TELEGRAM_CHAT_ID`; lalu **Settings > Actions > General > Workflow permissions**, pilih Read and write permissions. Token tidak pernah disimpan di kode.

## Hasil utama

Data awal: 3.000 ulasan diambil, 2.987 tersisa setelah pembersihan (rentang 23 Juli sampai 18 November 2026). Data bertambah otomatis setelah itu.

| Analisis | Metode | Hasil |
|---|---|---|
| Sentimen | TF-IDF + Logistic Regression, label dari rating (1-2 negatif, 3 netral, 4-5 positif), data uji 20% (598 ulasan) | Akurasi 81,6%; F1 positif 0,91, negatif 0,79, netral 0,15 |
| Tema keluhan | TF-IDF + K-Means (K = 4) pada ulasan 4 kata atau lebih (1.785 ulasan) | Empat tema; dua tema pujian dan dua tema keluhan yang masih tumpang tindih |
| Regresi | Linear Regression: jumlah kata dan rating untuk jumlah "membantu", data uji 20% | MAE 1,29 (menebak 0: 0,923); R² mendekati 0 (-0,003) |
| Pemeriksaan manual | 20 ulasan acak dari data uji | Manual vs rating 15/20; manual vs model 12/20; rating vs model 13/20 |
| Bot | Berbasis aturan (kemiripan kata), diukur dengan kalimat uji baru | Set C (41 kalimat): 82,9% |

Rincian pengukuran bot: set A (67 kalimat) 71,6% sebelum perbaikan; set B (28 kalimat) 89,3% sebagai uji baru; set C (41 kalimat) 82,9% sebagai pengukuran akhir. Perbaikan dibuat dari kesalahan set A dan B, sehingga hanya angka sebelum perbaikan dan set C yang dilaporkan sebagai kinerja.

## Struktur berkas

```
app.py, pages/            dashboard Streamlit
tampilan.py, muat.py      tema tampilan dan pemuat data
bot/                      mesin bot, basis pengetahuan (tema_bot.json), jawaban dinamis
pipeline/                 skrip pengambilan, pembersihan, prediksi, retensi, Telegram
latih_model.py            pelatihan model (manual)
data/raw, data/clean      data mentah dan data bersih
data/data_latih_awal.csv  data latih yang dibekukan (2.987 ulasan)
models/                   model dan metrik
tests/                    tes otomatis
evaluasi_*.csv            kalimat uji bot dan hasil pemeriksaan manual sentimen
.github/workflows/        jadwal pipeline
```

Skrip sekali pakai yang dipertahankan sebagai bukti proses: `tambah_pola.py`, `perluas_bot.py`, `perbaiki_log.py`, `nilai_manual.py`, `cek_regresi.py`, `cek_panjang.py`.

## Keterbatasan

- Label sentimen berasal dari rating, bukan penilaian manual, sehingga model meniru rating dan bukan "kebenaran" sentimen. Kelas netral paling lemah (F1 0,15).
- Pemeriksaan manual hanya 20 ulasan dan tidak mewakili seluruh data.
- Regresi tidak lebih baik daripada menebak 0 karena sekitar 88,6% ulasan tidak punya "membantu" dan ada beberapa nilai ekstrem. Regresi linear juga dapat menghasilkan estimasi negatif.
- Clustering memakai kata (TF-IDF), bukan makna; dua tema keluhan tumpang tindih dan satu tema berisi separuh ulasan.
- Hasil hanya berlaku untuk sampel ulasan yang diambil (sekitar empat bulan terakhir), bukan seluruh pengguna.
- Bot berbasis aturan hanya memahami kosakata yang mirip dengan polanya; penambahan intent baru pernah menurunkan satu kalimat uji lama.
- Jadwal GitHub Actions dapat tertunda beberapa jam (teramati sekitar 6 jam). Dua catatan log awal dari GitHub semula bercap UTC dan sudah dikoreksi ke WIB.
- Kalimat uji bot disusun dengan bantuan AI dan belum diuji oleh pengguna lain.

## Data dan etika

Data berupa ulasan publik Play Store, diambil dengan pustaka `google-play-scraper`. Nama pengguna tidak disimpan. Data hanya dipakai untuk keperluan tugas dan tidak untuk disebarkan.

## Sumber dan kredit

- Pustaka: Streamlit, Plotly, pandas, scikit-learn, joblib, google-play-scraper, requests, pytest.
- Mesin bot (praproses, skor kemiripan gabungan Jaccard, kemiripan karakter, dan cakupan, serta ambang) diadaptasi dari modul praktikum "Membangun Chatbot Tematik dengan Flask" pada mata kuliah Aplikasi Web.
- Analisis sentimen dan K-Means dikembangkan dari praktikum analisis sentimen dan crawling dan NLP pada mata kuliah yang sama.
- Huruf: Plus Jakarta Sans (Google Fonts).
- Bantuan AI: kode, desain, dan dokumen dikembangkan dengan bantuan Claude (Anthropic). Seluruh kode dijalankan dan hasilnya diperiksa oleh pemilik project.