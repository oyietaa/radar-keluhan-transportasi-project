import html
import os
from datetime import datetime, timedelta, timezone

BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
WIB = timezone(timedelta(hours=7))

def _angka(x, desimal=0):
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def _waktu():
    d = datetime.now(WIB)
    return f"{d.day} {BULAN[d.month - 1]} {d.year}, {d:%H.%M} WIB"

def _tautan_run():
    repo, run = os.getenv("GITHUB_REPOSITORY"), os.getenv("GITHUB_RUN_ID")
    return f"https://github.com/{repo}/actions/runs/{run}" if repo and run else ""

def _potong(teks, n=110):
    teks = " ".join(str(teks).split())
    return teks if len(teks) <= n else teks[: n - 1].rstrip() + "…"

def pesan_sukses(r, baru, neg_sebelum=None):
    e = html.escape
    p = r["persen_sentimen"]
    n = r["ulasan_baru"]
    baris = ["<b>📡 Radar Keluhan Access by KAI</b>", f"✅ Berhasil · {_waktu()}", ""]
    if n:
        c = baru["sentimen"].value_counts()
        baris.append(f"🆕 <b>{_angka(n)} ulasan baru</b> (total {_angka(r['total_ulasan'])})")
        baris.append(f"🟢 {c.get('positif', 0)} positif · 🟡 {c.get('netral', 0)} netral · "
                     f"🔴 {c.get('negatif', 0)} negatif")
        tb = baru[baru["tema"] != "Ulasan singkat"]["tema"].value_counts()
        if len(tb):
            baris.append(f"Tema terbanyak pada ulasan baru: {e(str(tb.index[0]))} ({tb.iloc[0]})")
    else:
        baris.append(f"🆕 Tidak ada ulasan baru (total {_angka(r['total_ulasan'])})")

    neg = f"🔴 {_angka(p['negatif'], 1)}% negatif"
    if neg_sebelum is not None:
        selisih = p["negatif"] - neg_sebelum
        if abs(selisih) >= 0.05:
            neg += f" ({'▲' if selisih > 0 else '▼'} {_angka(abs(selisih), 1)} poin)"
    baris += ["", "📊 <b>Seluruh data</b>",
              f"🟢 {_angka(p['positif'], 1)}% positif · 🟡 {_angka(p['netral'], 1)}% netral · {neg}",
              f"⭐ Rating rata-rata {_angka(r['rata_rata_rating'], 2)} dari 5"]
    jumlah_tema = r["jumlah_per_tema"].get(r["tema_terbanyak"], 0)
    baris.append(f"🧭 Tema terbesar: {e(r['tema_terbanyak'])} ({_angka(jumlah_tema)} ulasan)")

    if n:
        negatif = (baru[(baru["sentimen"] == "negatif") & (baru["score"] <= 2)]
                   .sort_values("at", ascending=False).head(3))
        if len(negatif):
            baris += ["", "💬 <b>Contoh ulasan baru (diprediksi negatif, rating 1-2)</b>"]
            baris += [f"• ⭐{int(s)} “{e(_potong(t))}”"
                      for t, s in zip(negatif["teks_asli"], negatif["score"])]

    link = _tautan_run()
    if link:
        baris += ["", f'🔗 <a href="{link}">Lihat jalannya di GitHub Actions</a>']
    return "\n".join(baris)

def pesan_gagal(err):
    baris = ["<b>⚠️ Pembaruan Radar Keluhan GAGAL</b>", _waktu(), "",
             f"Penyebab: {html.escape(_potong(err, 300))}", "",
             "Periksa catatan lengkapnya di GitHub Actions. Pipeline akan mencoba lagi "
             "pada jadwal berikutnya, atau jalankan manual dari tab Actions."]
    link = _tautan_run()
    if link:
        baris += ["", f'🔗 <a href="{link}">Buka log</a>']
    return "\n".join(baris)

if __name__ == "__main__":
    import json
    import sys
    import pandas as pd
    from config import CLEAN_CSV, RINGKASAN
    from pipeline.telegram import kirim

    r = json.loads(RINGKASAN.read_text(encoding="utf-8"))
    d = pd.read_csv(CLEAN_CSV, parse_dates=["at"]).sort_values("at", ascending=False)
    r["ulasan_baru"] = 7  # contoh untuk pratinjau
    teks = pesan_sukses(r, d.head(7), neg_sebelum=r["persen_sentimen"]["negatif"] - 0.3)
    print(teks)
    if "--kirim" in sys.argv:
        kirim(teks, pakai_html=True)