import streamlit as st

WARNA = {"baja": "#1B2A41", "rel": "#2F6FD6", "hijau": "#1E9E6A", "kuning": "#E3A008",
         "merah": "#D6293E", "abu": "#7A8798", "panel": "#F7F9FB"}
WARNA_SENTIMEN = {"positif": "#1E9E6A", "netral": "#E3A008", "negatif": "#D6293E"}
URUTAN_SENTIMEN = ["positif", "netral", "negatif"]
WARNA_TEMA = {
    "Apresiasi layanan KAI": "#1E9E6A",
    "Kemudahan memesan tiket": "#6CC7A0",
    "Gagal masuk dan transaksi bermasalah": "#E8743B",
    "Aplikasi error, lambat, dan bug": "#A3162B",
    "Ulasan singkat": "#7A8798",
}
TEMA_KELUHAN = ["Gagal masuk dan transaksi bermasalah", "Aplikasi error, lambat, dan bug"]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
html, body, .stApp, button, input, textarea, h1, h2, h3, h4, p, label, th, td {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
h1 { font-weight: 800; letter-spacing: -0.02em; }
h2, h3 { font-weight: 700; letter-spacing: -0.01em; }
.sorot { font-size: 1.3rem; font-weight: 600; line-height: 1.4; max-width: 46rem; margin: 0 0 1rem; }
.papan { display: grid; grid-template-columns: repeat(4, 1fr); border: 2px solid #9FB0C5;
  border-radius: 6px; background: #F7F9FB; margin: 0.5rem 0 1.5rem; }
.papan div { padding: 0.9rem 1.1rem; border-left: 1px solid #D5DDE8; }
.papan div:first-child { border-left: none; }
.papan b { display: block; font-size: 2rem; font-weight: 800; line-height: 1.1;
  font-variant-numeric: tabular-nums; }
.papan span { font-size: 0.85rem; color: #4A5B73; }
@media (max-width: 700px) { .papan { grid-template-columns: repeat(2, 1fr); } }
[data-testid="stSidebar"] { border-right: 1px solid #C9D4E1; }
.stTabs [data-baseweb="tab"] { font-weight: 600; }
"""

def siapkan(judul, ikon="🚆"):
    st.set_page_config(page_title=f"{judul} | Radar Keluhan", page_icon=ikon, layout="wide")
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)

def angka(x, desimal=0):
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def papan(sel):
    isi = "".join(f"<div><b style='color:{w}'>{n}</b><span>{l}</span></div>"
                  for n, l, w in sel)
    st.markdown(f"<div class='papan'>{isi}</div>", unsafe_allow_html=True)

def gaya(fig, tinggi=340, hover="closest"):
    fig.update_layout(
        template="plotly_white", height=tinggi, margin=dict(l=8, r=8, t=30, b=8),
        hovermode=hover, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=WARNA["baja"]),
        legend=dict(orientation="h", y=-0.2, title_text=""))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#D3DCE7", zerolinecolor="#D3DCE7")
    return fig

def _dua(rentang, tmin, tmax):
    if isinstance(rentang, (list, tuple)) and len(rentang) == 2:
        return rentang
    return (tmin, tmax)

def filter_sidebar(df, halaman):
    s = st.session_state
    tmin, tmax = df["at"].min().date(), df["at"].max().date()
    a, b = _dua(s.get("f_tgl", (tmin, tmax)), tmin, tmax)
    awal = (min(max(a, tmin), tmax), max(min(b, tmax), tmin))

    def simpan(kunci, widget):
        s[kunci] = s[widget]

    def setel_ulang():
        for k in list(s.keys()):
            if k.startswith(("f_", "w_")):
                del s[k]

    st.sidebar.markdown("**Filter ulasan**")
    k1 = f"w_tgl_{halaman}"
    rentang = st.sidebar.date_input("Tanggal ulasan", value=awal, min_value=tmin,
                                    max_value=tmax, key=k1, on_change=simpan,
                                    args=("f_tgl", k1))
    k2 = f"w_sent_{halaman}"
    pilih_sent = st.sidebar.multiselect(
        "Sentimen (prediksi)", URUTAN_SENTIMEN,
        default=[x for x in s.get("f_sent", URUTAN_SENTIMEN) if x in URUTAN_SENTIMEN],
        key=k2, on_change=simpan, args=("f_sent", k2))
    opsi_tema = [x for x in WARNA_TEMA if x in set(df["tema"])]
    k3 = f"w_tema_{halaman}"
    pilih_tema = st.sidebar.multiselect(
        "Tema", opsi_tema,
        default=[x for x in s.get("f_tema", opsi_tema) if x in opsi_tema],
        key=k3, on_change=simpan, args=("f_tema", k3))
    st.sidebar.button("Setel ulang filter", on_click=setel_ulang, key=f"reset_{halaman}")

    r = _dua(rentang, tmin, tmax)
    tgl = df["at"].dt.date
    hasil = df[tgl.between(r[0], r[1]) & df["sentimen"].isin(pilih_sent)
               & df["tema"].isin(pilih_tema)]
    st.sidebar.caption(f"{angka(len(hasil))} dari {angka(len(df))} ulasan")
    if hasil.empty:
        st.warning("Tidak ada ulasan yang cocok dengan filter. "
                   "Ubah filter di sidebar atau klik Setel ulang filter.")
        st.stop()
    return hasil