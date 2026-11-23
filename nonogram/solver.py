#!/usr/bin/env python3
"""數織 (Nonogram) 解題程式。

用法:
    python3 solver.py puzzles/level42.txt            # 印出答案
    python3 solver.py puzzles/level42.txt -o ans.png # 另存答案圖片

題目檔格式（# 開頭為註解，數字用空白分隔）：
    rows:
    5 1 2 2
    2 3 2 1
    ...
    cols:
    4 3 4
    9 4
    ...
空白列（沒有塗色）請寫 0。
"""
import argparse
import sys
from functools import lru_cache

UNKNOWN, EMPTY, FILLED = -1, 0, 1


def parse(path):
    rows, cols, cur = [], [], None
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#")[0].strip()
            if not line:
                continue
            low = line.lower().rstrip(":")
            if low in ("rows", "row", "橫列", "列"):
                cur = rows
                continue
            if low in ("cols", "col", "columns", "直行", "行"):
                cur = cols
                continue
            if cur is None:
                sys.exit("題目檔要先寫 rows: 或 cols:")
            clue = [int(x) for x in line.replace(",", " ").split()]
            cur.append([c for c in clue if c > 0])
    return rows, cols


def line_solve(clue, cells):
    """回傳這一條線所有合法排法的交集；無解回傳 None。"""
    n, k = len(cells), len(clue)
    # suffix[i] = 從第 i 段開始，最少需要幾格
    min_len = [0] * (k + 1)
    for i in range(k - 1, -1, -1):
        min_len[i] = clue[i] + (min_len[i + 1] + 1 if i + 1 < k else 0)

    can_fill = [False] * n
    can_empty = [False] * n

    @lru_cache(maxsize=None)
    def ok(pos, idx):
        """從 pos 開始放第 idx 段之後的所有段，是否可行。"""
        if idx == k:
            return all(cells[p] != FILLED for p in range(pos, n))
        length = clue[idx]
        last_start = n - min_len[idx]
        result = False
        for start in range(pos, last_start + 1):
            if any(cells[p] == FILLED for p in range(pos, start)):
                break
            end = start + length
            if any(cells[p] == EMPTY for p in range(start, end)):
                continue
            if end < n and cells[end] == FILLED:
                continue
            nxt = end + 1 if end < n else end
            if ok(nxt, idx + 1):
                result = True
                for p in range(pos, start):
                    can_empty[p] = True
                for p in range(start, end):
                    can_fill[p] = True
                if end < n:
                    can_empty[end] = True
                if idx + 1 == k:
                    for p in range(nxt, n):
                        can_empty[p] = True
        return result

    if not ok(0, 0):
        return None
    out = []
    for f, e in zip(can_fill, can_empty):
        out.append(FILLED if f and not e else EMPTY if e and not f else UNKNOWN)
    return out


def propagate(grid, rows, cols):
    h, w = len(rows), len(cols)
    dirty_r, dirty_c = set(range(h)), set(range(w))
    while dirty_r or dirty_c:
        for r in sorted(dirty_r):
            new = line_solve(tuple(rows[r]), tuple(grid[r]))
            if new is None:
                return False
            for c in range(w):
                if grid[r][c] != new[c]:
                    grid[r][c] = new[c]
                    dirty_c.add(c)
        dirty_r = set()
        for c in sorted(dirty_c):
            col = tuple(grid[r][c] for r in range(h))
            new = line_solve(tuple(cols[c]), col)
            if new is None:
                return False
            for r in range(h):
                if grid[r][c] != new[r]:
                    grid[r][c] = new[r]
                    dirty_r.add(r)
        dirty_c = set()
    return True


def solve(rows, cols, limit=2):
    """回傳最多 limit 個解（用來檢查是否唯一解）。"""
    solutions = []

    def rec(grid):
        if len(solutions) >= limit:
            return
        if not propagate(grid, rows, cols):
            return
        for r, row in enumerate(grid):
            for c, v in enumerate(row):
                if v == UNKNOWN:
                    for guess in (FILLED, EMPTY):
                        g = [list(x) for x in grid]
                        g[r][c] = guess
                        rec(g)
                    return
        solutions.append(grid)

    rec([[UNKNOWN] * len(cols) for _ in rows])
    return solutions


