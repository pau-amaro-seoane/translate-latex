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


class FromStep():
    def __init__(self, filename=None):

        if re.search(".txt$", filename) is None:
            sys.exit("The input should be .txt file. Exit.")

        self.filename = filename

        self.source = None
        self.comments = None
        self.commands = None
        self.latex = None

        self.trttex = None
        self.corrupted = None

        ### Regular expressions patterns
        self.p1 = re.compile("\[ *[012][\.\,][0-9]+\]")
        self.p2 = re.compile("(?<=[\[ ])[012](?=[\.\,])")
        self.p3 = re.compile("(?<=[\.\,])[0-9]+(?=\])")
        self.p4 = re.compile("___GTEXFIXCOMMENT[0-9]*___")

    def fix_spacing_and_chars(self):
        ### Replace weird characters introduced by translation
        self.trtext = re.sub("\u200B", " ", self.source)

        ### Fix spacing
        spacing = [
            (r"\\ ", r"\\"),
            (" ~ ", "~"),
            (" {", "{"),
        ]
        for pattern in spacing:
           self.trtext = re.sub(pattern[0], pattern[1], self.trtext)

    def restore_latex_and_formulas(self):
        ### Restore LaTeX and formulas
        here = 0
        newtext = ""
        nl = 0
        nc = 0
        self.corrupted = []
        for m in self.p1.finditer(self.trtext):
            group = m.group()
            t = int(self.p2.search(group).group())
            n = int(self.p3.search(group).group())
            if t == 1:
                if n < nl:
                    print(f"Token '{group}' found in place of [{t}.{nl}]. Edit manually and run again.")
                    break
                while nl != n:
                    self.corrupted.append(f"[{t}.{nl}]")
                    nl += 1
                newtext += self.trtext[here : m.start()] + self.latex[n]
                nl += 1
            elif t == 2:
                if n < nc:
                    print(f"Token '{group}' found in place of [{t}.{nc}]. Edit manually and run again.")
                    break
                while nc != n:
                    self.corrupted.append(f"[{t}.{nc}]")
                    nc += 1
                newtext += self.trtext[here : m.start()] + self.commands[n]
                nc += 1
            here = m.end()
        newtext += self.trtext[here:]
        self.trtext = newtext

    def restore_comments(self):
        ### Restore comments
        here = 0
        ncomment = 0
        newtext = []
        for m in self.p4.finditer(self.trtext):
            group = m.group()
            n = int(re.search("[0-9]+", group).group())
            if n != ncomment:
                print(f"Comment token {group} is broken. Stopping.")
                break
            newtext.append(self.trtext[here : m.start()] + self.comments[n])
            ncomment += 1
            here = m.end()
        newtext.append(self.trtext[here:])
        self.trtext = "".join(newtext)

    def process(self):

        self.read_files()
        self.fix_spacing_and_chars()
        self.restore_latex_and_formulas()
        self.restore_comments()


        ### Save the processed output to .tex file
        output_filename = self.filename.replace(".txt", ".tex")
        with open(output_filename, "w") as translation_file:
            translation_file.write(self.trtext)
        #print("Output file:", output_filename)

        ### Report the corrupted tokens
        if self.corrupted:
            print("Corrupted tokens detected:", end=" ")
            for c in self.corrupted:
                print(c, end=" ")
            print("\nTo improve the output manually change the corrupted tokens in file"
                  f"{self.filename} and run from.py again.")


    def read_files(self):
        ### Load LaTeX data from binary files
        with open(self.filename, "r") as fin:
            self.source = fin.read()
        with open("gtexfix_comments", "rb") as fp:
            self.comments = pickle.load(fp)
        with open("gtexfix_commands", "rb") as fp:
            self.commands = pickle.load(fp)
        with open("gtexfix_latex", "rb") as fp:
            self.latex = pickle.load(fp)


