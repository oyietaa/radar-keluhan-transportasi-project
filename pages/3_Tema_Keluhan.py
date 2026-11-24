import json
import plotly.express as px
import streamlit as st
import tampilan as t
from config import MODEL_DIR
from muat import muat_data

t.siapkan("Tema Keluhan", "🧭")
df = t.filter_sidebar(muat_data(), "tema")
info = json.loads((MODEL_DIR / "cluster_info.json").read_text(encoding="utf-8"))
tema = json.loads((MODEL_DIR / "tema.json").read_text(encoding="utf-8"))
nama_ke_kode = {v: k for k, v in tema.items() if k != "-1"}
cluster = df[df["cluster"] >= 0]
singkat = int((df["cluster"] == -1).sum())

st.title("Tema keluhan")
if cluster.empty:
    st.warning("Tidak ada ulasan 4 kata atau lebih pada filter ini, jadi tema belum bisa ditampilkan.")
    st.stop()
st.write(f"{t.angka(len(cluster))} ulasan dikelompokkan (4 kata atau lebih). "
         f"{t.angka(singkat)} ulasan yang lebih pendek diberi tema 'Ulasan singkat' "
         "dan tidak ikut clustering.")

hitung = cluster["tema"].value_counts().rename_axis("tema").reset_index(name="jumlah")
hitung["persen"] = hitung["jumlah"] / hitung["jumlah"].sum() * 100
hitung["label"] = hitung.apply(
    lambda r: f"{t.angka(r['jumlah'])} ulasan ({t.angka(r['persen'], 1)}%)", axis=1)
f = px.bar(hitung, x="jumlah", y="tema", orientation="h", color="tema",
           color_discrete_map=t.WARNA_TEMA, text="label",
           labels={"jumlah": "Jumlah ulasan", "tema": ""})
f.update_traces(textposition="outside", cliponaxis=False)
f.update_layout(showlegend=False)
f.update_yaxes(categoryorder="total ascending")
f.update_xaxes(range=[0, hitung["jumlah"].max() * 1.4])
st.plotly_chart(t.gaya(f, 300))

opsi = [n for n in t.WARNA_TEMA if n in nama_ke_kode and n in set(cluster["tema"])]
pilih = st.selectbox("Pilih tema untuk dilihat lebih dekat", opsi)
sub = cluster[cluster["tema"] == pilih]
kode = nama_ke_kode[pilih]
t.papan([
    (t.angka(len(sub)), "ulasan di tema ini", t.WARNA_TEMA[pilih]),
    (t.angka(len(sub) / len(cluster) * 100, 1) + "%", "dari ulasan yang dikelompokkan", t.WARNA["baja"]),
    (t.angka((sub["sentimen"] == "negatif").mean() * 100, 1) + "%", "bernada negatif", t.WARNA["merah"]),
    (t.angka(sub["score"].mean(), 2), "rata-rata rating", t.WARNA["baja"]),
])
st.write("**Kata dominan:** " + ", ".join(info[kode]["kata"]))

if "seed_contoh" not in st.session_state:
    st.session_state.seed_contoh = 1

def contoh_lain():
    st.session_state.seed_contoh += 1

st.button("Tampilkan contoh lain", on_click=contoh_lain)
for teks in sub["teks_asli"].sample(min(5, len(sub)), random_state=st.session_state.seed_contoh):
    st.markdown("> " + teks[:300].replace("\n", " "))

with st.expander("Pembeda antartema dan keterbatasan"):
    st.markdown(
        "- Dua tema berisi pujian (apresiasi layanan dan kemudahan memesan), dua tema berisi keluhan "
        "(gagal masuk atau transaksi, dan error atau lambat atau bug).\n"
        "- Tema keluhan masih tumpang tindih: 'tidak bisa dibuka' dan 'error terus' sangat berdekatan.\n"
        "- Tema 'Aplikasi error, lambat, dan bug' berisi separuh ulasan dan masih bercampur dengan "
        "keluhan biaya serta keluhan di luar aplikasi.\n"
        "- Pengelompokan memakai kata (TF-IDF), bukan makna, sehingga celaan yang memakai kata pujian "
        "bisa salah masuk.")