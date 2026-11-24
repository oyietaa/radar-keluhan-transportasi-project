import plotly.express as px
import streamlit as st
import tampilan as t
from muat import muat_data

t.siapkan("Data", "🗂️")
KOLOM_WAJIB = ["reviewId", "teks_asli", "teks_bersih", "score",
               "thumbsUpCount", "at", "sentimen", "tema"]
try:
    semua = muat_data()
except FileNotFoundError:
    st.error("Berkas data/clean/ulasan_bersih.csv belum ada. "
             "Jalankan pengambilan awal terlebih dahulu.")
    st.stop()
hilang = [k for k in KOLOM_WAJIB if k not in semua.columns]
if hilang:
    st.error(f"Kolom wajib tidak ditemukan: {', '.join(hilang)}")
    st.stop()

df = t.filter_sidebar(semua, "data")
df = df.assign(kata=df["teks_asli"].str.split().str.len())

st.title("Data ulasan")
t.papan([
    (t.angka(len(df)), "ulasan terpilih", t.WARNA["baja"]),
    (str(df["at"].min().date()), "ulasan paling lama", t.WARNA["baja"]),
    (str(df["at"].max().date()), "ulasan paling baru", t.WARNA["baja"]),
    (t.angka((df["thumbsUpCount"] > 0).mean() * 100, 1) + "%",
     "ulasan yang punya 'membantu'", t.WARNA["rel"]),
])

tab1, tab2, tab3 = st.tabs(["Sebaran", "Pratinjau dan unduhan", "Catatan pembersihan"])
with tab1:
    a, b = st.columns(2)
    with a:
        st.subheader("Rating bintang")
        rt = df.groupby(["score", "sentimen_rating"]).size().reset_index(name="jumlah")
        f1 = px.bar(rt, x="score", y="jumlah", color="sentimen_rating",
                    color_discrete_map=t.WARNA_SENTIMEN,
                    labels={"score": "Bintang", "jumlah": "Jumlah ulasan"})
        f1.update_xaxes(dtick=1)
        st.plotly_chart(t.gaya(f1, 320))
    with b:
        st.subheader("Panjang ulasan (jumlah kata)")
        f2 = px.histogram(df[df["kata"] <= 100], x="kata", nbins=50,
                          color_discrete_sequence=[t.WARNA["rel"]],
                          labels={"kata": "Jumlah kata"})
        st.plotly_chart(t.gaya(f2, 320))
        st.caption("Ulasan di atas 100 kata tidak ditampilkan di grafik ini.")
with tab2:
    st.dataframe(df.sort_values("at", ascending=False)
                 [["at", "score", "thumbsUpCount", "sentimen", "tema", "teks_asli"]]
                 .head(300), hide_index=True)
    st.download_button("Unduh ulasan terpilih (CSV)",
                       df.drop(columns=["kata"]).to_csv(index=False).encode("utf-8"),
                       "ulasan_terpilih.csv", "text/csv")
with tab3:
    st.markdown(
        "- Duplikat dibuang berdasarkan ID ulasan; ulasan kembar dari pengguna berbeda dipertahankan.\n"
        "- Ulasan kosong dibuang. Teks asli dan teks bersih disimpan di kolom berbeda.\n"
        "- Huruf kecil, tautan dan tanda baca dibuang, kata tidak baku dinormalisasi, huruf berulang dirapikan.\n"
        "- Kata negasi (tidak, bukan, belum) dipertahankan karena memengaruhi makna.\n"
        "- Nama pengguna tidak disimpan.")