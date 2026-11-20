import json
import streamlit as st
from config import MODEL_DIR
from muat import muat_data

st.title("Tema Keluhan")
df = muat_data()
info = json.loads((MODEL_DIR / "cluster_info.json").read_text(encoding="utf-8"))
tema = json.loads((MODEL_DIR / "tema.json").read_text(encoding="utf-8"))

cluster = df[df["cluster"] >= 0]
singkat = int((df["cluster"] == -1).sum())
st.write(f"{len(cluster):,} ulasan dikelompokkan (4 kata atau lebih). "
         f"{singkat:,} ulasan yang lebih pendek diberi tema 'Ulasan singkat' "
         "dan tidak ikut clustering.")

st.subheader("Ukuran tiap tema")
st.bar_chart(cluster["tema"].value_counts())

st.subheader("Kata dominan dan contoh ulasan")
for kode, nama in tema.items():
    if kode == "-1":
        continue
    sub = cluster[cluster["tema"] == nama]
    with st.expander(f"{nama} ({len(sub):,} ulasan)", expanded=True):
        st.write("Kata dominan: " + ", ".join(info[kode]["kata"]))
        for teks in sub["teks_asli"].sample(min(3, len(sub)), random_state=1):
            st.markdown(f"- {teks[:200]}")

st.subheader("Pembeda antartema dan keterbatasan")
st.markdown(
    "- Dua tema berisi pujian (apresiasi layanan dan kemudahan memesan), "
    "dua tema berisi keluhan (gagal masuk/transaksi dan error/lambat/bug).\n"
    "- Tema keluhan masih tumpang tindih: 'tidak bisa dibuka' dan 'error terus' "
    "sangat berdekatan.\n"
    "- Tema 'Aplikasi error, lambat, dan bug' berisi separuh ulasan dan masih "
    "bercampur dengan keluhan biaya serta keluhan di luar aplikasi.\n"
    "- Pengelompokan memakai kata (TF-IDF), bukan makna, sehingga celaan yang "
    "memakai kata pujian bisa salah masuk."
)