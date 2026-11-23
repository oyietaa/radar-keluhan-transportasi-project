import json
import pandas as pd
import streamlit as st
from config import JUMLAH_JADWAL, LOG, RETENSI_BULAN, RETENSI_MAKS

st.title("Pipeline Otomatis")
st.markdown(
    "Skrip Python dijalankan terjadwal oleh GitHub Actions, tanpa laptop menyala. "
    "Setiap kali jalan: ambil ulasan terbaru, bersihkan, tambahkan hanya ulasan baru "
    "(dicek lewat ID ulasan), tebak sentimen dan tema, terapkan batas simpan, "
    "perbarui ringkasan, lalu kirim pesan ke Telegram."
)
c1, c2, c3 = st.columns(3)
c1.metric("Ulasan diambil per jalan", JUMLAH_JADWAL)
c2.metric("Batas umur data", f"{RETENSI_BULAN} bulan")
c3.metric("Batas jumlah data", f"{RETENSI_MAKS:,}")

try:
    log = pd.DataFrame(json.loads(LOG.read_text(encoding="utf-8")))
except FileNotFoundError:
    st.info("Belum ada catatan pipeline.")
    st.stop()

st.subheader("Riwayat pipeline")
berhasil = int((log["status"] == "berhasil").sum())
gagal = int((log["status"] == "gagal").sum())
st.write(f"{len(log)} catatan terakhir. Berhasil: {berhasil}, gagal: {gagal}. "
         "Catatan awal mencakup uji coba, termasuk uji kegagalan dengan internet dimatikan.")
st.dataframe(log.iloc[::-1], hide_index=True)

st.subheader("Ulasan baru per pembaruan")
st.bar_chart(log.set_index("waktu")["baru"])
st.caption("Catatan dari laptop memakai WIB, catatan dari GitHub Actions memakai UTC "
           "(WIB = UTC + 7 jam). Log hanya menyimpan 50 catatan terakhir.")