from bot.jawab import ENGINE

def test_klasifikasi_inti():
    assert ENGINE.classify("keluhan apa yang paling banyak")[0] == "tema"
    assert ENGINE.classify("berapa persen ulasan negatif")[0] == "sentimen"
    assert ENGINE.classify("kapan data terakhir diperbarui")[0] == "status_pipeline"

def test_di_luar_topik_ditolak():
    assert ENGINE.classify("siapa presiden indonesia")[0] is None