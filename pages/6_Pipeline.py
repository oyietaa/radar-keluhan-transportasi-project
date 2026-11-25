import json
import pandas as pd
import plotly.express as px
import streamlit as st
import tampilan as t
from config import JUMLAH_JADWAL, LOG, RETENSI_BULAN, RETENSI_MAKS

t.siapkan("Pipeline", "⚙️")
st.title("Pipeline otomatis")
st.markdown(
    "Skrip Python dijalankan terjadwal oleh GitHub Actions, tanpa laptop menyala. Setiap kali jalan: "
    "ambil ulasan terbaru, bersihkan, tambahkan hanya ulasan baru (dicek lewat ID ulasan), tebak "
    "sentimen dan tema, terapkan batas simpan, perbarui ringkasan, lalu kirim pesan ke Telegram.")
try:
    log = pd.DataFrame(json.loads(LOG.read_text(encoding="utf-8")))
except FileNotFoundError:
    st.info("Belum ada catatan pipeline.")
    st.stop()
log["waktu"] = pd.to_datetime(log["waktu"])
berhasil = int((log["status"] == "berhasil").sum())
gagal = int((log["status"] == "gagal").sum())
t.papan([
    (t.angka(len(log)), "catatan terakhir", t.WARNA["baja"]),
    (t.angka(berhasil), "berhasil", t.WARNA["hijau"]),
    (t.angka(gagal), "gagal", t.WARNA["merah"]),
    (t.angka(log["baru"].sum()), "ulasan baru tercatat", t.WARNA["rel"]),
])
st.caption(f"Setiap jalan mengambil {JUMLAH_JADWAL} ulasan terbaru. Batas simpan: "
           f"{RETENSI_BULAN} bulan atau {t.angka(RETENSI_MAKS)} ulasan.")

st.subheader("Ulasan baru pada tiap pembaruan")
f = px.scatter(log, x="waktu", y="baru", color="status",
               color_discrete_map={"berhasil": t.WARNA["hijau"], "gagal": t.WARNA["merah"]},
               hover_data=["pesan"], labels={"waktu": "Waktu", "baru": "Ulasan baru"})
f.update_traces(marker_size=13)
st.plotly_chart(t.gaya(f, 320))
st.caption("Semua waktu dalam WIB. Dua catatan awal dari GitHub Actions semula tercatat UTC dan sudah dikoreksi ke WIB. "
           "Catatan awal mencakup uji coba, termasuk uji kegagalan dengan internet dimatikan. "
           "Log hanya menyimpan 50 catatan terakhir.")
st.dataframe(log.iloc[::-1], hide_index=True)