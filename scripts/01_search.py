"""Enumerate Bodie-related Internet Archive items. Polite: custom UA, 1 req/2s."""
import json,time,requests
UA={"User-Agent":"GhostTownRadio/0.1 (research project; github.com/sivaratrisrinivas)"}
qs=['title:("Bodie Chronicle")','title:("Bodie Standard")','title:("Bodie Daily Free Press") OR title:("Bodie Morning News") OR title:("Bodie Evening Miner")','title:(bodie) AND collection:(southernmonohistorical OR californiarevealed)','title:(bodie) AND subject:(oral history)']
out={}
for q in qs:
    r=requests.get("https://archive.org/advancedsearch.php",params={"q":q,"fl[]":["identifier","title","date","rights","licenseurl","collection"],"rows":300,"output":"json"},headers=UA,timeout=60).json()["response"]
    print(q,r["numFound"])
    for d in r["docs"]: out[d["identifier"]]=d
    time.sleep(2)
json.dump(out,open("data/search_hits.json","w"),indent=1)
print(len(out))
