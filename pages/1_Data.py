import streamlit as st
from muat import muat_data

st.title("Data")
KOLOM_WAJIB = ["reviewId", "teks_asli", "teks_bersih", "score",
               "thumbsUpCount", "at", "sentimen", "tema"]

try:
    df = muat_data()
except FileNotFoundError:
    st.error("Berkas data/clean/ulasan_bersih.csv belum ada. "
             "Jalankan pengambilan awal terlebih dahulu.")
    st.stop()

hilang = [k for k in KOLOM_WAJIB if k not in df.columns]
if hilang:
    st.error(f"Kolom wajib tidak ditemukan: {', '.join(hilang)}")
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Jumlah ulasan", f"{len(df):,}")
c2.metric("Ulasan paling lama", str(df["at"].min().date()))
c3.metric("Ulasan paling baru", str(df["at"].max().date()))

st.subheader("Sebaran rating")
st.bar_chart(df["score"].value_counts().sort_index())

st.subheader("Pratinjau data")
st.dataframe(df[["at", "score", "thumbsUpCount", "teks_asli", "teks_bersih"]].head(100))

st.caption("Duplikat (ID ulasan sama) dan teks kosong sudah dibuang saat "
           "pembersihan. Nama pengguna tidak disimpan.")