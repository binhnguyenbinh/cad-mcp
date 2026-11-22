"""Bản vẽ A3 nhà ở riêng lẻ 5 tầng vẽ theo vn_std (quy cách VN port từ text_to_autocad).

Chạy: python examples/nha5_vn_std.py   (AutoCAD phải đang mở)
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession, StdioServerParameters, stdio_client  # noqa: E402
from vn_std import VNSheet  # noqa: E402

SERVER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server.py")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "out")

W, D = 5000.0, 16000.0          # nhà 5.0 x 16.0 m
LV = [0.0, 3600.0, 6900.0, 10200.0, 13500.0, 16800.0]
LAB = ["±0.000", "+3.600", "+6.900", "+10.200", "+13.500", "+16.800"]


async def draw(s: VNSheet):
    await s.setup_layers()

    # ---- khung A3 + khung tên
    li, ot, rx, ry = await s.frame(420, 297)
    await s.title_block(rx - s.u(180), ot, 180, 50, rows=[
        ("CONG TRINH: NHA O RIENG LE 5 TANG", "BAN VE: KT-01"),
        ("DIA DIEM: PHUONG BAI CHAY - HA LONG", "TY LE: 1/100"),
        ("CHU DAU TU: ........................", "NGAY: 22/11/2026"),
        ("DON VI LAP: DOI CS PCCC & CNCH KV4", "NGUOI VE: HERMES / cad-mcp"),
    ])

    # ================= MẶT BẰNG TẦNG 2-5 =================
    px, py = 4000.0, 7000.0
    await s.axis_grid([px + 100, px + W - 100], [py + 100, py + 9050, py + D - 100],
                      px - 1800, py - 1800, px + W + 1800, py + D + 1800)

    # tường có lỗ mở (cắt poché đúng chỗ cửa/cửa sổ)
    await s.wall_run(px, py, px + W, py, 200, [(600, 1800)])                 # trước: cửa sổ PN1
    await s.wall_run(px, py + D - 200, px + W, py + D - 200, 200, [(3000, 4200)])   # sau: cửa sổ PN2
    await s.wall_run(px, py, px, py + D, 200, [(3000, 4200), (10500, 11700)])       # trái
    await s.wall_run(px + W - 200, py, px + W - 200, py + D, 200, [(13400, 14200)])  # phải: WC
    await s.wall_run(px, py + 9000, px + W, py + 9000, 100,
                     [(800, 1700), (3000, 3900)])                            # vách ngăn

    await s.stair(px + 200, py + 12900, px + 2300, py + 15800)
    await s.rect(px + 3100, py + 12900, px + 4800, py + 14900, "A-FURN-INT")
    await s.circle(px + 4100, py + 14200, 150, "A-FURN-INT")

    await s.door(px, py + 1700, 900, 90)                       # cửa PN1 (mở vào phòng)
    await s.door(px + 3000, py + 9100, 900, 90)                # cửa PN2
    await s.door(px + 2300, py + 12900, 800, 0)                # cửa WC

    await s.window(px + 600, py, 1200)                         # trước
    await s.window(px + 3000, py + D - 200, 1200)              # sau
    await s.window(px, py + 3000, 1200, vertical=True)         # trái - PN1
    await s.window(px, py + 10500, 1200, vertical=True)        # trái - PN2
    await s.window(px + W - 200, py + 13400, 800, vertical=True)   # phải - WC

    await s.text(px + 900, py + 4200, "PHONG NGU 1", 3.0, "A-TITL-TEXT")
    await s.text(px + 900, py + 11800, "PHONG NGU 2", 3.0, "A-TITL-TEXT")
    await s.text(px + 900, py + 10300, "HANH LANG", 2.5, "A-TITL-TEXT")
    await s.text(px + 3300, py + 13500, "WC", 2.5, "A-TITL-TEXT")
    await s.text(px + 500, py + 12600, "CAU THANG", 2.2, "A-STAIR")
    await s.text(px + W / 2, py + D + 3400, "MAT BANG TANG 2-5   (TL 1:100)", 4.0,
                 "A-TITL-TEXT", "center")

    await s.dim_h(px, px + W, py, py - 1200, "5000")
    await s.dim_v(py, py + 9000, px, px - 1200, "9000")
    await s.dim_v(py + 9000, py + D, px, px - 1200, "7000")
    await s.dim_v(py, py + D, px + W, px + W + 1200, "16000")

    # mũi tên hướng bắc
    nx, ny, nr = px + W + 3200, py + D + 2200, s.u(6)
    await s.circle(nx, ny, nr, "A-AXIS-GRID")
    await s.poly([(nx, ny + nr), (nx - nr * 0.35, ny - nr * 0.6),
                  (nx, ny - nr * 0.25), (nx + nr * 0.35, ny - nr * 0.6)], True, "A-AXIS-GRID")
    await s.text(nx, ny + nr + s.u(1), "B", 3.5, "A-AXIS-GRID", "center")

    # ================= MẶT ĐỨNG CHÍNH =================
    ex, ey = 20000.0, 7000.0
    await s.rect(ex, ey, ex + W, ey + 16800, "A-WALL-STR")
    for lv in LV[1:]:
        await s.line(ex, ey + lv, ex + W, ey + lv, "A-WALL-STR")
    await s.line(ex - 1200, ey - 250, ex + W + 1200, ey - 250, "A-WALL-STR")   # vỉa hè
    await s.rect(ex + 200, ey + 16800, ex + 2400, ey + 17900, "A-WALL-STR")    # tum thang
    await s.text(ex + 2600, ey + 17150, "TUM THANG", 2.0, "A-TITL-TEXT")

    await s.rect(ex + 1500, ey, ex + 3300, ey + 2400, "A-GLAZ-DOOR")           # cửa chính
    for y0 in LV[1:5]:
        await s.rect(ex + 1500, ey + y0 + 900, ex + 3300, ey + y0 + 2400, "A-GLAZ-DOOR")
        await s.line(ex + 2400, ey + y0 + 900, ex + 2400, ey + y0 + 2400, "A-GLAZ-DOOR")
    await s.rect(ex + 1500, ey + LV[5] + 900, ex + 3300, ey + LV[5] + 1800, "A-GLAZ-DOOR")

    names = ["TANG 1", "TANG 2", "TANG 3", "TANG 4", "TANG 5", "MAI"]
    for lv, lab, nm in zip(LV, LAB, names):
        await s.level(ex, ey + lv, lab, name=nm)
    for a, b in zip(LV, LV[1:]):
        await s.dim_v(ey + a, ey + b, ex + W, ex + W + 1400, f"{int(b - a)}")
    await s.dim_v(ey, ey + 16800, ex, ex - 1400, "16800")
    await s.text(ex + W / 2, ey + 17900 + 1500, "MAT DUNG CHINH   (TL 1:100)", 4.0,
                 "A-TITL-TEXT", "center")

    # ================= GHI CHÚ =================
    await s.note_block(28500, 26000, "GHI CHU KY THUAT", [
        "1. Nha o rieng le 5 tang, kich thuoc 5.0 x 16.0 m;",
        "   dien tich san 80 m2/tang, tong dien tich san 400 m2.",
        "2. Cao do: tang 1 = 3.60 m; tang 2-5 = 3.30 m;",
        "   tong chieu cao nha 16.80 m tinh tu vi he.",
        "3. Cau thang bo 2 ve, moi ve rong 1.10 m.",
        "4. Loi thoat nan: cua chinh tang 1 + cua so cac tang.",
        "5. Tum thang 2.2 x 1.1 m = 2.42 m2 = 3.0% DT mai",
        "   (<= 30% - Muc 1.4.50 QCVN 06:2022/BXD).",
        "6. Tuong ngoai day 200 mm, vach ngan 100 mm.",
        "7. Tham chieu: QCVN 04:2021/BXD, QCVN 06:2022/BXD,",
        "   QCVN 07:2016/BXD, ND 06/2021/ND-CP.",
    ], h_mm=2.5, line_mm=6.5, width_mm=115)

    await s.call("zoom_extents")


async def main():
    os.makedirs(OUT, exist_ok=True)
    params = StdioServerParameters(command=sys.executable, args=[SERVER], env={**os.environ})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as sess:
            await sess.initialize()
            s = VNSheet(sess, scale=100)
            await draw(s)
            await s.call("save", path=os.path.join(OUT, "nha_5_tang_vn.dwg"), overwrite=True)
            import json
            res = await sess.call_tool("list_entities", {"limit": 1200})
            ents = [json.loads(c.text) for c in res.content if c.text.strip().startswith("{")]
            from collections import Counter
            print("ENTITIES", len(ents), dict(Counter(e["type"] for e in ents)))
            print("ERRORS", len(s.errors))
            for e in s.errors[:5]:
                print("  ", e)


if __name__ == "__main__":
    asyncio.run(main())
