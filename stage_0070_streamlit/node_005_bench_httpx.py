"""
node_005 — bench httpx Async: tempo vs gap vs concurrency (CTTU Snapshot)

Mede wall-time / 429 / ok para achar SNAPSHOT_FETCH_GAP_S e workers
sem matar taxa (pós-429 ficou lento com gap=0.35).

Uso:
  python stage_0070_streamlit/node_005_bench_httpx.py
  python stage_0070_streamlit/node_005_bench_httpx.py --n 9 --gaps 0,0.05,0.1,0.2,0.35

Saída: EXPORT/v001/bench_httpx_*.json + summary.txt
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import httpx

_ROOT = Path(__file__).resolve().parents[1]
_GLOBALS = _ROOT / "stage_0010_globals"
if str(_GLOBALS) not in sys.path:
    sys.path.insert(0, str(_GLOBALS))

import node_003_globals as node_003

EXPORT_DIR = Path(node_003.BENCH_EXPORT)

# matriz default: gaps a varrer × workers (estilo multicam page)
DEFAULT_GAPS = (0.0, 0.05, 0.1, 0.15, 0.2, 0.35)
DEFAULT_WORKERS = (3, 6, 9)
DEFAULT_N = 9  # = STYLE_PANEL_PAGE_SIZE


@dataclass
class BenchRow:
    gap_s: float
    workers: int
    n_urls: int
    wall_s: float
    ok: int
    http_429: int
    other_err: int
    bytes_ok: int
    mean_ok_s: float


def resolve_urls(n: int) -> list[tuple[str, str]]:
    """(key, url) das primeiras N câmeras do DF_CAMERAS."""
    catalog = node_003.DF_CAMERAS
    if catalog.empty:
        raise RuntimeError(f"DF_CAMERAS vazio — {node_003.CAMERAS_JSON}")
    keys = [str(k) for k in catalog.index.tolist()[:n]]
    return [(k, str(catalog.loc[k, "url"])) for k in keys]


async def fetch_one(
    client: httpx.AsyncClient,
    url: str,
    *,
    retries: int,
    gap_s: float,
) -> tuple[str, int, int]:
    """
    Retorna (status_tag, nbytes, http_status).
    status_tag: ok | 429 | err
    """
    last_status = 0
    for attempt in range(retries + 1):
        try:
            resp = await client.get(url)
            last_status = int(resp.status_code)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                wait_s = float(retry_after) if retry_after else gap_s * (attempt + 2)
                await asyncio.sleep(max(wait_s, gap_s or 0.05))
                continue
            resp.raise_for_status()
            data = resp.content
            if data[:2] != b"\xff\xd8":
                return "err", 0, last_status
            return "ok", len(data), last_status
        except Exception:  # noqa: BLE001 — bench agrega erros
            return "err", 0, last_status
    return "429", 0, 429


async def run_matrix_row(
    pairs: list[tuple[str, str]],
    *,
    gap_s: float,
    workers: int,
    timeout_s: float,
    user_agent: str,
    retries: int,
) -> BenchRow:
    """Uma célula da matriz: N urls com pacer + semaphore."""
    sem = asyncio.Semaphore(max(1, workers))
    pacer = asyncio.Lock()
    next_at = 0.0
    ok = http_429 = other_err = bytes_ok = 0
    t_ok: list[float] = []

    async def _pace() -> None:
        nonlocal next_at
        async with pacer:
            now = asyncio.get_running_loop().time()
            wait = next_at - now
            if wait > 0:
                await asyncio.sleep(wait)
            next_at = asyncio.get_running_loop().time() + gap_s

    async def _one(client: httpx.AsyncClient, url: str) -> None:
        nonlocal ok, http_429, other_err, bytes_ok
        async with sem:
            await _pace()
            t0 = time.perf_counter()
            tag, nbytes, _status = await fetch_one(
                client, url, retries=retries, gap_s=gap_s
            )
            dt = time.perf_counter() - t0
            if tag == "ok":
                ok += 1
                bytes_ok += nbytes
                t_ok.append(dt)
            elif tag == "429":
                http_429 += 1
            else:
                other_err += 1

    headers = {"User-Agent": user_agent}
    timeout = httpx.Timeout(timeout_s)
    wall0 = time.perf_counter()
    async with httpx.AsyncClient(
        timeout=timeout,
        headers=headers,
        follow_redirects=True,
    ) as client:
        await asyncio.gather(*[_one(client, url) for _k, url in pairs])
    wall = time.perf_counter() - wall0
    mean_ok = (sum(t_ok) / len(t_ok)) if t_ok else 0.0
    return BenchRow(
        gap_s=gap_s,
        workers=workers,
        n_urls=len(pairs),
        wall_s=round(wall, 3),
        ok=ok,
        http_429=http_429,
        other_err=other_err,
        bytes_ok=bytes_ok,
        mean_ok_s=round(mean_ok, 3),
    )


def pick_best(rows: list[BenchRow]) -> BenchRow | None:
    """Melhor = zero 429, max ok, menor wall_s."""
    clean = [r for r in rows if r.http_429 == 0 and r.ok == r.n_urls]
    if not clean:
        clean = [r for r in rows if r.http_429 == 0 and r.ok > 0]
    if not clean:
        return min(rows, key=lambda r: (r.http_429, -r.ok, r.wall_s)) if rows else None
    return min(clean, key=lambda r: (r.wall_s, r.gap_s))


def write_export(rows: list[BenchRow], best: BenchRow | None) -> Path:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    payload = {
        "stamp": stamp,
        "globals_gap": float(node_003.SNAPSHOT_FETCH_GAP_S),
        "globals_workers": int(node_003.STYLE_MULTICAM_WORKERS),
        "globals_retries": int(node_003.SNAPSHOT_429_RETRIES),
        "rows": [asdict(r) for r in rows],
        "best": asdict(best) if best else None,
    }
    json_path = EXPORT_DIR / f"bench_httpx_{stamp}.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        f"bench httpx async — {stamp}",
        f"globals: GAP={node_003.SNAPSHOT_FETCH_GAP_S} WORKERS={node_003.STYLE_MULTICAM_WORKERS}",
        "",
        f"{'gap':>6} {'w':>3} {'wall':>7} {'ok':>3} {'429':>4} {'err':>3} {'mean_ok':>8}",
        "-" * 48,
    ]
    for r in rows:
        lines.append(
            f"{r.gap_s:6.2f} {r.workers:3d} {r.wall_s:7.2f} {r.ok:3d} "
            f"{r.http_429:4d} {r.other_err:3d} {r.mean_ok_s:8.2f}"
        )
    lines.append("")
    if best:
        lines.append(
            f"BEST → gap={best.gap_s} workers={best.workers} "
            f"wall={best.wall_s}s ok={best.ok}/{best.n_urls} 429={best.http_429}"
        )
        lines.append(
            f"sugerido: SNAPSHOT_FETCH_GAP_S = {best.gap_s}  "
            f"# STYLE_MULTICAM_WORKERS = {best.workers}"
        )
    summary = EXPORT_DIR / f"bench_httpx_{stamp}_summary.txt"
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest = EXPORT_DIR / "bench_httpx_latest_summary.txt"
    latest.write_text(summary.read_text(encoding="utf-8"), encoding="utf-8")
    return summary


def parse_floats(raw: str) -> tuple[float, ...]:
    return tuple(float(x.strip()) for x in raw.split(",") if x.strip())


def parse_ints(raw: str) -> tuple[int, ...]:
    return tuple(int(x.strip()) for x in raw.split(",") if x.strip())


async def amain(args: argparse.Namespace) -> int:
    pairs = resolve_urls(args.n)
    gaps = parse_floats(args.gaps) if args.gaps else DEFAULT_GAPS
    workers_list = parse_ints(args.workers) if args.workers else DEFAULT_WORKERS
    retries = int(node_003.SNAPSHOT_429_RETRIES)
    timeout_s = float(node_003.SNAPSHOT_TIMEOUT_S)
    ua = str(node_003.SNAPSHOT_USER_AGENT)

    print(f"bench httpx | n={len(pairs)} gaps={gaps} workers={workers_list}")
    print(f"globals gap={node_003.SNAPSHOT_FETCH_GAP_S} workers={node_003.STYLE_MULTICAM_WORKERS}")
    rows: list[BenchRow] = []
    for gap in gaps:
        for workers in workers_list:
            print(f"  … gap={gap} workers={workers}", flush=True)
            row = await run_matrix_row(
                pairs,
                gap_s=gap,
                workers=workers,
                timeout_s=timeout_s,
                user_agent=ua,
                retries=retries,
            )
            rows.append(row)
            print(
                f"    wall={row.wall_s}s ok={row.ok} 429={row.http_429} err={row.other_err}",
                flush=True,
            )
            # respiro entre células pra não contaminar a próxima
            await asyncio.sleep(1.0)

    best = pick_best(rows)
    path = write_export(rows, best)
    print(f"\nexport: {path}")
    if best:
        print(
            f"BEST gap={best.gap_s} workers={best.workers} "
            f"wall={best.wall_s}s 429={best.http_429}"
        )
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Bench CTTU Snapshot httpx async")
    p.add_argument("--n", type=int, default=DEFAULT_N, help="n câmeras (default 9)")
    p.add_argument(
        "--gaps",
        type=str,
        default="",
        help="lista gaps segundos, ex: 0,0.05,0.1,0.35",
    )
    p.add_argument(
        "--workers",
        type=str,
        default="",
        help="lista concurrency, ex: 3,6,9",
    )
    args = p.parse_args()
    return asyncio.run(amain(args))


if __name__ == "__main__":
    raise SystemExit(main())
