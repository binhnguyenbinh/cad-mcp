"""Sơ đồ chữa cháy (PACC) cho nhà ở riêng lẻ 5 tầng — khổ A3 tỷ lệ 1:100.

Dùng thư viện ký hiệu chuẩn C07 của D:/project/text_to_autocad (53 ký hiệu bóc từ temp_sodo.dwg).
1 unit = 1 mét. A3 @1:100 = 42 x 29.7 m.
"""
import os
import sys

import ezdxf

T2A = r"D:\project\text_to_autocad"
sys.path.insert(0, T2A)
from pacc_symbols_data import insert_pacc_symbol  # noqa: E402

OUT_DIR = r"D:\project\cad-mcp\tests\out"
DXF = os.path.join(OUT_DIR, "pacc_nha5.dxf")

doc = ezdxf.new("R2010", setup=True)
msp = doc.modelspace()

LAYERS = [
    ("PACC-CONG-TRINH", 7, 50),
    ("PACC-TUONG", 7, 35),
    ("PACC-THONG-THUY", 3, 18),
    ("PACC-DUONG", 8, 25),
    ("PACC-DUONG-VOI", 1, 50),
    ("PACC-TIA-NUOC", 4, 35),
    ("PACC-CHIEN-THUAT", 1, 50),
    ("PACC-TEXT", 7, 25),
    ("PACC-FRAME", 7, 50),
    ("PACC-LEGEND", 30, 25),
]
for name, color, lw in LAYERS:
    doc.layers.add(name, color=color, lineweight=lw)

TH = 0.25       # chiều cao chữ thường (2.5 mm trên giấy)
TF = 0.20
B = "PACC-TUONG"


def txt(s, x, y, h=TH, layer="PACC-TEXT", align="left", rot=0):
    w = len(s) * h * 0.95
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    t = msp.add_text(s, dxfattribs={"height": h, "layer": layer, "rotation": rot})
    t.dxf.insert = (x, y)
    return t


def line(x1, y1, x2, y2, layer=B):
    return msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})


def rect(x1, y1, x2, y2, layer=B):
    return msp.add_lwpolyline([(x1, y1), (x2, y1), (x2, y2), (x1, y2)], close=True,
                              dxfattribs={"layer": layer})


# catalog C07 chuẩn hoá kích thước chữ nhật nhỏ; quy đổi về kích thước thật (mét)
SYM_SCALE = {"xe_bon": 13.0, "xe_chi_huy": 9.0, "diem_xp_chay": 4.0,
             "dam_chay": 2.0, "huong_tan_cong_chinh": 3.0}


def sym(sid, x, y, scale=None, rot=0, layer=None):
    sc = scale if scale is not None else SYM_SCALE.get(sid, 1.0)
    return insert_pacc_symbol(msp, sid, insert=(x, y), scale=sc, rotation_deg=rot, layer=layer)


# ===================== KHUNG + KHUNG TÊN =====================
rect(0, 0, 42, 29.7, "PACC-FRAME")
rect(0.25, 0.1, 41.9, 29.6, "PACC-FRAME")

TBX, TBY, TBW, TBH = 23.9, 0.1, 18.0, 5.0
rect(TBX, TBY, TBX + TBW, TBY + TBH, "PACC-FRAME")
for i in (1, 2, 3):
    line(TBX, TBY + i * TBH / 4, TBX + TBW, TBY + i * TBH / 4, "PACC-FRAME")
line(TBX + TBW * 0.76, TBY, TBX + TBW * 0.76, TBY + TBH, "PACC-FRAME")
ROWS = [("CONG TRINH: NHA O RIENG LE 5 TANG", "SO HIEU: PACC-01"),
        ("DIA DIEM: P. BAI CHAY - TP HA LONG - QN", "TY LE: 1/100"),
        ("DON VI: DOI CC&CNCH KV4 - PCCC QN", "NGAY: 23/11/2026"),
        ("NHIEM VU: CHUA CHAY TANG 1 + CNCH", "VE: HERMES")]
for i, (l, r) in enumerate(ROWS):
    cy = TBY + (3 - i) * TBH / 4 + TBH / 8
    txt(l, TBX + 0.2, cy - 0.07, 0.25, "PACC-TEXT")
    txt(r, TBX + TBW * 0.76 + 0.2, cy - 0.07, 0.25, "PACC-TEXT")

# ===================== CÔNG TRÌNH (5 x 16 m) =====================
BX1, BY1, BX2, BY2 = 3.5, 8.0, 8.5, 24.0
rect(BX1, BY1, BX2, BY2, "PACC-CONG-TRINH")
rect(BX1 + 0.2, BY1 + 0.2, BX2 - 0.2, BY2 - 0.2, B)
line(BX1, BY1 + 9.0, BX2, BY1 + 9.0, B)                    # vách ngăn tầng
rect(BX1 + 0.2, BY1 + 5.9, BX1 + 2.3, BY1 + 8.8, B)        # cầu thang
for i in range(1, 8):
    y = BY1 + 5.9 + i * (2.9 / 8)
    line(BX1 + 0.2, y, BX1 + 1.25, y, B)
