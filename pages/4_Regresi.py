import json
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st
import tampilan as t
from config import MODEL_DIR

t.siapkan("Regresi", "📉")
metrik = json.loads((MODEL_DIR / "metrik.json").read_text(encoding="utf-8"))
reg = joblib.load(MODEL_DIR / "regresi.joblib")
uji = pd.read_csv(MODEL_DIR / "uji_regresi.csv")

st.title("Regresi: perkiraan jumlah 'membantu'")
st.write("Fitur: jumlah kata dan rating. Target: jumlah 'membantu'. "
         "Data dibagi 80% latih dan 20% uji (random_state=42).")
st.caption("Model dilatih dan diuji pada 2.987 ulasan awal (data/data_latih_awal.csv). "
           "Ulasan yang ditambahkan pipeline tidak mengubah angka di halaman ini.")
t.papan([
    (t.angka(metrik["regresi_mae"], 3), "MAE model", t.WARNA["merah"]),
    (t.angka(metrik["mae_tebak_nol"], 3), "MAE jika selalu menebak 0", t.WARNA["hijau"]),
    (t.angka(metrik["mae_tebak_rata2"], 3), "MAE jika menebak rata-rata", t.WARNA["baja"]),
    (t.angka(metrik["regresi_r2"], 3), "R²", t.WARNA["baja"]),
])

tab1, tab2, tab3 = st.tabs(["Aktual dan prediksi", "Interpretasi", "Coba estimasi"])
with tab1:
    sembunyi = st.checkbox("Sembunyikan ulasan ekstrem (aktual > 20)", value=True)
    tampil = uji[uji["aktual"] <= 20] if sembunyi else uji
    f = px.scatter(tampil, x="aktual", y="prediksi", opacity=0.45,
                   color_discrete_sequence=[t.WARNA["rel"]],
                   labels={"aktual": "Jumlah 'membantu' sebenarnya", "prediksi": "Prediksi model"})
    batas = max(float(tampil["aktual"].max()), 1.0)
    f.add_shape(type="line", x0=0, y0=0, x1=batas, y1=batas,
                line=dict(color=t.WARNA["abu"], dash="dash"))
    st.plotly_chart(t.gaya(f, 380))
    st.caption("Garis putus-putus adalah prediksi sempurna. Titik yang jauh di bawahnya berarti "
               "model menebak terlalu rendah untuk ulasan yang dianggap sangat membantu. "
               f"{len(uji) - len(tampil)} ulasan tidak ditampilkan di grafik, tetapi tetap dihitung dalam MAE dan R².")
    rata = (uji.assign(aktual=uji["aktual"].clip(upper=5))
               .groupby("aktual")["prediksi"].mean().round(2).reset_index())
    rata["aktual"] = rata["aktual"].map(lambda v: "5 atau lebih" if v >= 5 else str(int(v)))
    st.subheader("Rata-rata prediksi menurut nilai sebenarnya")
    f2 = px.bar(rata, x="aktual", y="prediksi", color_discrete_sequence=[t.WARNA["rel"]],
                labels={"aktual": "Jumlah 'membantu' sebenarnya", "prediksi": "Rata-rata prediksi"})
    st.plotly_chart(t.gaya(f2, 300))
with tab2:
    st.markdown(
        f"- **MAE** adalah rata-rata selisih mutlak tebakan dan nilai asli. Tebakan 0 untuk semua ulasan "
        f"memberi MAE {t.angka(metrik['mae_tebak_nol'], 3)}, lebih kecil dari model "
        f"({t.angka(metrik['regresi_mae'], 3)}).\n"
        f"- **R²** = {t.angka(metrik['regresi_r2'], 3)}. Nilai mendekati 0 berarti model tidak lebih baik "
        "daripada menebak rata-rata, dan nilai negatif berarti lebih buruk.\n"
        f"- {t.angka(metrik['persen_membantu_nol'], 1)}% ulasan tidak memiliki 'membantu', dan beberapa "
        "ulasan ekstrem memengaruhi hasil.\n"
        "- Jumlah 'membantu' dipengaruhi faktor lain, seperti usia ulasan, isi pesan, dan kebiasaan pengguna.\n"
        "- Regresi linear dapat menghasilkan estimasi negatif, yang tidak bermakna sebagai jumlah 'membantu'.")
    st.write(f"Koefisien model: setiap tambahan 10 kata mengubah estimasi sebesar "
             f"{t.angka(reg.coef_[0] * 10, 3)}, dan setiap tambahan 1 bintang mengubahnya sebesar "
             f"{t.angka(reg.coef_[1], 3)}.")
with tab3:
    with st.form("estimasi"):
        kata = st.number_input("Jumlah kata dalam ulasan", min_value=1, max_value=300, value=20)
        rating = st.slider("Rating bintang", 1, 5, 3)
        kirim = st.form_submit_button("Hitung estimasi")
    if kirim:
        est = float(reg.predict(pd.DataFrame({"jumlah_kata": [kata], "score": [rating]}))[0])
        st.metric("Estimasi jumlah 'membantu'", t.angka(est, 2))
        if est < 0:
            st.warning("Estimasi bernilai negatif, tidak bermakna sebagai jumlah 'membantu'. "
                       "Ini menunjukkan keterbatasan regresi linear.")