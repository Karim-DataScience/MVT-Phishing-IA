import zipfile
import hashlib
import statistics
from pathlib import Path
import re
import html as ihtml

# =========================
# CONFIG
# =========================

INPUT_DIR = Path("/input")
OUTPUT_FILE = Path("/output/dataset.tsv")

DATASETS = [
    ("Benign_HTML.zip", "benign"),
    ("Malicious_HTML.zip", "malicious"),
]

SEP = "\t"

# =========================
# GLOBAL STORAGE
# =========================

seen_hashes = set()

# =========================
# FAST DECODING
# =========================

def decode_bytes(raw: bytes) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except:
            pass
    return raw.decode("utf-8", errors="ignore")

# =========================
# FAST HTML CLEANING
# =========================

def extract_text(html: str) -> str:
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)

    html = ihtml.unescape(html)
    return " ".join(html.split())

# =========================
# NOISE CLEANING
# =========================

BAD = [
    "skip to main", "cookie", "accept", "login",
    "sign in", "register", "menu", "navigation",
    "footer", "copyright", "terms", "privacy",
]

def clean_text(text: str) -> str:
    t = text.lower()
    for b in BAD:
        t = t.replace(b, " ")
    return " ".join(t.split())

# =========================
# HASH + NORMALIZE
# =========================

def normalize(text: str) -> str:
    return " ".join(text.lower().split())

def get_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# =========================
# ZIP PROCESSING
# =========================

def process_zip(zip_path: Path, label: str):

    rows = []
    total = 0
    kept = 0

    lengths = []

    print(f"\n[+] Processing {zip_path.name}")

    with zipfile.ZipFile(zip_path, "r") as z:

        files = z.namelist()
        total = len(files)

        for file_name in files:

            if not file_name.lower().endswith((".html", ".htm")):
                continue

            try:
                with z.open(file_name) as f:
                    raw = f.read()

                html = decode_bytes(raw)
                text = extract_text(html)

                if len(text) < 20:
                    continue

                text = clean_text(text)
                text = normalize(text)

                h = get_hash(text)

                if h in seen_hashes:
                    continue

                seen_hashes.add(h)

                rows.append((text, label))
                lengths.append(len(text))

                kept += 1

            except:
                continue

    print(f"[ZIP STATS] total={total} kept={kept}")

    return rows, lengths

# =========================
# STATS FUNCTION
# =========================

def print_stats(benign_lengths, malicious_lengths):

    print("\n====================")
    print("TEXT LENGTH STATS")
    print("====================")

    if benign_lengths:
        print("\n[Benign]")
        print("avg:", sum(benign_lengths) / len(benign_lengths))
        print("min:", min(benign_lengths))
        print("max:", max(benign_lengths))
        print("median:", statistics.median(benign_lengths))

    if malicious_lengths:
        print("\n[Malicious]")
        print("avg:", sum(malicious_lengths) / len(malicious_lengths))
        print("min:", min(malicious_lengths))
        print("max:", max(malicious_lengths))
        print("median:", statistics.median(malicious_lengths))

# =========================
# MAIN
# =========================

def main():

    all_rows = []

    benign_lengths = []
    malicious_lengths = []

    for zip_name, label in DATASETS:

        zip_path = INPUT_DIR / zip_name

        if not zip_path.exists():
            print(f"[!] missing {zip_path}")
            continue

        rows, lengths = process_zip(zip_path, label)

        all_rows.extend(rows)

        if label == "benign":
            benign_lengths.extend(lengths)
        else:
            malicious_lengths.extend(lengths)

    print(f"\n[GLOBAL] samples = {len(all_rows)}")

    if not all_rows:
        print("No data extracted")
        return

    # =========================
    # SHUFFLE
    # =========================

    import random
    random.shuffle(all_rows)

    # =========================
    # SAVE TSV
    # =========================

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("text" + SEP + "label\n")

        for text, label in all_rows:
            text = text.replace("\n", " ").replace(SEP, " ")
            f.write(text + SEP + label + "\n")

    print("\n====================")
    print("DONE")
    print("Saved:", OUTPUT_FILE)
    print("Samples:", len(all_rows))
    print("====================")

    # =========================
    # STATS
    # =========================

    print_stats(benign_lengths, malicious_lengths)


if __name__ == "__main__":
    main()