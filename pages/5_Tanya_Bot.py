import streamlit as st
import tampilan as t
from bot.jawab import ENGINE, TEMA, jawab

t.siapkan("Tanya Bot", "💬")
SARAN = ["Berapa persen ulasan negatif?", "Keluhan apa yang paling banyak?",
         "Rata-rata rating berapa?", "R2 itu apa?", "Apa keterbatasan analisis ini?"]

if "riwayat" not in st.session_state:
    st.session_state.riwayat = [("assistant", TEMA["greeting"], "")]

def kirim(teks):
    teks = teks.strip()[:500]
    if not teks:
        return
    h = jawab(teks)
    meta = f"intent: {h['intent'] or 'tidak dikenali'} | skor {h['score']:.2f}"
    if st.session_state.get("mode_belajar"):
        for i, c in enumerate(ENGINE.explain(teks), 1):
            meta += f"\n{i}. {c['intent']} ({c['score']:.2f}), pola: {c['pattern']}"
    st.session_state.riwayat.append(("user", teks, ""))
    st.session_state.riwayat.append(("assistant", h["reply"], meta))

st.title("Tanya bot")
st.caption("Jawaban dibaca dari hasil analisis di dashboard ini, bukan dikarang.")
st.toggle("Mode belajar: tampilkan kandidat intent dan skornya", key="mode_belajar")

kolom = st.columns(len(SARAN))
for c, s in zip(kolom, SARAN):
    c.button(s, key=f"saran_{s}", on_click=kirim, args=(s,))

for peran, teks, meta in st.session_state.riwayat:
    with st.chat_message(peran):
        st.write(teks)
        for baris in meta.split("\n"):
            if baris:
                st.caption(baris)

pesan = st.chat_input("Tanya soal hasil analisis...")
if pesan:
    kirim(pesan)
    st.rerun()