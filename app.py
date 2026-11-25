import pandas as pd
import plotly.express as px
import streamlit as st
import tampilan as t
from muat import muat_data, muat_ringkasan

t.siapkan("Beranda")
try:
    semua = muat_data()
    r = muat_ringkasan()
except FileNotFoundError as e:
    st.error(f"Berkas data belum ada: {e.filename}. Jalankan pipeline terlebih dahulu.")
    st.stop()

df = t.filter_sidebar(semua, "beranda")
n = len(df)
neg = (df["sentimen"] == "negatif").mean() * 100
pos = (df["sentimen"] == "positif").mean() * 100
keluhan = df[df["tema"].isin(t.TEMA_KELUHAN)]["tema"].value_counts()

st.title("Radar Keluhan Access by KAI")
sorot = f"Dari {t.angka(n)} ulasan, {t.angka(neg, 1)}% bernada negatif."
if len(keluhan):
    sorot += f" Keluhan terbesar: {keluhan.index[0]} ({t.angka(keluhan.iloc[0])} ulasan)."
st.markdown(f"<p class='sorot'>{sorot}</p>", unsafe_allow_html=True)

t.papan([
    (t.angka(n), "ulasan terpilih", t.WARNA["baja"]),
    (t.angka(df["score"].mean(), 2), "rata-rata rating (dari 5)", t.WARNA["baja"]),
    (t.angka(neg, 1) + "%", "negatif (prediksi)", t.WARNA["merah"]),
    (t.angka(pos, 1) + "%", "positif (prediksi)", t.WARNA["hijau"]),
])

st.subheader("Ulasan per minggu menurut sentimen")
mingguan = (df.groupby([pd.Grouper(key="at", freq="W"), "sentimen"])
              .size().reset_index(name="jumlah"))
fig = px.bar(mingguan, x="at", y="jumlah", color="sentimen",
             color_discrete_map=t.WARNA_SENTIMEN,
             category_orders={"sentimen": t.URUTAN_SENTIMEN},
             labels={"at": "Minggu berakhir", "jumlah": "Jumlah ulasan"})
st.plotly_chart(t.gaya(fig, 340, "x unified"))
st.caption("Minggu pertama dan terakhir belum penuh karena data dipotong pada tanggal pengambilan.")

kiri, kanan = st.columns(2)
with kiri:
    st.subheader("Prediksi model dan menurut rating")
    bd = pd.DataFrame({
        "Prediksi model": df["sentimen"].value_counts(normalize=True) * 100,
        "Menurut rating": df["sentimen_rating"].value_counts(normalize=True) * 100,
    }).reindex(t.URUTAN_SENTIMEN).fillna(0).round(1)
    bd = bd.rename_axis("sentimen").reset_index().melt(
        id_vars="sentimen", var_name="sumber", value_name="persen")
    f2 = px.bar(bd, x="sentimen", y="persen", color="sumber", barmode="group",
                color_discrete_sequence=[t.WARNA["rel"], t.WARNA["abu"]],
                labels={"persen": "Persen (%)", "sentimen": ""})
    st.plotly_chart(t.gaya(f2, 340))
    st.caption("Model dilatih dari rating bintang, jadi keduanya mirip tetapi tidak sama.")
with kanan:
    st.subheader("Tema keluhan")
    tm = (df["tema"].value_counts().rename_axis("tema").reset_index(name="jumlah"))
    tm = tm[tm["tema"] != "Ulasan singkat"]
    f3 = px.bar(tm, x="jumlah", y="tema", orientation="h", color="tema",
                color_discrete_map=t.WARNA_TEMA, labels={"jumlah": "Jumlah ulasan", "tema": ""})
    f3.update_layout(showlegend=False)
    f3.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(t.gaya(f3, 340))
    st.caption("Hanya ulasan 4 kata atau lebih yang dikelompokkan.")

st.caption(f"Data diperbarui {r['diperbarui']} (waktu dicatat dalam WIB). "
           "Gunakan menu di kiri untuk membuka halaman lain.")