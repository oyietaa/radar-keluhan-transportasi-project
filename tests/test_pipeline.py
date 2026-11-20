import pandas as pd
from pipeline.retensi import terapkan_retensi

def test_retensi_membuang_ulasan_lama():
    df = pd.DataFrame({"at": [pd.Timestamp.now(),
                              pd.Timestamp.now() - pd.DateOffset(months=8)]})
    assert len(terapkan_retensi(df)) == 1