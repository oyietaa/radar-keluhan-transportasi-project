import pandas as pd
from pipeline.pesan import pesan_sukses, pesan_gagal

R = {"total_ulasan": 3064, "ulasan_baru": 2, "rata_rata_rating": 3.37,
     "persen_sentimen": {"positif": 52.0, "netral": 8.0, "negatif": 40.0},
     "tema_terbanyak": "Aplikasi error, lambat, dan bug",
     "jumlah_per_tema": {"Aplikasi error, lambat, dan bug": 914}, "ulasan_singkat": 1234}

def _baru():
    return pd.DataFrame({
        "sentimen": ["negatif", "positif"],
        "score": [1, 5],
        "tema": ["Aplikasi error, lambat, dan bug", "Ulasan singkat"],
        "teks_asli": ["lemot <b>banget</b> & error", "bagus"],
        "at": pd.to_datetime(["2026-11-25 07:00", "2026-11-25 06:00"])})

def test_pesan_sukses_memuat_ringkasan():
    teks = pesan_sukses(R, _baru(), neg_sebelum=39.5)
    assert "2 ulasan baru" in teks and "3.064" in teks
    assert "40,0%" in teks and "▲" in teks

def test_teks_ulasan_di_escape():
    teks = pesan_sukses(R, _baru())
    assert "&lt;b&gt;banget&lt;/b&gt;" in teks and "&amp;" in teks

def test_tanpa_ulasan_baru_dan_pesan_gagal():
    assert "Tidak ada ulasan baru" in pesan_sukses(dict(R, ulasan_baru=0), pd.DataFrame())
    assert "GAGAL" in pesan_gagal(RuntimeError("uji"))