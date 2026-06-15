#!/usr/bin/env python3
"""
dxf_tube.py  —  Cable-mark tube schedule from AutoCAD Electrical DXF.

Algorithm (v2 — instance-count):
    Each cable mark block (FAMILY=CBL) represents ONE wire segment.
    A wire segment always needs 2 tubes — one at each end (head + tail).
    Therefore:

        tube = 2 × (number of CBL block instances with that tag)

    This is correct for every case when the drawing follows the convention:
        • 1 CBL block per wire segment
        • branched rungs  → 2 blocks with the same tag  → 4 tubes
        • 3-way branch    → 3 blocks same tag            → 6 tubes
        • bus rail (220V) → 9 blocks same tag            → 18 tubes

    No geometry tracing is needed.  The result is exact by construction.

Connection hint (informational, not used in tube count):
    The nearest device above and below the FIRST block instance in the column
    is shown in the "การเชื่อมต่อ" column so the engineer can cross-check.

Output:  Two-sheet Excel
    Sheet 1  CableMark  — No / Name cablemark / จำนวน tube / การเชื่อมต่อ
    Sheet 2  DeviceList — No / Symbol / Name / Brand / Model
"""
import math
from collections import Counter, defaultdict

import ezdxf

WIRE_LAYER_PREFIX = "YEL"
CBL_FAMILY        = "CBL"
COL_TOL           = 20.0   # drawing units — same-column tolerance


# ── helpers ────────────────────────────────────────────────────────────────

def _attrs(insert):
    return {a.dxf.tag: a.dxf.text for a in insert.attribs}


def load_dxf(path):
    """Return (cable_marks, devices).

    cable_marks : list of (tag:str, pos:(x,y))
    devices     : list of (family:str, tag:str, pos:(x,y), attrs:dict)
    """
    try:
        doc = ezdxf.readfile(path)
    except ezdxf.DXFStructureError:
        doc, _ = ezdxf.recover.readfile(path)

    msp = doc.modelspace()
    cable_marks, devices = [], []

    for e in msp.query("INSERT"):
        a   = _attrs(e)
        fam = a.get("FAMILY")
        tag = a.get("TAG1") or a.get("TAG2") or ""
        p   = (round(e.dxf.insert.x, 2), round(e.dxf.insert.y, 2))

        if fam == CBL_FAMILY:
            cable_marks.append((tag, p))
        elif fam:
            devices.append((fam, tag, p, a))

    return cable_marks, devices


def _neighbors(pos, devices):
    """Nearest device directly above and below pos in the same column."""
    cx, cy = pos
    col    = [(tag, p) for _, tag, p, _ in devices if abs(p[0] - cx) <= COL_TOL]
    above  = [(p[1], tag) for tag, p in col if p[1] > cy]
    below  = [(p[1], tag) for tag, p in col if p[1] < cy]
    a = min(above)[1] if above else None   # smallest y-above = closest
    b = max(below)[1] if below else None   # largest y-below  = closest
    return a, b


def _clean(tag):
    return (tag or "").lstrip("-")


# ── core algorithm ──────────────────────────────────────────────────────────

def count_tubes(cable_marks, devices):
    """Return list of row-dicts for the CableMark sheet.

    Each row: {name, tube, connection}
    tube is always an integer — never None — because 1 instance = 2 tubes.
    """
    # 1) count instances per tag  →  tube = 2 × count
    counts = Counter(_clean(tag) for tag, _ in cable_marks)

    # 2) connection hint: use the FIRST occurrence of each tag
    first_pos = {}
    for tag, pos in cable_marks:
        name = _clean(tag)
        if name not in first_pos:
            first_pos[name] = pos

    rows = []
    for name, cnt in counts.items():
        pos  = first_pos[name]
        a, b = _neighbors(pos, devices)
        conn = f"{_clean(a)}-{_clean(b)}" if a and b else \
               f"bus/rail ({_clean(a) or _clean(b)})"
        # flag multi-instance rows so the engineer sees why tube > 2
        if cnt > 1:
            conn += f"  (+{cnt-1} segment)"
        rows.append({"name": name, "tube": 2 * cnt, "connection": conn})

    # sort: A1…A11 numerically, then others alphabetically
    def _sort_key(r):
        n = r["name"]
        digits = "".join(ch for ch in n if ch.isdigit())
        alpha  = "".join(ch for ch in n if ch.isalpha())
        return (alpha, int(digits)) if digits else (n, 0)

    rows.sort(key=_sort_key)
    return rows