line(BX1 + 1.25, BY1 + 5.9, BX1 + 1.25, BY1 + 8.8, B)
txt("CAU THANG", BX1 + 0.3, BY1 + 5.4, TF, "PACC-TEXT")
txt("NHA O RIENG LE 5 TANG", BX1 + 0.7, BY1 + 6.2, 0.30, "PACC-TEXT", rot=90)
txt("WC", BX1 + 3.4, BY1 + 7.5, TF, "PACC-TEXT")
line(BX1 + 3.0, BY1 + 5.9, BX1 + 3.0, BY1 + 8.8, B)        # vách WC
# lối thoát nạn tầng 1
line(BX1 + 3.6, BY1 + 0.2, BX1 + 3.6, BY1 - 1.4, "PACC-THONG-THUY")
line(BX1 + 4.4, BY1 + 0.2, BX1 + 4.4, BY1 - 1.4, "PACC-THONG-THUY")
txt("LOI THOAT NAN", BX1 + 4.6, BY1 - 1.2, TF, "PACC-THONG-THUY")

# ===================== ĐƯỜNG + VỈA HÈ =====================
line(0.25, 6.6, 23.5, 6.6, "PACC-DUONG")
line(0.25, 3.1, 23.5, 3.1, "PACC-DUONG")
line(0.25, 6.3, 23.5, 6.3, "PACC-DUONG")
txt("DUONG NOI BO RONG 6.0 m", 12.0, 4.55, TF, "PACC-DUONG", "center")
txt("VIA HE", 2.0, 6.75, TF, "PACC-DUONG")

# ===================== PHƯƠNG TIỆN =====================
sym("xe_bon", 11.0, 4.9, None, 0)
txt("XE CC TEC (5 tan)", 11.0, 4.0, TF, "PACC-TEXT", "center")
sym("xe_chi_huy", 20.0, 4.9, None, 0)
txt("XE CHI HUY", 20.0, 4.0, TF, "PACC-TEXT", "center")

# ===================== NGUỒN NƯỚC =====================
sym("tru_nuoc", 9.6, 7.4, None, 0)
txt("TRU NUOC D100", 11.2, 8.05, TF, "PACC-TEXT", "center")

# ===================== ĐIỂM CHÁY GIẢ ĐỊNH =====================
FX, FY = 5.6, 12.0
sym("diem_xp_chay", FX, FY, None, 0)
msp.add_circle((FX, FY), 0.9, dxfattribs={"layer": "PACC-CHIEN-THUAT", "color": 1})
sym("dam_chay", FX, FY, None, 0)
txt("DIEM CHAY GIA DINH T1", FX + 3.4, FY + 2.6, TF, "PACC-CHIEN-THUAT")
line(FX + 3.3, FY + 2.45, FX + 0.75, FY + 0.55, "PACC-CHIEN-THUAT")   # leader

# ===================== LĂNG + VÒI + TIA NƯỚC =====================
sym("lang_b", 5.6, 7.6, None, 90)          # lăng B tấn công gốc lửa
txt("LANG B", 6.1, 7.1, TF, "PACC-CHIEN-THUAT")
sym("lang_a", 1.6, 16.0, None, 0)          # lăng A làm mát, chống cháy lan
txt("LANG A", 1.3, 15.2, TF, "PACC-CHIEN-THUAT")

# vòi chữa cháy S-line: xe -> lăng B
pts = [(14.2, 4.9), (12.4, 6.0), (10.0, 6.9), (7.6, 7.2), (6.0, 7.5), (5.6, 7.6)]
msp.add_spline(pts, dxfattribs={"layer": "PACC-DUONG-VOI", "color": 1})
txt("VOI D65 - 6 CUON", 8.0, 7.75, TF, "PACC-DUONG-VOI")
# vòi hút tiếp nước: xe -> trụ nước
pts2 = [(11.0, 4.9), (10.4, 5.9), (9.7, 6.6), (9.6, 7.2)]
msp.add_spline(pts2, dxfattribs={"layer": "PACC-DUONG-VOI", "color": 4})
txt("VOI HUT D100", 10.15, 6.15, TF, "PACC-DUONG-VOI")

