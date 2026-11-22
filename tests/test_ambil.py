import pytest
import pipeline.ambil as m

def test_ambil_gagal_jika_hasil_kosong(monkeypatch):
    monkeypatch.setattr(m, "reviews", lambda *a, **k: ([], None))
    with pytest.raises(RuntimeError):
        m.ambil(5)