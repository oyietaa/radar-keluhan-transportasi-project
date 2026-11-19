from pathlib import Path

BASE = Path(__file__).parent
APP_ID = "com.kai.kaiticketing"
LANG, COUNTRY = "id", "id"
RAW_DIR = BASE / "data" / "raw"
CLEAN_CSV = BASE / "data" / "clean" / "ulasan_bersih.csv"
MODEL_DIR = BASE / "models"
RINGKASAN = BASE / "ringkasan.json"
LOG = BASE / "log_pipeline.json"
JUMLAH_JADWAL = 500
RETENSI_BULAN = 6
RETENSI_MAKS = 10000