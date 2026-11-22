"""Nha o rieng le 5 tang 5.0 x 16.0 m - mat bang tang 2-5 + mat dung chinh, ve qua MCP cad-mcp."""
import asyncio, base64, os, sys
from mcp import ClientSession, StdioServerParameters, stdio_client

SERVER = r"D:\project\cad-mcp\server.py"
OUT = r"D:\project\cad-mcp\tests\out"
os.makedirs(OUT, exist_ok=True)

W, D = 5000.0, 16000.0          # 5.0 x 16.0 m
XE = 20000.0                    # x goc mat dung
LV = [0.0, 3600.0, 6900.0, 10200.0, 13500.0, 16800.0]   # cao do 5 tang
T = 200.0                       # be day tuong ngoai


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER], env={**os.environ})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            n_err = 0

            async def call(tool, **kw):
                nonlocal n_err
                res = await s.call_tool(tool, kw)
                if res.is_error:
                    n_err += 1
                    print("ERR", tool, kw, [getattr(c, "text", "") for c in res.content][:1])
                return res

            # ---------- LAYERS ----------
            await call("layer", name="TRUC", color=1, make_current=False)
            await call("layer", name="TUONG", color=7, make_current=False)
            await call("layer", name="CAU-THANG", color=3, make_current=False)
            await call("layer", name="CUA", color=4, make_current=False)
            await call("layer", name="NOI-THAT", color=2, make_current=False)
            await call("layer", name="GHI-CHU", color=6, make_current=False)
            await call("layer", name="KICH-THUOC", color=5, make_current=False)
            await call("layer", name="KHUNG-TEN", color=7, make_current=False)

            # ---------- PANEL A: MAT BANG TANG 2-5 ----------
            # truc
            for x in (0, W):
                await call("line", x1=x, y1=-800, x2=x, y2=D + 800, layer="TRUC")
            for y in (0, 9000, D):
                await call("line", x1=-800, y1=y, x2=W + 800, y2=y, layer="TRUC")
            for x, lab in ((0, "1"), (W, "2")):
                await call("circle", x=x, y=D + 1500, r=250, layer="TRUC")
                await call("text", x=x - 100, y=D + 1400, value=lab, height=300, layer="TRUC")
            for y, lab in ((0, "A"), (9000, "B"), (D, "C")):
                await call("circle", x=-1500, y=y, r=250, layer="TRUC")
                await call("text", x=-1600, y=y - 100, value=lab, height=300, layer="TRUC")

            # tuong ngoai + tuong ngan
            await call("polyline", points=[[0, 0], [W, 0], [W, D], [0, D]], closed=True, layer="TUONG")
            await call("polyline", points=[[T, T], [W - T, T], [W - T, D - T], [T, D - T]],
                       closed=True, layer="TUONG")
            await call("line", x1=T, y1=8900, x2=W - T, y2=8900, layer="TUONG")
            await call("line", x1=T, y1=9100, x2=W - T, y2=9100, layer="TUONG")

            # cau thang: 2 ve, moi ve rong 1100
            await call("rectangle", x1=200, y1=12900, x2=2400, y2=15700, layer="CAU-THANG")
            for y in range(13100, 15600, 300):
                await call("line", x1=300, y1=y, x2=1200, y2=y, layer="CAU-THANG")
                await call("line", x1=1400, y1=y, x2=2300, y2=y, layer="CAU-THANG")
            await call("line", x1=1300, y1=13000, x2=1300, y2=15600, layer="CAU-THANG")
            await call("line", x1=700, y1=13300, x2=700, y2=15300, layer="CAU-THANG")   # mui ten huong
            await call("line", x1=1900, y1=15300, x2=1900, y2=13300, layer="CAU-THANG")

            # WC
            await call("rectangle", x1=3000, y1=12900, x2=4800, y2=14900, layer="NOI-THAT")
            await call("circle", x=4200, y=14200, r=150, layer="NOI-THAT")

            # cua di: 1 o cua thong phong + 1 cua vao cau thang
            await call("arc", x=2000, y=9000, r=900, start_deg=0, end_deg=90, layer="CUA")
            await call("line", x1=2000, y1=9000, x2=2000, y2=9900, layer="CUA")
            await call("arc", x=2400, y=13500, r=900, start_deg=90, end_deg=180, layer="CUA")
            await call("line", x1=2400, y1=13500, x2=1500, y2=13500, layer="CUA")

            # cua so tren tuong ngoai
            for x1, x2 in ((800, 2000), (3000, 4200)):
                await call("rectangle", x1=x1, y1=0, x2=x2, y2=T, layer="CUA")
                await call("rectangle", x1=x1, y1=D - T, x2=x2, y2=D, layer="CUA")
            for y1, y2 in ((3000, 4200),):
                await call("rectangle", x1=0, y1=y1, x2=T, y2=y2, layer="CUA")
                await call("rectangle", x1=W - T, y1=y1, x2=W, y2=y2, layer="CUA")

            # ghi chu phong
            await call("text", x=700, y=4200, value="PHONG NGU 1", height=280, layer="GHI-CHU")
            await call("text", x=700, y=11800, value="PHONG NGU 2", height=280, layer="GHI-CHU")
            await call("text", x=500, y=15000, value="CAU THANG", height=220, layer="CAU-THANG")
            await call("text", x=3350, y=13500, value="WC", height=250, layer="GHI-CHU")
            await call("text", x=700, y=10500, value="HANH LANG", height=250, layer="GHI-CHU")
            await call("text", x=700, y=D + 2500, value="MAT BANG TANG 2-5   (TL 1:100)", height=450,
                       layer="GHI-CHU")

            # kich thuoc
            await call("dim_aligned", x1=0, y1=0, x2=W, y2=0, offset=-900, layer="KICH-THUOC")
            await call("dim_aligned", x1=0, y1=9000, x2=0, y2=D, offset=1500, layer="KICH-THUOC")
            await call("dim_aligned", x1=0, y1=0, x2=0, y2=9000, offset=1500, layer="KICH-THUOC")
            await call("dim_aligned", x1=W, y1=0, x2=W, y2=D, offset=-1500, layer="KICH-THUOC")

            # ---------- PANEL B: MAT DUNG CHINH ----------
            await call("polyline", points=[[XE, 0], [XE + W, 0], [XE + W, 16800], [XE, 16800]],
                       closed=True, layer="TUONG")
            for y in LV[1:]:
                await call("line", x1=XE, y1=y, x2=XE + W, y2=y, layer="TUONG")
            # san / via he
            await call("line", x1=XE - 1200, y1=-250, x2=XE + W + 1200, y2=-250, layer="TUONG")
            # tum thang (<= 30% DT mai)
            await call("rectangle", x1=XE + 200, y1=16800, x2=XE + 2400, y2=17900, layer="TUONG")
            await call("text", x=XE + 300, y=17300, value="TUM THANG", height=200, layer="GHI-CHU")
            # cua so tung tang + cua chinh tang 1
            await call("rectangle", x1=XE + 1500, y1=0, x2=XE + 3300, y2=2400, layer="CUA")
            for y0 in LV[1:5]:
                await call("rectangle", x1=XE + 1500, y1=y0 + 900, x2=XE + 3300, y2=y0 + 2400, layer="CUA")
                await call("line", x1=XE + 2400, y1=y0 + 900, x2=XE + 2400, y2=y0 + 2400, layer="CUA")
            await call("rectangle", x1=XE + 1500, y1=LV[5] + 900, x2=XE + 3300, y2=LV[5] + 1800, layer="CUA")
            # kich thuoc cao do
            await call("dim_aligned", x1=XE, y1=0, x2=XE, y2=16800, offset=1500, layer="KICH-THUOC")
            for a, b in zip(LV, LV[1:]):
                await call("dim_aligned", x1=XE + W, y1=a, x2=XE + W, y2=b, offset=-1600, layer="KICH-THUOC")
            await call("text", x=XE + 800, y=18800, value="MAT DUNG CHINH   (TL 1:100)", height=450,
                       layer="GHI-CHU")
            for y0, lab in zip(LV[:5], ("TANG 1", "TANG 2", "TANG 3", "TANG 4", "TANG 5")):
                await call("text", x=XE + W + 1800, y=y0 + 1200, value=lab, height=250, layer="GHI-CHU")

            # ---------- GHI CHU KY THUAT ----------
            gx, gy = 9000.0, 13500.0
            await call("text", x=gx, y=gy, value="GHI CHU KY THUAT", height=400, layer="GHI-CHU")
            notes = [
                "1. Nha o rieng le 5 tang, kich thuoc 5.0 x 16.0 m.",
                "   Dien tich san 80 m2/tang, tong san 400 m2.",
                "2. Cao do: tang 1 = 3.60 m; tang 2-5 = 3.30 m;",
                "   tong chieu cao nha 16.80 m (tinh tu via he).",
                "3. Cau thang bo 2 ve, moi ve rong 1.10 m;",
                "   loi thoat nan qua cua chinh va cua so cac tang.",
                "4. Tum thang 2.2 x 1.1 m = 2.42 m2 = 3.0% DT mai",
                "   (<= 30% - Muc 1.4.50 QCVN 06:2022/BXD).",
                "5. Tuong ngoai day 200 mm, tuong ngan 100-200 mm.",
                "6. Tham chieu: QCVN 04:2021/BXD, QCVN 06:2022/BXD,",
                "   NĐ 06/2021/ND-CP ve an toan xay dung.",
            ]
            y = gy - 700
            for line in notes:
                await call("text", x=gx, y=y, value=line, height=280, layer="GHI-CHU")
                y -= 480

            # ---------- KHUNG TEN ----------
            bx, by = 9000.0, -7500.0
            await call("rectangle", x1=bx, y1=by, x2=bx + 11000, y2=by + 2600, layer="KHUNG-TEN")
            await call("line", x1=bx, y1=by + 1300, x2=bx + 11000, y2=by + 1300, layer="KHUNG-TEN")
            await call("line", x1=bx + 7000, y1=by, x2=bx + 7000, y2=by + 2600, layer="KHUNG-TEN")
            tb = [
                (bx + 200, by + 1900, "CHU DAU TU: ...............................", 300),
                (bx + 200, by + 900, "CONG TRINH: NHA O RIENG LE 5 TANG", 350),
                (bx + 7300, by + 1900, "BAN VE: MAT BANG TANG 2-5 + MAT DUNG CHINH", 280),
                (bx + 7300, by + 1500, "TY LE: 1/100", 280),
                (bx + 7300, by + 1100, "SO HIEU: KT-01", 280),
                (bx + 7300, by + 600, "NGAY: 22/11/2026", 280),
                (bx + 7300, by + 200, "NGUOI VE: HERMES / cad-mcp MCP", 260),
            ]
            for x, y2, val, h in tb:
                await call("text", x=x, y=y2, value=val, height=h, layer="GHI-CHU")

            await call("zoom_extents")
            r1 = await s.call_tool("list_entities", {"limit": 800})
            import json
            ents = [json.loads(c.text) for c in r1.content if c.text.strip().startswith("{")]
            from collections import Counter
            print("ENTITIES", len(ents), dict(Counter(e["type"] for e in ents)))
            await call("save", path=OUT + r"\nha_5_tang.dwg", overwrite=True)
            img = await s.call_tool("screenshot", {"zoom_extents": True})
            for c in img.content:
                d = getattr(c, "data", None)
                if d:
                    open(OUT + r"\nha_5_tang.png", "wb").write(base64.b64decode(d))
                    print("PNG ok")
            print("ERRORS", n_err)
    print("DONE")


asyncio.run(main())
