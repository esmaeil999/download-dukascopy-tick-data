#!/usr/bin/env python3
"""Convert dukascopy-node CSV (timestamp,askPrice,bidPrice[,askVolume,bidVolume])
to JForex-style CSV: GmtTime,Bid,Ask,BidVolume,AskVolume (GMT)."""

import csv
import glob
import sys
from datetime import datetime, timezone

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "ticks_converted.csv"
    files = sorted(glob.glob("download/*.csv"))
    if not files:
        print("No input CSV files found in ./download", file=sys.stderr)
        sys.exit(1)

    total = 0
    with open(out_path, "w", newline="") as fo:
        fo.write("GmtTime,Bid,Ask,BidVolume,AskVolume\n")
        for path in files:
            with open(path, newline="") as fi:
                reader = csv.reader(fi)
                header = next(reader, None) or []
                idx = {name: i for i, name in enumerate(header)}
                has_vol = "bidVolume" in idx and "askVolume" in idx
                if not has_vol:
                    print(f"WARNING: {path} has no volume columns; writing 0", file=sys.stderr)
                for row in reader:
                    if not row:
                        continue
                    ts = int(float(row[idx["timestamp"]]))
                    dt = datetime.fromtimestamp(ts // 1000, tz=timezone.utc)
                    gmt = f"{dt:%Y-%m-%d %H:%M:%S}.{ts % 1000:03d}"
                    bid = row[idx["bidPrice"]]
                    ask = row[idx["askPrice"]]
                    bid_vol = row[idx["bidVolume"]] if has_vol else "0"
                    ask_vol = row[idx["askVolume"]] if has_vol else "0"
                    fo.write(f"{gmt},{bid},{ask},{bid_vol},{ask_vol}\n")
                    total += 1
            print(f"converted {path} (total rows: {total})", flush=True)

    print(f"DONE. rows = {total} -> {out_path}")

if __name__ == "__main__":
    main()
