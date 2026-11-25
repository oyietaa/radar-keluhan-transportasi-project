import json
from datetime import datetime, timedelta, timezone
import pandas as pd
from config import CLEAN_CSV, RAW_DIR, RINGKASAN, LOG, JUMLAH_JADWAL
from pipeline.ambil import ambil
from pipeline.bersihkan import bersihkan_df
from pipeline.prediksi import tambah_prediksi
from pipeline.retensi import terapkan_retensi, bersihkan_raw
from pipeline.ringkasan import buat_ringkasan, pesan_ringkas
from pipeline.telegram import kirim

WIB = timezone(timedelta(hours=7))

def sekarang():
    return datetime.now(WIB).replace(tzinfo=None)

def tulis_log(status, baru, pesan=""):
    log = json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else []
    log.append({"waktu": sekarang().isoformat(timespec="seconds"),
                "status": status, "baru": baru, "pesan": pesan})
    LOG.write_text(json.dumps(log[-50:], ensure_ascii=False, indent=2),
                   encoding="utf-8")

def main():
    try:
        mentah = ambil(JUMLAH_JADWAL)
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        nama = f"mentah_{sekarang():%Y-%m-%d_%H%M}.csv"
        mentah.to_csv(RAW_DIR / nama, index=False)
        lama = pd.read_csv(CLEAN_CSV, parse_dates=["at"])
        bersih = bersihkan_df(mentah)
        baru = bersih[~bersih["reviewId"].isin(lama["reviewId"])]
        if len(baru):
            baru = tambah_prediksi(baru)
            semua = pd.concat([lama, baru], ignore_index=True)
        else:
            semua = lama
        semua = terapkan_retensi(semua)
        semua.to_csv(CLEAN_CSV, index=False)
        bersihkan_raw()
        ringkas = buat_ringkasan(semua, len(baru))
        RINGKASAN.write_text(json.dumps(ringkas, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        tulis_log("berhasil", len(baru))
        kirim(pesan_ringkas(ringkas))
        print("Selesai:", len(baru), "ulasan baru;", len(semua), "ulasan total")
    except Exception as e:
        tulis_log("gagal", 0, str(e))
        kirim(f"Pengambilan gagal: {e}")
        raise

if __name__ == "__main__":
    main()