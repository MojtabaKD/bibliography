import re
import regex
from pathlib import Path

BIB_DIR = Path("bib")

def memoir_number_from_doi(doi):
    m = re.search(r'memo/0*([0-9]+)$', doi)
    return int(m.group(1)) if m else None

def parse_amsrefs_entries(text):
    pattern = r"""
    \\bib\s*{[^}]+}
    \s*{book}
    \s*{
        (?P<content>
            (?: [^{}] | { (?&content) } )*
        )
    }
    """

    raw_entries = regex.findall(pattern, text, flags=regex.DOTALL | regex.VERBOSE)

    entries = []

    for raw in raw_entries:
        # print(f'raw={raw}')
        doi_match = re.search(r'doi\s*=\s*{([^}]+)}', raw)
        vol_match = re.search(r'volume\s*=\s*{([^}]+)}', raw)
        # print(f'doi_match={doi_match}, vol_match={vol_match}')

        title_match = re.findall(r'\btitle\s*=\s*{([^}]+)}', raw)
        title = title_match[-1] if title_match else None

        doi = doi_match.group(1) if doi_match else None
        vol = vol_match.group(1) if vol_match else None
        num = memoir_number_from_doi(doi) if doi else None

        if num:
            entries.append({
                "volume": int(vol),
                "title": title,
            })

    return entries

def main():
    all_entries = []
    final_memoirs = {}

    for file in sorted(BIB_DIR.glob("*.bib")):
        text = file.read_text(encoding="utf-8")
        entries = parse_amsrefs_entries(text)

        for e in entries:
            # print(e)
            e["file"] = file.name
            all_entries.append(e)

    all_entries.sort(key=lambda x: x["volume"])

    print(f"{'Vol':>5}  {'Title':100}  File")
    print("-" * 90)

    for e in all_entries:
        print(f"{str(e['volume']):>5}  {e['title'][:100]:100}  {e['file']}")

if __name__ == "__main__":
    main()
