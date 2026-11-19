from pipeline.bersihkan import bersihkan_teks

def test_negasi_dipertahankan():
    assert "tidak" in bersihkan_teks("Aplikasi gak bisa dibuka!!").split()

def test_normalisasi_dan_tautan():
    assert bersihkan_teks("Mantap bgt https://x.co") == "mantap banget"