#!/usr/bin/env python
# -----------------------------------------
# Google translate fix for LaTeX documents
# Copyright (c) Dmitry R. Gulevich 2020
# GNU General Public License v3.0
# -----------------------------------------
import re
import sys
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

if re.search(".txt$", args.filename) is None:
    sys.exit("The input should be .txt file. Exit.")

print("Input file:", args.filename)

### Regular expressions patterns
p1 = re.compile("\[ *[012][\.\,][0-9]+\]")
p2 = re.compile("(?<=[\[ ])[012](?=[\.\,])")
p3 = re.compile("(?<=[\.\,])[0-9]+(?=\])")
p4 = re.compile("___GTEXFIXCOMMENT[0-9]*___")


### Load LaTeX data from binary files
with open(args.filename, "r") as fin:
    source = fin.read()
with open("gtexfix_comments", "rb") as fp:
    comments = pickle.load(fp)
with open("gtexfix_commands", "rb") as fp:
    commands = pickle.load(fp)
with open("gtexfix_latex", "rb") as fp:
    latex = pickle.load(fp)

### Replace weird characters introduced by translation
trtext = re.sub("\u200B", " ", source)

### Fix spacing
trtext = re.sub(r"\\ ", r"\\", trtext)
trtext = re.sub(" ~ ", "~", trtext)
trtext = re.sub(" {", "{", trtext)

### Restore LaTeX and formulas
here = 0
newtext = ""
nl = 0
nc = 0
corrupted = []
for m in p1.finditer(trtext):
    group = m.group()
    t = int(p2.search(group).group())
    n = int(p3.search(group).group())
    if t == 1:
        if n < nl:
            print(f"Token '{group}' found in place of [{t}.{nl}]. Edit manually and run again.")
            break
        while nl != n:
            corrupted.append(f"[{t}.{nl}]")
            nl += 1
        newtext += trtext[here : m.start()] + latex[n]
        nl += 1
    elif t == 2:
        if n < nc:
            print(f"Token '{group}' found in place of [{t}.{nc}]. Edit manually and run again.")
            break
        while nc != n:
            corrupted.append(f"[{t}.{nc}]")
            nc += 1
        newtext += trtext[here : m.start()] + commands[n]
        nc += 1
    here = m.end()
newtext += trtext[here:]
trtext = newtext

### Restore comments
here = 0
ncomment = 0
newtext = []
for m in p4.finditer(trtext):
    group = m.group()
    n = int(re.search("[0-9]+", group).group())
    if n != ncomment:
        print(f"Comment token {group} is broken. Stopping.")
        break
    newtext.append(trtext[here : m.start()] + comments[n])
    ncomment += 1
    here = m.end()
newtext.append(trtext[here:])
trtext = "".join(newtext)

### Save the processed output to .tex file
output_filename = re.sub(".txt$", ".tex", args.filename)
with open(output_filename, "w") as translation_file:
    translation_file.write(trtext)
print("Output file:", output_filename)

### Report the corrupted tokens
if corrupted == []:
    print("No corrupted tokens. The translation is ready.")
else:
    print("Corrupted tokens detected:", end=" ")
    for c in corrupted:
        print(c, end=" ")
    print("\nTo improve the output manually change the corrupted tokens in file"
          f"{args.filename} and run from.py again.")
