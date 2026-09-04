#!/usr/bin/env python3
"""
Convert dukascopy-node CSV to the requested format:

Date,Time,Bid,Ask,Last,Volume,Flags
2014.01.01,22:00:00.896,0.81909,0.82012,0.81909,0.1,0.1
"""

import csv
import glob
import sys
from datetime import datetime, timezone


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "ticks_converted.csv"

    # اول فایل‌های داخل download را می‌خوانیم
    files = sorted(glob.glob("download/*.csv"))
    if not files:
        # اگر از قبل کپی شده بود، خود فایل ورودی را هم امتحان می‌کنیم
        if out_path and out_path.endswith(".csv"):
            files = [out_path]
        else:
            print("No input CSV files found", file=sys.stderr)
            sys.exit(1)

    total = 0
    with open(out_path, "w", newline="", encoding="utf-8") as fo:
        fo.write("Date,Time,Bid,Ask,Last,Volume,Flags\n")

        for path in files:
            with open(path, newline="", encoding="utf-8") as fi:
                reader = csv.reader(fi)
                header = next(reader, None) or []
                idx = {name: i for i, name in enumerate(header)}

                # پشتیبانی از هر دو حالت نام ستون‌ها
                ts_col = idx.get("timestamp")
                bid_col = idx.get("bidPrice") or idx.get("Bid")
                ask_col = idx.get("askPrice") or idx.get("Ask")
                bid_vol_col = idx.get("bidVolume") or idx.get("BidVolume")
                ask_vol_col = idx.get("askVolume") or idx.get("AskVolume")

                if ts_col is None or bid_col is None or ask_col is None:
                    print(f"ERROR: required columns missing in {path}", file=sys.stderr)
                    print(f"Header found: {header}", file=sys.stderr)
                    sys.exit(1)

                for row in reader:
                    if not row or len(row) <= max(ts_col, bid_col, ask_col):
                        continue

                    try:
                        ts = int(float(row[ts_col]))
                    except (ValueError, TypeError):
                        continue

                    dt = datetime.fromtimestamp(ts // 1000, tz=timezone.utc)
                    ms = ts % 1000

                    date_str = f"{dt:%Y.%m.%d}"
                    time_str = f"{dt:%H:%M:%S}.{ms:03d}"

                    bid = row[bid_col]
                    ask = row[ask_col]
                    last = bid  # معمولاً Last = Bid

                    volume = row[bid_vol_col] if bid_vol_col is not None else "0"
                    flags = row[ask_vol_col] if ask_vol_col is not None else "0"

                    fo.write(f"{date_str},{time_str},{bid},{ask},{last},{volume},{flags}\n")
                    total += 1

            print(f"converted {path}  (rows so far: {total})", flush=True)

    print(f"DONE. total rows = {total}  →  {out_path}")


if __name__ == "__main__":
    main()
