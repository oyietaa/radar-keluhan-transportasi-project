import random
import re
from difflib import SequenceMatcher

NORMALISASI = {
    "gak": "tidak", "ga": "tidak", "nggak": "tidak", "enggak": "tidak",
    "tdk": "tidak", "gimana": "bagaimana", "gmn": "bagaimana",
    "brp": "berapa", "yg": "yang", "dgn": "dengan", "utk": "untuk",
    "sy": "saya", "aku": "saya", "persentase": "persen",
    "kak": "", "min": "", "dong": "", "sih": "", "nih": "", "ya": "",
    "makasih": "terima kasih", "thanks": "terima kasih",
    "hai": "halo", "hi": "halo", "hello": "halo",
    "ketemu": "bertemu", "aja": "saja", "jelek": "negatif", "buruk": "negatif",
    "mengeluh": "keluhan", "komplain": "keluhan", "dikeluhkan": "keluhan",
    "kekurangan": "kelemahan", "dipercaya": "akurat",
    "kategori": "tema", "topik": "tema", "kelompok": "tema",
    "skrip": "pipeline", "script": "pipeline",
}
STOPWORDS = {"yang", "di", "ke", "dari", "dan", "atau", "itu", "ini", "untuk",
             "dengan", "adalah", "apa", "saya", "mau", "ingin", "tolong",
             "bisa", "boleh", "kah", "pada", "akan", "juga", "ada"}
BOBOT_JACCARD, BOBOT_FUZZY, BOBOT_CAKUPAN = 0.4, 0.3, 0.3

def preprocess(teks):
    teks = teks.lower().replace("r kuadrat", "r2")
    teks = re.sub(r"[^a-z0-9\s]", " ", teks)
    tokens = []
    for kata in teks.split():
        for k in NORMALISASI.get(kata, kata).split():
            if len(k) > 5 and k.endswith("nya"):
                k = k[:-3]
            if k and k not in STOPWORDS:
                tokens.append(k)
    return tokens

def similarity(a, b):
    if not a or not b:
        return 0.0
    sa, sb = set(a), set(b)
    jaccard = len(sa & sb) / len(sa | sb)
    fuzzy = SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()
    cakupan = len(sa & sb) / len(sb)
    return round(BOBOT_JACCARD * jaccard + BOBOT_FUZZY * fuzzy
                 + BOBOT_CAKUPAN * cakupan, 4)

class ChatbotEngine:
    def __init__(self, theme, threshold=0.45):
        self.theme, self.threshold = theme, threshold
        self._patterns = [(i["tag"], p, preprocess(p))
                          for i in theme["intents"] for p in i["patterns"]]
        self._responses = {i["tag"]: i["responses"] for i in theme["intents"]}

    def explain(self, pesan, top=3):
        tokens = preprocess(pesan)
        terbaik = {}
        for tag, pola, pt in self._patterns:
            skor = similarity(tokens, pt)
            if tag not in terbaik or skor > terbaik[tag]["score"]:
                terbaik[tag] = {"intent": tag, "pattern": pola, "score": skor}
        return sorted(terbaik.values(), key=lambda x: x["score"], reverse=True)[:top]

    def classify(self, pesan):
        kandidat = self.explain(pesan, top=1)
        if not kandidat:
            return None, 0.0
        best = kandidat[0]
        if best["score"] < self.threshold:
            return None, best["score"]
        return best["intent"], best["score"]

    def reply(self, pesan):
        if not pesan or not pesan.strip():
            return {"reply": "Pesannya masih kosong.", "intent": None, "score": 0.0}
        tag, skor = self.classify(pesan)
        if tag is None:
            teks = random.choice(self.theme["fallback"])
        else:
            teks = random.choice(self._responses[tag])
        teks = teks.replace("{nama_bot}", self.theme["bot_name"])
        return {"reply": teks, "intent": tag, "score": skor}