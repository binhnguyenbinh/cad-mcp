"""Smoke test end-to-end: cad-mcp server.py <-> AutoCAD qua MCP stdio.
Chạy: python -I -B tests\\test_mcp_smoke.py   (AutoCAD phải đang mở)
Không có AutoCAD -> SKIP (exit 0), không fail."""
import asyncio, base64, os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "server.py")
OUT = os.path.join(ROOT, "tests", "out")
os.makedirs(OUT, exist_ok=True)

# AutoCAD đang chạy?
import time
ok = False
last = None
for _ in range(30):
    try:
        import pythoncom, win32com.client
        pythoncom.CoInitialize()
        app = win32com.client.GetActiveObject("AutoCAD.Application")
        _ = app.Name
        ok = True
        break
    except Exception as e:
        last = e
        time.sleep(1)
if not ok:
    print("SKIP: AutoCAD khong san sang (", type(last).__name__, ")", "- bo qua test MCP.")
    sys.exit(0)
print("AutoCAD:", app.Name, "ready")

from mcp import ClientSession, StdioServerParameters, stdio_client

fail = 0
cases = 0


def check(label, ok):
    global fail, cases
    cases += 1
    if not ok:
        fail += 1
        print("FAIL", label)
    else:
        print("PASS", label)


async def main():
    global fail
    params = StdioServerParameters(command=sys.executable, args=[SERVER], env={**os.environ})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tl = await s.list_tools()
            names = {t.name for t in tl.tools}
            check("tool count >= 35", len(names) >= 35)
            check("has core tools", {"line", "circle", "rectangle", "text", "save", "screenshot", "info"} <= names)

            async def call(tool, **kw):
                res = await s.call_tool(tool, kw)
                if res.is_error:
                    print("  ERR", tool, res.content)
                return res

            r = await call("info")
            check("info ok", not r.is_error)
            r = await call("layer", name="SMOKE", color=3, make_current=True)
            check("layer ok", not r.is_error)
            r = await call("rectangle", x1=0, y1=0, x2=100, y2=60)
            check("rectangle ok", not r.is_error)
            r = await call("text", x=10, y=70, value="MCP SMOKE", height=8)
            check("text ok", not r.is_error)
            r = await call("zoom_extents")
            check("zoom ok", not r.is_error)
            dwg = os.path.join(OUT, "mcp_smoke_test.dwg")
            r = await call("save", path=dwg, overwrite=True)
            check("save ok", not r.is_error and os.path.exists(dwg))
            r = await call("screenshot")
            img_saved = False
            for c in r.content:
                data = getattr(c, "data", None)
                if data:
                    open(os.path.join(OUT, "mcp_smoke_test.png"), "wb").write(base64.b64decode(data))
                    img_saved = True
            check("screenshot ok", not r.is_error and img_saved)
    print(f"\n{cases - fail}/{cases} passed")


asyncio.run(main())
sys.exit(1 if fail else 0)