# tia nước (nét đứt) từ miệng lăng vào tâm cháy
msp.add_line((5.6, 8.3), (5.6, FY - 0.95), dxfattribs={"layer": "PACC-TIA-NUOC", "linetype": "DASHED"})
msp.add_line((4.95, 8.3), (5.15, FY - 1.4), dxfattribs={"layer": "PACC-TIA-NUOC", "linetype": "DASHED"})
msp.add_line((6.25, 8.3), (6.05, FY - 1.4), dxfattribs={"layer": "PACC-TIA-NUOC", "linetype": "DASHED"})
msp.add_line((2.4, 16.0), (BX1, 16.0), dxfattribs={"layer": "PACC-TIA-NUOC", "linetype": "DASHED"})

# ===================== CHIẾN THUẬT =====================
sym("huong_tan_cong_chinh", 9.0, 6.95, None, 180)
txt("HUONG TAN CONG CHINH", 9.2, 9.2, TF, "PACC-CHIEN-THUAT")

# hướng gió
gx, gy = 19.5, 24.5
line(gx, gy, gx + 3.2, gy - 1.1, "PACC-CHIEN-THUAT")
line(gx + 3.2, gy - 1.1, gx + 2.5, gy - 0.95, "PACC-CHIEN-THUAT")
line(gx + 3.2, gy - 1.1, gx + 2.9, gy - 0.35, "PACC-CHIEN-THUAT")
txt("HUONG GIO", gx - 0.2, gy + 0.35, TF, "PACC-CHIEN-THUAT")

# ===================== BẢNG CHÚ GIẢI =====================
LX, LY = 14.2, 11.6
msp.add_lwpolyline([(LX, LY), (LX + 9.4, LY), (LX + 9.4, LY + 7.0), (LX, LY + 7.0)],
                   close=True, dxfattribs={"layer": "PACC-FRAME"})
txt("BANG CHU GIAI KY HIEU (C07)", LX + 0.25, LY + 6.5, 0.26, "PACC-LEGEND")
LEG = [("xe_bon", "Xe chua chay co gioi (tec nuoc)"),
       ("lang_b", "Lang B (D50) tan cong goc lua"),
       ("lang_a", "Lang A (D65) lam mat - chan chay lan"),
       ("tru_nuoc", "Tru nuoc chua chay D100"),
       ("diem_xp_chay", "Diem chay gia dinh"),
       ("huong_tan_cong_chinh", "Huong tan cong chinh")]
for i, (sid, label) in enumerate(LEG):
    yy = LY + 5.7 - i * 1.05
    sym(sid, LX + 0.85, yy + 0.15, 0.30 * SYM_SCALE.get(sid, 1.0), 0, "PACC-LEGEND")
    txt(label, LX + 2.1, yy, TF, "PACC-LEGEND")

# ===================== GHI CHÚ CHIẾN THUẬT =====================
NX, NY = 23.9, 27.9
txt("GHI CHU CHIEN THUAT", NX, NY, 0.30, "PACC-TEXT")
NOTES = ["1. Tinh huong: chay tai tang 1, khu vuc cau thang - kho.",
         "2. Xe CC do tai vi tri quy dinh, trien khai 2 lang:",
         "   Lang B tan cong truc dien goc lua, Lang A lam mat.",
         "3. Tiep nuoc tu tru D100 cach nha 6 m, 1 xe du tru.",
         "4. Cuu nguoi qua loi thoat nan phia truoc nha.",
         "5. Chi huy tai xe chi huy, phong toa 2 dau duong."]
for i, s in enumerate(NOTES):
    txt(s, NX, NY - 0.55 - i * 0.42, TF, "PACC-TEXT")

# mui Bac
nx, ny = 12.4, 1.6
line(nx, ny - 0.9, nx, ny + 1.7, "PACC-CHIEN-THUAT")
msp.add_solid([(nx - 0.28, ny + 0.75), (nx + 0.28, ny + 0.75), (nx, ny + 1.75)],
              dxfattribs={"layer": "PACC-CHIEN-THUAT", "color": 7})
txt("B", nx - 0.1, ny + 1.9, 0.24, "PACC-TEXT")
# thuoc ty le 0-5 m
sx, sy = 14.6, 1.0
for i in range(5):
    line(sx + i, sy, sx + i, sy + (0.35 if i % 2 == 0 else 0.2), "PACC-TEXT")
line(sx, sy, sx + 5, sy, "PACC-TEXT")
for i, lab in ((0, "0"), (2.5, "2,5"), (5, "5 m")):
    txt(lab, sx + i, sy - 0.35, 0.2, "PACC-TEXT", "center")
txt("TY LE 1:100", sx + 2.5, sy + 0.55, 0.2, "PACC-TEXT", "center")

txt("SO DO CHUA CHAY - NHA O RIENG LE 5 TANG", 12.0, 28.4, 0.45, "PACC-TEXT", "center")

os.makedirs(OUT_DIR, exist_ok=True)
doc.saveas(DXF)
print("DXF", DXF, os.path.getsize(DXF), "entities", len(msp))
