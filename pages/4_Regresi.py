import json
import joblib
import pandas as pd
import streamlit as st
from config import MODEL_DIR

st.title("Regresi: Perkiraan Jumlah 'Membantu'")
metrik = json.loads((MODEL_DIR / "metrik.json").read_text(encoding="utf-8"))
reg = joblib.load(MODEL_DIR / "regresi.joblib")
uji = pd.read_csv(MODEL_DIR / "uji_regresi.csv")

st.write("Fitur: jumlah kata dan rating. Target: jumlah 'membantu'. "
         "Data dibagi 80% latih dan 20% uji (random_state=42).")
st.caption("Model dilatih dan diuji pada 2.987 ulasan awal (data/data_latih_awal.csv). "
           "Ulasan yang ditambahkan pipeline tidak mengubah angka di halaman ini.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("MAE model", metrik["regresi_mae"])
c2.metric("MAE tebak 0", metrik["mae_tebak_nol"])
c3.metric("MAE tebak rata-rata", metrik["mae_tebak_rata2"])
c4.metric("R²", metrik["regresi_r2"])

st.subheader("Aktual dibandingkan prediksi (data uji)")
sembunyi = st.checkbox("Sembunyikan ulasan ekstrem (aktual > 20)", value=True)
tampil = uji[uji["aktual"] <= 20] if sembunyi else uji
st.scatter_chart(tampil, x="aktual", y="prediksi")
if sembunyi:
    st.caption(f"{len(uji) - len(tampil)} ulasan dengan 'membantu' di atas 20 "
               "tidak ditampilkan di grafik, tetapi tetap dihitung dalam MAE dan R².")

st.write("Rata-rata prediksi menurut nilai aktual (angka 5 berarti 5 atau lebih)")
ringkas = (uji.assign(aktual=uji["aktual"].clip(upper=5))
              .groupby("aktual")["prediksi"].mean().round(2))
st.bar_chart(ringkas)

st.subheader("Interpretasi")
st.markdown(
    f"- **MAE** adalah rata-rata selisih mutlak tebakan dan nilai asli, dalam "
    f"satuan jumlah 'membantu'. Tebakan 0 untuk semua ulasan memberi MAE "
    f"{metrik['mae_tebak_nol']}, lebih kecil dari model "
    f"({metrik['regresi_mae']}).\n"
    f"- **R²** = {metrik['regresi_r2']}. Nilai mendekati 0 berarti model tidak "
    "lebih baik daripada menebak rata-rata, dan nilai negatif berarti lebih buruk.\n"
    f"- {metrik['persen_membantu_nol']}% ulasan tidak memiliki 'membantu', dan "
    "beberapa ulasan ekstrem memengaruhi hasil.\n"
    "- Jumlah 'membantu' dipengaruhi faktor lain, seperti usia ulasan, isi pesan, "
    "dan kebiasaan pengguna menekan tombol."
)

st.subheader("Perkirakan jumlah 'membantu'")
with st.form("estimasi"):
    kata = st.number_input("Jumlah kata dalam ulasan", min_value=1, max_value=300, value=20)
    rating = st.slider("Rating bintang", 1, 5, 3)
    kirim = st.form_submit_button("Hitung estimasi")
if kirim:
    est = float(reg.predict(pd.DataFrame({"jumlah_kata": [kata], "score": [rating]}))[0])
    st.metric("Estimasi jumlah 'membantu'", f"{est:.2f}")
    if est < 0:
        st.warning("Estimasi bernilai negatif, tidak bermakna sebagai jumlah "
                   "'membantu'. Ini menunjukkan keterbatasan regresi linear.")