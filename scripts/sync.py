import csv
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


# ============================================================
# NGUỒN DỮ LIỆU TTHC ĐIỆN BIÊN
# ============================================================

SOURCE_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vQk2DNzNnpsDR4wTrzBjoy7aKtDKDeubqvnyBdlJstAzxobagxsvSo8kJX2TI9dXHlBMbUjO2htStuw/"
    "pub?gid=226385689&single=true&output=csv"
)

OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "tthc.json"
META_FILE = OUTPUT_DIR / "meta.json"


# ============================================================
# HÀM TẢI CSV
# ============================================================

def download_csv(url):
    print("==============================================")
    print(" DONG BO TTHC DIEN BIEN")
    print("==============================================")
    print("Nguon:")
    print(url)
    print()

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/131.0 Safari/537.36"
            )
        },
    )

    with urlopen(request, timeout=60) as response:
        raw = response.read()

    print(f"Da tai: {len(raw):,} bytes")

    # Google Sheets thường trả UTF-8
    text = raw.decode("utf-8-sig", errors="replace")

    return text


# ============================================================
# CHUẨN HÓA TÊN CỘT
# ============================================================

def normalize_key(value):
    if value is None:
        return ""

    return (
        str(value)
        .replace("\ufeff", "")
        .replace("\n", " ")
        .replace("\r", " ")
        .strip()
    )


# ============================================================
# CHUYỂN CSV → JSON
# ============================================================

def parse_csv(text):

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise RuntimeError("CSV khong co header.")

    headers = [normalize_key(h) for h in reader.fieldnames]

    print()
    print("Cac cot tim thay:")
    for h in headers:
        print(" -", h)

    rows = []

    for index, raw_row in enumerate(reader, start=1):

        row = {}

        for key, value in raw_row.items():

            clean_key = normalize_key(key)

            if value is None:
                value = ""

            value = str(value).strip()

            row[clean_key] = value

        # Bỏ dòng hoàn toàn rỗng
        if not any(str(v).strip() for v in row.values()):
            continue

        # Đảm bảo STT nếu nguồn không có
        if not row.get("STT"):
            row["STT"] = str(index)

        rows.append(row)

    return headers, rows


# ============================================================
# KIỂM TRA DỮ LIỆU
# ============================================================

def validate(headers, rows):

    if len(rows) == 0:
        raise RuntimeError(
            "NGUON TRA VE 0 DONG. "
            "Khong ghi de du lieu hien tai."
        )

    # Các cột quan trọng
    important_columns = [
        "MaTTHC",
        "Tên TTHC",
    ]

    found = 0

    for column in important_columns:
        if column in headers:
            found += 1

    if found == 0:
        print()
        print("CANH BAO:")
        print("Khong tim thay cot MaTTHC/Tên TTHC theo ten chuan.")
        print("Van tiep tuc vi du lieu co the dung ten cot khac.")

    print()
    print(f"Tong so dong TTHC: {len(rows):,}")

    # In thử 3 dòng
    print()
    print("Mau du lieu:")

    for row in rows[:3]:
        print(
            row.get("STT", ""),
            "|",
            row.get("MaTTHC", ""),
            "|",
            row.get("Tên TTHC", ""),
            "|",
            row.get("LinhVuc", ""),
            "|",
            row.get("MucDo", ""),
        )


# ============================================================
# GHI JSON
# ============================================================

def save_json(rows):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Ghi file tạm trước
    temp_file = OUTPUT_FILE.with_suffix(".tmp")

    with temp_file.open("w", encoding="utf-8") as f:

        json.dump(
            rows,
            f,
            ensure_ascii=False,
            indent=2,
        )

    temp_file.replace(OUTPUT_FILE)

    print()
    print(f"Da ghi: {OUTPUT_FILE}")
    print(f"So luong: {len(rows):,}")


# ============================================================
# GHI META
# ============================================================

def save_meta(rows, headers):

    now = datetime.now(timezone.utc).isoformat()

    meta = {
        "source": SOURCE_URL,
        "province": "Điện Biên",
        "updated_at": now,
        "count": len(rows),
        "headers": headers,
        "sync_status": "success",
    }

    with META_FILE.open("w", encoding="utf-8") as f:

        json.dump(
            meta,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Da ghi: {META_FILE}")


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        text = download_csv(SOURCE_URL)

        headers, rows = parse_csv(text)

        validate(headers, rows)

        save_json(rows)

        save_meta(rows, headers)

        print()
        print("==============================================")
        print(f"SYNC OK: {len(rows):,} TTHC")
        print("==============================================")

    except Exception as exc:

        print()
        print("==============================================")
        print("SYNC FAILED")
        print("==============================================")
        print(str(exc))
        print()

        # Quan trọng:
        # Không tạo file rỗng nếu nguồn bị lỗi.
        # Giữ nguyên data cũ trong repository.

        sys.exit(2)


if __name__ == "__main__":
    main()
