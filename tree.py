from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "__pycache__"
}

MAX_DEPTH = 6
PNG_SUMMARY_THRESHOLD = 5


def format_size(size_bytes):
    """Convertit les bytes en taille lisible."""
    units = ["B", "KB", "MB", "GB", "TB"]

    size = float(size_bytes)

    for unit in units:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024

    return f"{size:.1f} PB"


def get_dir_size(path):
    """Calcule récursivement la taille d'un dossier."""
    total = 0

    try:
        for p in path.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
    except:
        pass

    return total


def afficher_arborescence(path, prefix="", depth=0):
    if depth > MAX_DEPTH:
        return

    path = Path(path)

    try:
        items = [
            i for i in path.iterdir()
            if i.name not in EXCLUDE_DIRS
        ]
    except PermissionError:
        return

    items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        branch = "└── " if is_last else "├── "

        # =========================
        # DOSSIERS
        # =========================
        if item.is_dir():

            try:
                sub_items = list(item.iterdir())
            except:
                sub_items = []

            png_files = [
                f for f in sub_items
                if f.is_file() and f.suffix.lower() == ".png"
            ]

            dir_size = format_size(get_dir_size(item))

            # Résumé automatique des dossiers remplis de png
            if len(png_files) >= PNG_SUMMARY_THRESHOLD:
                print(
                    prefix + branch +
                    f"{item.name}/ "
                    f"({len(png_files)} fichiers .png, ~{dir_size})"
                )
                continue

            print(
                prefix + branch +
                f"{item.name}/ "
                f"(~{dir_size})"
            )

            new_prefix = prefix + ("    " if is_last else "│   ")
            afficher_arborescence(item, new_prefix, depth + 1)

        # =========================
        # FICHIERS
        # =========================
        else:

            # Ne pas afficher les png individuellement
            if item.suffix.lower() == ".png":
                continue

            try:
                file_size = format_size(item.stat().st_size)
            except:
                file_size = "?"

            print(
                prefix + branch +
                f"{item.name} "
                f"(~{file_size})"
            )


print(".")
afficher_arborescence(".")