def build_device_list(devices):
    """De-duplicate by symbol; pull catalog attrs if present."""
    seen = {}
    for _, tag, _, a in devices:
        sym = _clean(tag)
        if not sym or sym in seen:
            continue
        seen[sym] = {
            "symbol": sym,
            "name" : a.get("DESC1", "") or a.get("CATDESC", ""),
            "brand": a.get("MFG",   ""),
            "model": a.get("CAT",   ""),
        }
    out = sorted(seen.values(), key=lambda d: (
        "".join(ch for ch in d["symbol"] if ch.isalpha()),
        int("".join(ch for ch in d["symbol"] if ch.isdigit()) or 0),
    ))
    return out


# ── Excel writer ────────────────────────────────────────────────────────────

def write_excel(rows, dev_list, dest):
    """Write two-sheet workbook to dest (path or BytesIO)."""
    import pandas as pd
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    cable_df = pd.DataFrame(
        [(i+1, r["name"], r["tube"], r["connection"]) for i, r in enumerate(rows)],
        columns=["No", "Name cablemark", "จำนวน tube", "การเชื่อมต่อ"],
    )
    dev_df = pd.DataFrame(
        [(i+1, d["symbol"], d["name"], d["brand"], d["model"])
         for i, d in enumerate(dev_list)],
        columns=["No", "Symbol", "Name", "Brand", "Model"],
    )

    with pd.ExcelWriter(dest, engine="openpyxl") as xl:
        cable_df.to_excel(xl, sheet_name="CableMark",  index=False)
        dev_df.to_excel(xl,   sheet_name="DeviceList", index=False)
        _style_sheet(xl.sheets["CableMark"],  [8, 18, 14, 36])
        _style_sheet(xl.sheets["DeviceList"], [8, 14, 24, 18, 18])


def _style_sheet(ws, widths):
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    HDR  = PatternFill("solid", fgColor="1F4E78")
    BAND = PatternFill("solid", fgColor="EDF2FA")
    side = Side(style="thin", color="AAAAAA")
    box  = Border(side, side, side, side)

    for cell in ws[1]:
        cell.font      = Font(bold=True, color="FFFFFF")
        cell.fill      = HDR
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border    = box

    for r_idx, row in enumerate(ws.iter_rows(min_row=2), start=2):
        fill = BAND if r_idx % 2 == 0 else None
        for c_idx, cell in enumerate(row):
            cell.border    = box
            cell.alignment = Alignment(
                horizontal="left" if c_idx >= 3 else "center",
                vertical="center",
            )
            if fill:
                cell.fill = fill

    for i, w in enumerate(widths):
        ws.column_dimensions[chr(ord("A") + i)].width = w


# ── web-app helper ──────────────────────────────────────────────────────────

def build_workbook_bytes(dxf_path):
    """DXF path → (xlsx bytes, stats dict).  Used by server.py."""
    import io
    marks, devices = load_dxf(dxf_path)
    rows    = count_tubes(marks, devices)
    devlist = build_device_list(devices)

    buf = io.BytesIO()
    write_excel(rows, devlist, buf)
    buf.seek(0)

    stats = {
        "marks"  : len(rows),
        "devices": len(devlist),
        "total_tubes": sum(r["tube"] for r in rows),
    }
    return buf.getvalue(), stats


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser(description="DXF → tube schedule Excel")
    ap.add_argument("dxf",         help="input .dxf file")
    ap.add_argument("-o", "--out", required=True, help="output .xlsx path")
    args = ap.parse_args()

    marks, devices = load_dxf(args.dxf)
    rows    = count_tubes(marks, devices)
    devlist = build_device_list(devices)
    write_excel(rows, devlist, args.out)

    print(f"Cable marks : {len(rows)}")
    print(f"Total tubes : {sum(r['tube'] for r in rows)}")
    print(f"Devices     : {len(devlist)}")
    print(f"Saved       : {args.out}")


if __name__ == "__main__":
    main()
