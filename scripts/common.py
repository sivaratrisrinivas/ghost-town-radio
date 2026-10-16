import re,hashlib,json,os
def norm(s):
    """Whitespace-only normalization. Case, punctuation, OCR errors are kept exactly."""
    return re.sub(r"\s+"," ",s).strip()
def split_of(doc_id):
    """Frozen split: sha256(doc_id) mod 5 == 0 -> held-out (about 20% of docs)."""
    return "heldout" if int(hashlib.sha256(doc_id.encode()).hexdigest(),16)%5==0 else "dev"
def load_meta(): return {m["id"]:m for m in json.load(open("data/corpus_meta.json"))}
def doc_text(m): return open(m["text_file"]).read()
