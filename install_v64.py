
from pathlib import Path
import shutil

project = Path(r"A:\quantum-cyber-defense-arena")
app_file = project / "frontend" / "src" / "App.tsx"
panel_file = project / "frontend" / "src" / "components" / "QuantumResearchPanel.tsx"

if not panel_file.is_file():
    raise SystemExit("HIBA: QuantumResearchPanel.tsx nem található.")

content = app_file.read_text(encoding="utf-8")

import_line = 'import QuantumResearchPanel from "./components/QuantumResearchPanel";'
panel_line = "<QuantumResearchPanel />"
anchor = "<AIThreatReport />"

if anchor not in content:
    raise SystemExit("HIBA: AIThreatReport beszúrási pont nem található.")

if content.count(anchor) != 1:
    raise SystemExit("HIBA: Nem egyértelmű a beszúrási pont.")

backup = app_file.with_suffix(".tsx.before_v64_python.bak")
shutil.copy2(app_file, backup)

if import_line not in content:
    content = import_line + "\n" + content

if panel_line not in content:
    content = content.replace(
        anchor,
        anchor + "\n        " + panel_line,
        1,
    )

app_file.write_text(content, encoding="utf-8")

print("V6.4 QUANTUM RESEARCH PANEL BEKÖTVE")
print("Biztonsági mentés:", backup)
print("Az App.tsx többi része változatlan.")
