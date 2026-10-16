import asyncio,json,time,math,glob,os
from playwright.async_api import async_playwright
T=json.load(open("tl.json")); tl=T["tl"]; total=T["total"]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/opt/google/chrome/chrome",args=["--autoplay-policy=no-user-gesture-required","--no-sandbox"])
        c=await b.new_context(viewport={"width":1280,"height":720},record_video_dir="vid",record_video_size={"width":1280,"height":720})
        t_ctx=time.monotonic(); pg=await c.new_page()
        await pg.goto("http://localhost:8765/#bodie/h5"); await pg.wait_for_selector("#schedule button"); await pg.wait_for_timeout(500)
        t0=time.monotonic(); print("load offset",t0-t_ctx)
        async def at(x): 
            d=x-(time.monotonic()-t0)
            if d>0: await pg.wait_for_timeout(d*1000)
        await at(tl["towns"]+0.5)
        for s in ["bangalore","coorg","hyderabad","mumbai"]:
            await pg.click(f'#towns [data-slug="{s}"]'); await pg.wait_for_timeout(1500)
        await at(tl["knob"]+0.4)
        bb=await (await pg.query_selector("#knob")).bounding_box(); cx,cy=bb["x"]+bb["width"]/2,bb["y"]+bb["height"]/2
        await pg.mouse.move(cx,cy-40); await pg.mouse.down()
        n=60
        for i in range(n+1):
            a=-math.pi/2+math.radians(150)*i/n*(1 if i<=n else 1); await pg.mouse.move(cx+40*math.cos(a),cy+40*math.sin(a)); await pg.wait_for_timeout(45)
        await pg.mouse.up(); await pg.wait_for_timeout(700)
        h=int(await pg.get_attribute("#knob","aria-valuenow")); print("hour after drag",h)
        await pg.focus("#knob")
        for i in range(abs(h-17)): await pg.keyboard.press("ArrowLeft" if h>17 else "ArrowRight"); await pg.wait_for_timeout(110)
        await at(tl["dj"]-0.9)
        await pg.click("#play")
        await pg.wait_for_timeout(60); await pg.click("#skip")
        print("djstart",time.monotonic()-t0,"expected",tl["dj"])
        await at(tl["quiet"]); await pg.click("#schedule li:nth-child(1) button")
        await pg.wait_for_timeout(1200); await pg.mouse.wheel(0,500)
        await at(tl["nums"]-0.3); await pg.mouse.wheel(0,-600)
        await at(total); 
        await c.close(); await b.close()
asyncio.run(main())
