"""Write docs/data/towns.json: the town selector index (name, place, era, claim count, footer text)."""
import json
cfg=json.load(open("data/towns.json")); out=[]
FOOT={"bodie":"Sources: Internet Archive, California Revealed, Mammoth Museum. Public domain newspapers.",
      "bangalore":"Sources: Internet Archive. Public domain gazetteers (Bangalore Gazetteer 1875, Rice's Mysore gazetteers).",
      "coorg":"Sources: Internet Archive. Public domain gazetteers and manuals of Coorg from the 1870s.",
      "hyderabad":"Sources: Internet Archive. Public domain books on Hyderabad from 1884 to 1910.",
      "mumbai":"Sources: Internet Archive. Public domain Bombay city gazetteers (1909, 1910) and the Imperial Gazetteer."}
for slug,c in cfg.items():
    d="" if slug=="bodie" else slug+"/"
    F=json.load(open(f"docs/data/{d}facts.json"))
    out.append({"slug":slug,"name":c["name"],"place":c["place"],"era":c["era"],"dir":d,"claims":len(F),"footer":FOOT[slug]})
json.dump(out,open("docs/data/towns.json","w"),indent=1); print([(o["slug"],o["claims"]) for o in out])
