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

st.subheader("Sentimen (prediksi model)")
st.bar_chart(df["sentimen"].value_counts())
st.info("Gunakan menu di sebelah kiri untuk membuka halaman lain.")