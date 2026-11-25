from bot.jawab import ENGINE

def test_klasifikasi_inti():
    assert ENGINE.classify("keluhan apa yang paling banyak")[0] == "tema"
    assert ENGINE.classify("berapa persen ulasan negatif")[0] == "sentimen"
    assert ENGINE.classify("kapan data terakhir diperbarui")[0] == "status_pipeline"

def test_di_luar_topik_ditolak():
    assert ENGINE.classify("siapa presiden indonesia")[0] is None

from bot.jawab import _angka

def test_format_angka_indonesia():
    assert _angka(2987) == "2.987"
    assert _angka(52.1, 1) == "52,1"

def test_intent_baru_dikenali():
    assert ENGINE.classify("daftar tema")[0] == "daftar_tema"
    assert ENGINE.classify("kebijakan retensi data")[0] == "masa_simpan"