"""vn_std — bộ primitive vẽ bản vẽ kỹ thuật theo quy cách VN (TCVN/AIA) trên cad-mcp MCP.

Port từ D:/project/text_to_autocad:
  - pacc_common.py   : tên layer AIA, dim tick 45°, ký hiệu cao độ tam giác, khung tên auto-fit
  - sodo/pacc_sheet.py: quy ước sheet A3, margin, layer PACC, bảng chú giải

Quy ước: 1 unit model = 1 mm thật. Tham số *_mm là mm TRÊN GIẤY, tự nhân scale 1:S.
"""
from __future__ import annotations

import math

# (tên layer, màu ACI, linetype, lineweight 1/100 mm)
LAYERS = [
    ("A-WALL-STR", 7, "Continuous", 50),
    ("A-WALL-HATCH", 8, "Continuous", 13),
    ("A-GLAZ-DOOR", 4, "Continuous", 35),
    ("A-STAIR", 3, "Continuous", 25),
    ("A-FURN-INT", 8, "Continuous", 18),
    ("A-AXIS-GRID", 1, "CENTER", 18),
    ("A-DIMS-MEAS", 3, "Continuous", 18),
    ("A-TITL-TEXT", 7, "Continuous", 25),
    ("A-BORD-FRAM", 7, "Continuous", 50),
    ("A-ROAD-STRT", 9, "Continuous", 25),
    ("A-TREE-VEGE", 92, "Continuous", 25),
    ("PACC-FIRE", 1, "Continuous", 50),
    ("PACC-HOSE", 1, "Continuous", 40),
    ("PACC-ESCAPE", 92, "Continuous", 50),
    ("PACC-SYMBOL", 2, "Continuous", 40),
    ("PACC-TACT-TEXT", 1, "Continuous", 25),
]

SETUP_CODE = r'''
import math
for lt in ("CENTER", "DASHED", "HIDDEN"):
    try:
        doc.Linetypes.Load(lt, "acadiso.lin")
    except Exception:
        pass
SPEC = %r
for name, col, lt, lw in SPEC:
    try:
        L = doc.Layers.Item(name)
    except Exception:
        L = doc.Layers.Add(name)
    L.color = col
    try:
        L.Linetype = lt
    except Exception:
        pass
    try:
        L.Lineweight = lw
    except Exception:
        pass
result = {"layers": len(SPEC)}
''' % (LAYERS,)


