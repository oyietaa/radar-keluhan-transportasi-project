import pandas as pd
import streamlit as st
from muat import muat_data, muat_ringkasan

st.set_page_config(page_title="Radar Keluhan Access by KAI", layout="wide")
st.title("Radar Keluhan Access by KAI")
st.caption("Analisis ulasan Google Play Store: sentimen, tema keluhan, dan regresi.")

try:
    df = muat_data()
    r = muat_ringkasan()
except FileNotFoundError as e:
    st.error(f"Berkas data belum ada: {e.filename}. Jalankan pipeline terlebih dahulu.")
    st.stop()

p = r["persen_sentimen"]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Jumlah ulasan", f"{r['total_ulasan']:,}")
k2.metric("Rata-rata rating", r["rata_rata_rating"])
k3.metric("Negatif (prediksi)", f"{p['negatif']}%")
k4.metric("Positif (prediksi)", f"{p['positif']}%")

st.write(f"Data diperbarui: **{r['diperbarui']}** | "
         f"ulasan baru pada pembaruan terakhir: **{r['ulasan_baru']}**")
st.caption("Waktu pembaruan otomatis dari GitHub memakai UTC (WIB = UTC + 7 jam).")

kiri, kanan = st.columns(2)

with kiri:
    st.subheader("Sentimen: prediksi model dan menurut rating")
    urutan = ["positif", "netral", "negatif"]
    banding = pd.DataFrame({
        "prediksi model (%)": (df["sentimen"].value_counts(normalize=True) * 100)
                              .reindex(urutan).round(1),
        "menurut rating (%)": (df["sentimen_rating"].value_counts(normalize=True) * 100)
                              .reindex(urutan).round(1),
    })
    st.bar_chart(banding)
    st.caption("Model dilatih dari rating bintang, jadi keduanya mirip tetapi tidak sama. "
               "Angka menurut rating adalah label yang menjadi target pelatihan.")

with kanan:
    st.subheader("Tema keluhan (ulasan 4 kata atau lebih)")
    st.bar_chart(pd.Series(r["jumlah_per_tema"]))
    st.caption(f"{r['ulasan_singkat']:,} ulasan yang lebih pendek tidak ikut "
               "pengelompokan tema.")

st.info("Gunakan menu di sebelah kiri untuk membuka halaman lain.")