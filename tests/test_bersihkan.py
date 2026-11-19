import pandas as pd
from pipeline.bersihkan import bersihkan_teks, bersihkan_df

def test_negasi_dipertahankan():
    assert "tidak" in bersihkan_teks("Aplikasi gak bisa dibuka!!").split()

def test_normalisasi_dan_tautan():
    assert bersihkan_teks("Mantap bgt https://x.co") == "mantap banget"

def test_huruf_berulang_dan_singkatan():
    assert bersihkan_teks("kerennn") == "keren"
    assert bersihkan_teks("g bisa lg") == "tidak bisa lagi"

def test_ulasan_singkat_dan_kembar_dipertahankan():
    df = pd.DataFrame({"reviewId": ["a", "b"], "content": ["Bagus", "Bagus"],
                       "score": [5, 5], "thumbsUpCount": [0, 0],
                       "at": ["2026-11-18", "2026-11-18"]})
    assert len(bersihkan_df(df)) == 2