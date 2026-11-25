import json
import pandas as pd
import plotly.express as px
import streamlit as st
import tampilan as t
from config import BASE, MODEL_DIR
from muat import muat_data

t.siapkan("Sentimen", "🚦")
df = t.filter_sidebar(muat_data(), "sentimen")
metrik = json.loads((MODEL_DIR / "metrik.json").read_text(encoding="utf-8"))
n = len(df)
hitung = df["sentimen"].value_counts().reindex(t.URUTAN_SENTIMEN).fillna(0).astype(int)

st.title("Sentimen ulasan")
t.papan([
    (t.angka(n), "ulasan terpilih", t.WARNA["baja"]),
    (t.angka(hitung["positif"] / n * 100, 1) + "%", "positif", t.WARNA["hijau"]),
    (t.angka(hitung["netral"] / n * 100, 1) + "%", "netral", t.WARNA["kuning"]),
    (t.angka(hitung["negatif"] / n * 100, 1) + "%", "negatif", t.WARNA["merah"]),
])

tab1, tab2, tab3, tab4 = st.tabs(["Distribusi", "Kinerja model", "Pemeriksaan manual", "Tabel ulasan"])

with tab1:
    a, b = st.columns(2)
    with a:
        st.subheader("Komposisi sentimen (prediksi)")
        d = hitung.rename_axis("sentimen").reset_index(name="jumlah")
        donat = px.pie(d, names="sentimen", values="jumlah", hole=0.55, color="sentimen",
                       color_discrete_map=t.WARNA_SENTIMEN)
        donat.update_traces(textinfo="percent+label", sort=False)
        donat.update_layout(showlegend=False)
        st.plotly_chart(t.gaya(donat, 340))
    with b:
        st.subheader("Rating dibanding prediksi")
        ct = (pd.crosstab(df["sentimen_rating"], df["sentimen"])
                .reindex(index=t.URUTAN_SENTIMEN, columns=t.URUTAN_SENTIMEN)
                .fillna(0).astype(int))
        peta = px.imshow(ct, text_auto=True, aspect="auto",
                         color_continuous_scale=[t.WARNA["panel"], t.WARNA["rel"]],
                         labels=dict(x="Prediksi model", y="Menurut rating", color="Ulasan"))
        st.plotly_chart(t.gaya(peta, 340))
    sama = (df["sentimen_rating"] == df["sentimen"]).mean() * 100
    st.caption(f"Kesesuaian rating dan prediksi: {sama:.1f}% pada ulasan terpilih. Dihitung pada data "
               "yang sebagian dipakai melatih, jadi tampak lebih baik daripada akurasi data uji.")

with tab2:
    st.metric("Akurasi model pada data uji (598 ulasan)", f"{metrik['sentimen_akurasi'] * 100:.1f}%")
    st.dataframe(pd.DataFrame(
        {"precision": [0.76, 0.14, 0.95], "recall": [0.83, 0.17, 0.88],
         "f1": [0.79, 0.15, 0.91], "jumlah uji": [225, 36, 337]},
        index=["negatif", "netral", "positif"]))
    st.caption("Kelas netral jauh lebih lemah karena jumlahnya sedikit dan rating 3 sering berisi "
               "campuran pujian dan keluhan, sehingga akurasi keseluruhan tidak menggambarkan kelas ini.")
    st.subheader("Akurasi menurut panjang ulasan (data uji)")
    try:
        pjg = pd.read_csv(MODEL_DIR / "evaluasi_panjang.csv", index_col=0)
        fp = px.bar(pjg.reset_index(), x="kelompok", y="akurasi", text_auto=".0%",
                    color_discrete_sequence=[t.WARNA["rel"]], labels={"kelompok": ""})
        fp.update_yaxes(range=[0, 1], tickformat=".0%")
        st.plotly_chart(t.gaya(fp, 300))
        st.caption("Ulasan 1-2 kata paling mudah ditebak. Akurasi keseluruhan sebagian ditopang kelompok ini.")
    except FileNotFoundError:
        st.info("Berkas evaluasi_panjang.csv belum ada. Jalankan cek_panjang.py.")

with tab3:
    try:
        ev = pd.read_csv(BASE / "evaluasi_sentimen.csv")
    except FileNotFoundError:
        st.info("Berkas evaluasi_sentimen.csv belum ada.")
    else:
        m = len(ev)
        c1, c2, c3 = st.columns(3)
        c1.metric("Manual vs rating", f"{(ev.label_manual == ev.sentimen_rating).sum()}/{m}")
        c2.metric("Manual vs model", f"{(ev.label_manual == ev.prediksi).sum()}/{m}")
        c3.metric("Rating vs model", f"{(ev.sentimen_rating == ev.prediksi).sum()}/{m}")
        st.caption("Label diberikan sebelum melihat rating dan prediksi; penilai memilih netral bila ragu. "
                   "Sampel kecil, sehingga tidak menggambarkan seluruh data.")
        st.write("Ketidaksesuaian antara label manual dan prediksi model:")
        beda = ev[ev.label_manual != ev.prediksi]
        st.dataframe(beda[["teks_asli", "label_manual", "sentimen_rating", "prediksi"]], hide_index=True)

with tab4:
    q = st.text_input("Cari kata dalam ulasan")
    tampil = df if not q else df[df["teks_asli"].str.contains(q, case=False, na=False, regex=False)]
    st.write(f"{t.angka(len(tampil))} ulasan ditampilkan (maksimal 300 terbaru).")
    st.dataframe(tampil.sort_values("at", ascending=False)
                 [["at", "score", "sentimen", "tema", "teks_asli"]].head(300), hide_index=True)