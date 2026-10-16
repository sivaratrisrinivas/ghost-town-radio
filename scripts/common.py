import re,hashlib,json,os
TOWN=os.environ.get("TOWN","bodie")
LEGACY=(TOWN=="bodie")
def P(rel):
    """Data path for the current town. Bodie keeps its original paths."""
    if LEGACY: return "data/"+rel
    d=f"data/towns/{TOWN}"; os.makedirs(d,exist_ok=True); return f"{d}/{rel}"
def DOCS(rel):
    """Output path under docs/data for the current town."""
    if LEGACY: return "docs/data/"+rel
    d=f"docs/data/{TOWN}"; os.makedirs(d,exist_ok=True); return f"{d}/{rel}"
def EV(rel): return "evals/"+rel if LEGACY else f"evals/{TOWN}_"+rel
def norm(s):
    """Whitespace-only normalization. Case, punctuation, OCR errors are kept exactly."""
    return re.sub(r"\s+"," ",s).strip()
def split_of(doc_id):
    """Frozen split: sha256(id) mod 5 == 0 -> held-out (about 20%). Bodie splits by document, the book towns by passage."""
    return "heldout" if int(hashlib.sha256(doc_id.encode()).hexdigest(),16)%5==0 else "dev"
def load_meta(): return {m["id"]:m for m in json.load(open(P("corpus_meta.json")))}
def doc_text(m): return open(m["text_file"]).read()
def town_cfg(): return json.load(open("data/towns.json"))[TOWN]