class VNSheet:
    """Bọc MCP ClientSession, vẽ theo quy cách VN. scale=100 nghĩa là in 1:100."""

    def __init__(self, session, scale: int = 100):
        self.s = session
        self.S = float(scale)
        self.errors: list[str] = []

    # ---------------------------------------------------------------- helpers
    def u(self, mm: float) -> float:
        """mm trên giấy -> đơn vị model."""
        return mm * self.S

    async def call(self, tool: str, **kw):
        res = await self.s.call_tool(tool, kw)
        if res.is_error:
            self.errors.append(f"{tool}: {[getattr(c, 'text', '') for c in res.content][:1]}")
            return None
        txt = res.content[0].text if res.content else ""
        return txt

    @staticmethod
    def tw(text: str, h: float) -> float:
        """Bề rộng xấp xỉ của text theo chiều cao h (hệ số 0.95 đo thực tế với txt.shx)."""
        return len(text) * h * 0.95

    # ---------------------------------------------------------------- setup
    async def setup_layers(self):
        await self.call("run_python", code=SETUP_CODE)

    # ---------------------------------------------------------------- text
    async def text(self, x, y, value, h_mm=2.5, layer="A-TITL-TEXT", align="left", width_mm=None):
        """align: left|center|right. width_mm: tự thu nhỏ chữ cho vừa bề rộng."""
        h = self.u(h_mm)
        if width_mm:
            h = min(h, self.u(width_mm) / max(len(value) * 0.95, 1))
        w = self.tw(value, h)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        await self.call("text", x=x, y=y, value=value, height=h, layer=layer)
        return h

    async def mtext(self, x, y, value, h_mm=2.5, width_mm=60, layer="A-TITL-TEXT"):
        return await self.call("mtext", x=x, y=y, value=value, width=self.u(width_mm),
                               height=self.u(h_mm), layer=layer)

    # ---------------------------------------------------------------- hình học
    async def line(self, x1, y1, x2, y2, layer="A-WALL-STR"):
        return await self.call("line", x1=x1, y1=y1, x2=x2, y2=y2, layer=layer)

    async def rect(self, x1, y1, x2, y2, layer="A-WALL-STR", hatch=None):
        h = await self.call("rectangle", x1=x1, y1=y1, x2=x2, y2=y2, layer=layer)
        if hatch and h:
            await self.call("hatch", boundary_handles=[h], pattern=hatch,
                            scale=max(self.u(1.0), 1), layer="A-WALL-HATCH")
        return h

    async def poly(self, pts, closed=True, layer="A-WALL-STR"):
        return await self.call("polyline", points=[list(p) for p in pts], closed=closed, layer=layer)

    async def circle(self, x, y, r, layer="A-TITL-TEXT"):
        return await self.call("circle", x=x, y=y, r=r, layer=layer)

    async def arc(self, x, y, r, a0, a1, layer="A-GLAZ-DOOR"):
        return await self.call("arc", x=x, y=y, r=r, start_deg=a0, end_deg=a1, layer=layer)

    # ---------------------------------------------------------------- kiến trúc
    async def wall(self, x1, y1, x2, y2, t=200, layer="A-WALL-STR", hatch="SOLID"):
        """Tường đặc: 2 nét mặt + hatch. t = bề dày thật (mm)."""
        if abs(y2 - y1) < 1e-9:                      # tường ngang
            for yy in (y1, y1 + t):
                await self.line(x1, yy, x2, yy, layer)
            h = await self.call("rectangle", x1=x1, y1=y1, x2=x2, y2=y1 + t, layer=layer)
        else:                                        # tường đứng
            for xx in (x1, x1 + t):
                await self.line(xx, y1, xx, y2, layer)
            h = await self.call("rectangle", x1=x1, y1=y1, x2=x1 + t, y2=y2, layer=layer)
        if hatch and h:
            await self.call("hatch", boundary_handles=[h], pattern=hatch,
                            scale=1 if hatch == "SOLID" else max(self.u(0.5), 1),
                            layer="A-WALL-HATCH")
        return h

    async def wall_run(self, x1, y1, x2, y2, t=200, openings=(), layer="A-WALL-STR", hatch="SOLID"):
        """Tường có lỗ mở: cắt thành các đoạn đặc nằm giữa các lỗ (openings theo trục chạy)."""
        horiz = abs(y2 - y1) < 1e-9
        a, b = (x1, x2) if horiz else (y1, y2)
        cur, segs = a, []
        for o0, o1 in sorted(openings):
            if o0 > cur:
                segs.append((cur, min(o0, b)))
            cur = max(cur, o1)
        if cur < b:
            segs.append((cur, b))
        for s0, s1 in segs:
            if horiz:
                await self.wall(s0, y1, s1, y1, t, layer, hatch)
            else:
                await self.wall(x1, s0, x1, s1, t, layer, hatch)

    async def window(self, x, y, length, vertical=False, t=200):
        """Cửa sổ: 3 nét song song trong ô tường."""
        if vertical:
            for xx in (x, x + t / 2, x + t):
                await self.line(xx, y, xx, y + length, "A-GLAZ-DOOR")
        else:
            for yy in (y, y + t / 2, y + t):
                await self.line(x, yy, x + length, yy, "A-GLAZ-DOOR")

    async def door(self, x, y, width, angle_deg=0, leaf=90):
        """Cửa đi 1 cánh: bản lề tại (x,y), cung mở leaf độ, hướng angle_deg."""
        await self.arc(x, y, width, angle_deg, angle_deg + leaf, "A-GLAZ-DOOR")
        a = math.radians(angle_deg)
        await self.line(x, y, x + width * math.cos(a), y + width * math.sin(a), "A-GLAZ-DOOR")
        await self.line(x, y, x + width * math.cos(math.radians(angle_deg + leaf)),
                        y + width * math.sin(math.radians(angle_deg + leaf)), "A-GLAZ-DOOR")

    async def stair(self, x1, y1, x2, y2, flights=2, tread=300, up=True):
        """Cầu thang bộ: khung + vách giữa + bậc + mũi tên chiều đi."""
        await self.rect(x1, y1, x2, y2, "A-STAIR")
        w = (x2 - x1) / flights
        for f in range(1, flights):
            await self.line(x1 + f * w, y1, x1 + f * w, y2, "A-STAIR")
        n = max(int((y2 - y1) / tread), 2)
        step = (y2 - y1) / n
        for i in range(1, n):
            await self.line(x1, y1 + i * step, x1 + w, y1 + i * step, "A-STAIR")
            await self.line(x1 + w, y1 + i * step, x2, y1 + i * step, "A-STAIR")
        xm = (x1 + x2) / 2
        y0, y1a = (y1 + 300, y2 - 300) if up else (y2 - 300, y1 + 300)
        await self.line(xm, y0, xm, y1a, "A-STAIR")
        s = self.u(2.0)
        await self.line(xm - s, y1a - math.copysign(s, y1a - y0), xm, y1a, "A-STAIR")
        await self.line(xm + s, y1a - math.copysign(s, y1a - y0), xm, y1a, "A-STAIR")

    # ---------------------------------------------------------------- lưới trục
    async def axis_grid(self, xs, ys, x0, y0, x1, y1, bubble_mm=8, tag_x="1", tag_y="A"):
        """Lưới trục: nét CENTER + bong bóng tròn có nhãn ở 2 đầu."""
        r = self.u(bubble_mm / 2)
        for i, x in enumerate(xs):
            await self.line(x, y0, x, y1, "A-AXIS-GRID")
            await self.circle(x, y1 + r * 1.6, r, "A-AXIS-GRID")
            await self.text(x, y1 + r * 1.2, str(i + 1) if tag_x == "1" else f"{tag_x}{i+1}",
                            bubble_mm * 0.45, "A-AXIS-GRID", "center")
        for j, y in enumerate(ys):
            await self.line(x0, y, x1, y, "A-AXIS-GRID")
            await self.circle(x0 - r * 1.6, y, r, "A-AXIS-GRID")
            lab = chr(ord(tag_y) + j) if tag_y == "A" else f"{tag_y}{j+1}"
            await self.text(x0 - r * 1.6, y - r * 0.45, lab, bubble_mm * 0.45, "A-AXIS-GRID", "center")

    # ---------------------------------------------------------------- kích thước
    async def dim_h(self, x1, x2, y, ydim=None, label=None, tick_mm=1.5, text_mm=2.5):
        """Dim ngang kiểu TCVN: gạch 45° ở 2 đầu, chữ đặt trên đường dim."""
        ydim = y if ydim is None else ydim
        label = label or f"{int(round(abs(x2 - x1)))}"
        tk = self.u(tick_mm)
        ext = self.u(2.0)
        await self.line(x1, y, x1, ydim + math.copysign(ext, ydim - y), "A-DIMS-MEAS")
        await self.line(x2, y, x2, ydim + math.copysign(ext, ydim - y), "A-DIMS-MEAS")
        await self.line(x1, ydim, x2, ydim, "A-DIMS-MEAS")
        for xx in (x1, x2):
            await self.line(xx - tk, ydim - tk, xx + tk, ydim + tk, "A-DIMS-MEAS")
        h = self.u(text_mm)
        ytxt = ydim + self.u(0.8) if ydim < y else ydim - h - self.u(0.8)
        await self.text((x1 + x2) / 2, ytxt, label, text_mm, "A-DIMS-MEAS", "center")

    async def dim_v(self, y1, y2, x, xdim=None, label=None, tick_mm=1.5, text_mm=2.5):
        xdim = x if xdim is None else xdim
        label = label or f"{int(round(abs(y2 - y1)))}"
        tk = self.u(tick_mm)
        ext = self.u(2.0)
        await self.line(x, y1, xdim + math.copysign(ext, xdim - x), y1, "A-DIMS-MEAS")
        await self.line(x, y2, xdim + math.copysign(ext, xdim - x), y2, "A-DIMS-MEAS")
        await self.line(xdim, y1, xdim, y2, "A-DIMS-MEAS")
        for yy in (y1, y2):
            await self.line(xdim - tk, yy - tk, xdim + tk, yy + tk, "A-DIMS-MEAS")
        h = self.u(text_mm)
        if xdim >= x:
            await self.text(xdim + self.u(1.0), (y1 + y2) / 2 - h * 0.35, label, text_mm,
                            "A-DIMS-MEAS", "left")
        else:
            await self.text(xdim - self.u(1.0), (y1 + y2) / 2 - h * 0.35, label, text_mm,
                            "A-DIMS-MEAS", "right")

    async def level(self, x, y, value="±0.000", name="", tri_mm=2.6, text_mm=2.5):
        """Ký hiệu cao độ: tam giác ngược + đường dẫn + số cao độ."""
        w, hh = self.u(tri_mm), self.u(tri_mm * 0.8)
        await self.poly([(x, y), (x - w / 2, y + hh), (x + w / 2, y + hh)], True, "A-DIMS-MEAS")
        await self.line(x - w * 1.2, y + hh, x + self.u(14), y + hh, "A-DIMS-MEAS")
        await self.text(x + self.u(1.2), y + hh + self.u(0.6), value, text_mm, "A-DIMS-MEAS", "left")
        if name:
            await self.text(x + self.u(1.2), y + hh - self.u(2.2), name, text_mm * 0.8,
                            "A-TITL-TEXT", "left")

    # ---------------------------------------------------------------- sheet
    async def frame(self, w_mm, h_mm, left_mm=25, other_mm=10):
        """Khung bản vẽ 2 lớp theo TCVN: mép trái 25 mm, các mép 10 mm."""
        W, H = self.u(w_mm), self.u(h_mm)
        await self.rect(0, 0, W, H, "A-BORD-FRAM")
        li, ot = self.u(left_mm), self.u(other_mm)
        await self.rect(li, ot, W - ot, H - ot, "A-BORD-FRAM")
        return li, ot, W - ot, H - ot

    async def title_block(self, x, y, w_mm=180, h_mm=50, rows=None):
        """Khung tên: cột trái nội dung, cột phải (24%) tỷ lệ/số hiệu. Chữ tự fit cột."""
        rows = rows or []
        W, H = self.u(w_mm), self.u(h_mm)
        await self.rect(x, y, x + W, y + H, "A-BORD-FRAM")
        split = x + W * 0.76
        n = max(len(rows), 1)
        rh = H / n
        for i in range(1, n):
            await self.line(x, y + i * rh, x + W, y + i * rh, "A-BORD-FRAM")
        await self.line(split, y, split, y + H, "A-BORD-FRAM")
        pad = self.u(2.0)
        for i, (left, right) in enumerate(rows):
            cy = y + (n - i - 1) * rh + rh / 2
            h_mm_txt = min(h_mm / n * 0.55, 3.2)
            if left:
                await self.text(x + pad, cy - self.u(h_mm_txt) * 0.35, left, h_mm_txt,
                                "A-TITL-TEXT", "left", width_mm=w_mm * 0.76 - 6)
            if right:
                await self.text(split + pad, cy - self.u(h_mm_txt) * 0.35, right, h_mm_txt,
                                "A-TITL-TEXT", "left", width_mm=w_mm * 0.24 - 4)
        return split

    async def note_block(self, x, y, title, lines, h_mm=2.5, line_mm=6.0, width_mm=90):
        await self.text(x, y, title, h_mm * 1.25, "A-TITL-TEXT", "left", width_mm=width_mm)
        yy = y - self.u(line_mm)
        for s in lines:
            await self.text(x, yy, s, h_mm, "A-TITL-TEXT", "left", width_mm=width_mm)
            yy -= self.u(line_mm)
        return yy
