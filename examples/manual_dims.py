"""Ve dim thu cong (line + tick + text) thay AddDimAligned, vi dim object khong plot duoc."""
import asyncio, json, os, sys
from mcp import ClientSession, StdioServerParameters, stdio_client

SERVER = r"D:\project\cad-mcp\server.py"
OUT = r"D:\project\cad-mcp\tests\out"
W, D, XE = 5000.0, 16000.0, 20000.0
LV = [0.0, 3600.0, 6900.0, 10200.0, 13500.0, 16800.0]


async def main():
    p = StdioServerParameters(command=sys.executable, args=[SERVER], env={**os.environ})
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            nerr = 0

            async def call(tool, **kw):
                nonlocal nerr
                res = await s.call_tool(tool, kw)
                if res.is_error:
                    nerr += 1
                    print("ERR", tool, [getattr(c, "text", "") for c in res.content][:1])
                return res

            # xoa dim object cu
            r1 = await s.call_tool("list_entities", {"limit": 900, "layer": "KICH-THUOC"})
            for c in r1.content:
                if c.text.strip().startswith("{"):
                    await call("delete", handle=json.loads(c.text)["handle"])

            H, TK = 260, 90          # chieu cao chu so do, nua chieu dai tick

            async def txt(x, y, val, h=H, layer="KICH-THUOC", anchor="center"):
                n = len(val)
                if anchor == "center":
                    x = x - n * h * 0.30
                await call("text", x=x, y=y, value=val, height=h, layer=layer)

            async def dim_h(x1, x2, y, ydim, label):
                await call("line", x1=x1, y1=y, x2=x1, y2=ydim + (300 if ydim < y else -300), layer="KICH-THUOC")
                await call("line", x1=x2, y1=y, x2=x2, y2=ydim + (300 if ydim < y else -300), layer="KICH-THUOC")
                await call("line", x1=x1, y1=ydim, x2=x2, y2=ydim, layer="KICH-THUOC")
                for xx in (x1, x2):
                    await call("line", x1=xx - TK, y1=ydim - TK, x2=xx + TK, y2=ydim + TK, layer="KICH-THUOC")
                await txt((x1 + x2) / 2, ydim + (90 if ydim < y else -H - 90), label)

            async def dim_v(y1, y2, x, xdim, label):
                await call("line", x1=x, y1=y1, x2=xdim + (300 if xdim > x else -300), y2=y1, layer="KICH-THUOC")
                await call("line", x1=x, y1=y2, x2=xdim + (300 if xdim > x else -300), y2=y2, layer="KICH-THUOC")
                await call("line", x1=xdim, y1=y1, x2=xdim, y2=y2, layer="KICH-THUOC")
                for yy in (y1, y2):
                    await call("line", x1=xdim - TK, y1=yy - TK, x2=xdim + TK, y2=yy + TK, layer="KICH-THUOC")
                await txt(xdim + (60 if xdim > x else -len(label) * H * 0.60 - 60), (y1 + y2) / 2, label)

            # MAT BANG
            await dim_h(0, W, 0, -900, "5000")
            await dim_v(0, 9000, 0, -1600, "9000")
            await dim_v(9000, D, 0, -1600, "7000")
            await dim_v(0, D, W, W + 1600, "16000")
            # MAT DUNG
            await dim_v(0, 16800, XE, XE - 2000, "16800")
            for a, b in zip(LV, LV[1:]):
                await dim_v(a, b, XE + W, XE + W + 1800, f"{int(round(b - a))}")
            # cao do
            for lv, lab in zip(LV, ("+-0.000", "+3.600", "+6.900", "+10.200", "+13.500", "+16.800")):
                await call("line", x1=XE, y1=lv, x2=XE - 700, y2=lv, layer="KICH-THUOC")
                await txt(XE - 7300, lv + 100, lab, h=240, anchor="left")

            await call("zoom_extents")
            await call("save", path=OUT + r"\nha_5_tang.dwg", overwrite=True)
            r2 = await s.call_tool("list_entities", {"limit": 900})
            ents = [json.loads(c.text) for c in r2.content if c.text.strip().startswith("{")]
            from collections import Counter
            print("TOTAL", len(ents), dict(Counter(e["type"] for e in ents)), "ERR", nerr)
    print("DONE")


asyncio.run(main())
