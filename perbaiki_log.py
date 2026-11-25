import json
from datetime import datetime, timedelta
from config import LOG, RINGKASAN

def geser(teks, jam=7):
    d = datetime.fromisoformat(teks) + timedelta(hours=jam)
    return d.isoformat(timespec="seconds" if len(teks) > 16 else "minutes")

log = json.loads(LOG.read_text(encoding="utf-8"))
n = 0
for e in log:
    if e["waktu"] in {"2026-11-22T06:15:08", "2026-11-22T13:51:08"}:
        e["waktu"] = geser(e["waktu"])
        e["pesan"] = "waktu dikoreksi dari UTC ke WIB"
        n += 1
LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

r = json.loads(RINGKASAN.read_text(encoding="utf-8"))
if r["diperbarui"].startswith("2026-11-22T13:5"):
    r["diperbarui"] = geser(r["diperbarui"])
    RINGKASAN.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
print(n, "catatan log dikoreksi")