import streamlit as st
from bot.jawab import jawab, TEMA

st.title("Tanya Bot")
st.caption("Jawaban dibaca dari hasil analisis di dashboard ini, bukan dikarang.")

with st.expander("Contoh pertanyaan"):
    st.markdown("- Berapa persen ulasan negatif?\n- Keluhan apa yang paling banyak?\n"
                "- Rata-rata rating berapa?\n- R2 itu apa?\n"
                "- Kapan data terakhir diperbarui?\n- Apa keterbatasan analisis ini?")

if "riwayat" not in st.session_state:
    st.session_state.riwayat = [("assistant", TEMA["greeting"], "")]

for peran, teks, meta in st.session_state.riwayat:
    with st.chat_message(peran):
        st.write(teks)
        if meta:
            st.caption(meta)

pesan = st.chat_input("Tanya soal hasil analisis...")
if pesan:
    hasil = jawab(pesan)
    label = hasil["intent"] or "tidak dikenali"
    st.session_state.riwayat.append(("user", pesan, ""))
    st.session_state.riwayat.append(
        ("assistant", hasil["reply"], f"intent: {label} | skor {hasil['score']:.2f}"))
    st.rerun()