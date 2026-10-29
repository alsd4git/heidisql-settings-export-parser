"""Regenerate the README's synthetic CLI output preview."""

from html import escape
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "examples" / "synthetic-export.txt"
OUTPUT = ROOT / "docs" / "assets" / "quickstart-output.svg"


def main() -> None:
    with TemporaryDirectory(prefix="heidi-decode-demo-") as temp_dir:
        export_path = Path(temp_dir) / "synthetic-export.txt"
        export_path.write_bytes(EXPORT.read_bytes())
        result = subprocess.run(
            [sys.executable, str(ROOT / "heidi_decode.py"), str(export_path)],
            cwd=temp_dir,
            capture_output=True,
            check=True,
            text=True,
        )

    lines = result.stdout.rstrip().splitlines()
    svg_lines = "\n".join(
        f'  <text x="32" y="{94 + index * 28}">{escape(line)}</text>'
        for index, line in enumerate(lines)
    )
    height = 110 + len(lines) * 28
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="{height}" viewBox="0 0 920 {height}" role="img" aria-labelledby="title description">
  <title id="title">heidi-decode output for synthetic demo data</title>
  <desc id="description">CLI output from a fake HeidiSQL connection. No real credentials are used.</desc>
  <rect width="920" height="{height}" rx="12" fill="#111827" />
  <circle cx="28" cy="28" r="6" fill="#f87171" />
  <circle cx="50" cy="28" r="6" fill="#fbbf24" />
  <circle cx="72" cy="28" r="6" fill="#34d399" />
  <text x="96" y="33" class="caption">heidi-decode · synthetic output</text>
  <g class="output">
{svg_lines}
  </g>
  <style>
    .caption {{ fill: #9ca3af; font: 14px system-ui, sans-serif; }}
    .output {{ fill: #e5e7eb; font: 16px ui-monospace, SFMono-Regular, Consolas, monospace; }}
  </style>
</svg>
'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
