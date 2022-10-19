import os
import sys
from deep_translator import GoogleTranslator
from subprocess import check_call


# input filename
filename = sys.argv[1]

translator = GoogleTranslator(source='en', target='es')

data = None
with open(filename) as f:
    data = f.read()

new_sections = []

sections = data.split("\n\n")
for section in sections:

    tmp_file = "tmp.tex"

    with open(tmp_file, "w") as f:
        f.write(section)

    # Call to.py
    check_call(f"python to.py {tmp_file}".split())

    fname = tmp_file.replace(".tex", "_0.txt")
    with open(fname) as f:
        text = f.read()
        out = translator.translate(text)

    with open(f"translated_{fname}", "w") as f:
        f.write(out)

    # Call from.py
    check_call(f"python from.py translated_{fname}".split())

    translated = None
    with open(f"translated_{fname}".replace(".txt", ".tex")) as f:
        translated = f.read()
    new_sections.append(translated)

with open(f"es_{filename}", "w") as f:
    f.write("\n\n".join(new_sections))

# Cleaning files
_files = ["gtexfix_commands", "gtexfix_comments", "gtexfix_latex",
      "tmp.tex", "tmp_0.txt", "translated_tmp_0.tex",
      "translated_tmp_0.txt"]
for _f in _files:
    os.remove(_f)