def check_input(rows, cols):
    errs = []
    w, h = len(cols), len(rows)
    for i, cl in enumerate(rows, 1):
        need = sum(cl) + max(len(cl) - 1, 0)
        if need > w:
            errs.append(f"第 {i} 列 {cl} 需要 {need} 格，超過寬度 {w}")
    for i, cl in enumerate(cols, 1):
        need = sum(cl) + max(len(cl) - 1, 0)
        if need > h:
            errs.append(f"第 {i} 行 {cl} 需要 {need} 格，超過高度 {h}")
    sr, sc = sum(map(sum, rows)), sum(map(sum, cols))
    if sr != sc:
        errs.append(f"橫列總格數 {sr} ≠ 直行總格數 {sc}，提示可能抄錯")
    return errs


def to_text(grid, rows):
    w = len(grid[0])
    lines = ["     " + "".join(f"{c % 10}" if c % 5 == 0 else "·" for c in range(1, w + 1))]
    for i, (row, cl) in enumerate(zip(grid, rows), 1):
        cells = "".join("█" if v == FILLED else "·" for v in row)
        lines.append(f"{i:>3}  {cells}   {' '.join(map(str, cl))}")
    return "\n".join(lines)


def to_png(grid, rows, cols, path, cell=36):
    from PIL import Image, ImageDraw, ImageFont

    h, w = len(rows), len(cols)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(cell * 0.45))
    except OSError:
        font = ImageFont.load_default()
    left = cell * (max(len(r) for r in rows) * 0.7 + 1)
    top = cell * (max(len(c) for c in cols) * 0.55 + 0.5)
    left, top = int(left), int(top)
    img = Image.new("RGB", (left + w * cell + 10, top + h * cell + 10), "#fdf3e6")
    d = ImageDraw.Draw(img)
    for r, cl in enumerate(rows):
        d.text((left - 8, top + r * cell + cell / 2), " ".join(map(str, cl)),
               fill="#5a3a1a", font=font, anchor="rm")
    for c, cl in enumerate(cols):
        for j, num in enumerate(reversed(cl)):
            d.text((left + c * cell + cell / 2, top - 6 - j * cell * 0.55), str(num),
                   fill="#5a3a1a", font=font, anchor="mb")
    for r in range(h):
        for c in range(w):
            x, y = left + c * cell, top + r * cell
            if grid[r][c] == FILLED:
                d.rectangle([x + 2, y + 2, x + cell - 2, y + cell - 2], fill="#f4c20d", outline="#b8860b")
            else:
                d.line([x + cell * .35, y + cell * .35, x + cell * .65, y + cell * .65], fill="#bbb", width=2)
                d.line([x + cell * .65, y + cell * .35, x + cell * .35, y + cell * .65], fill="#bbb", width=2)
    for i in range(w + 1):
        d.line([left + i * cell, top, left + i * cell, top + h * cell],
               fill="#5a3a1a" if i % 5 == 0 else "#d8c4a8", width=2 if i % 5 == 0 else 1)
    for i in range(h + 1):
        d.line([left, top + i * cell, left + w * cell, top + i * cell],
               fill="#5a3a1a" if i % 5 == 0 else "#d8c4a8", width=2 if i % 5 == 0 else 1)
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description="數織解題程式")
    ap.add_argument("puzzle", help="題目檔路徑")
    ap.add_argument("-o", "--output", help="輸出答案圖片 (.png)")
    args = ap.parse_args()

    rows, cols = parse(args.puzzle)
    print(f"大小：{len(rows)} 列 × {len(cols)} 行")
    errs = check_input(rows, cols)
    if errs:
        print("⚠ 提示數字有問題：\n  " + "\n  ".join(errs))
        sys.exit(1)

    sols = solve(rows, cols)
    if not sols:
        print("❌ 無解，請檢查提示數字是否抄錯")
        sys.exit(1)
    if len(sols) > 1:
        print("⚠ 有多組解，以下是其中一組")
    print(to_text(sols[0], rows))
    if args.output:
        to_png(sols[0], rows, cols, args.output)
        print(f"答案圖片：{args.output}")


if __name__ == "__main__":
    main()
