import os
import sys
from deep_translator import GoogleTranslator
from subprocess import check_call

from step_to import ToStep
from step_from import FromStep


# input filename
filename = sys.argv[1]

translator = GoogleTranslator(source="en", target="es")

data = None
with open(filename) as f:
    data = f.read()

new_sections = []

sections = data.split("\n\n")
total_sections = len(sections)
for idx, section in enumerate(sections):
    print(f"Translating {idx}/{total_sections - 1}")

    tmp_file = "tmp.tex"

    with open(tmp_file, "w") as f:
        f.write(section)

    t = ToStep(filename=tmp_file)
    t.process()

    fname = tmp_file.replace(".tex", "_0.txt")
    with open(fname) as f:
        text = f.read()
        out = translator.translate(text)

    t_fname = f"translated_{fname}"
    with open(t_fname, "w") as f:
        f.write(out)

    f = FromStep(filename=t_fname)
    f.process()

    translated = None
    with open(t_fname.replace(".txt", ".tex")) as f:
        translated = f.read()
    new_sections.append(translated)

with open(f"es_{filename}", "w") as f:
    f.write("\n\n".join(new_sections))

# Cleaning files
_files = [
    "gtexfix_commands",
    "gtexfix_comments",
    "gtexfix_latex",
    "tmp.tex",
    "tmp_0.txt",
    "translated_tmp_0.tex",
    "translated_tmp_0.txt",
]
for _f in _files:
    os.remove(_f)
