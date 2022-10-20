#!/usr/bin/env python
# -----------------------------------------
# Google translate fix for LaTeX documents
# Copyright (c) Dmitry R. Gulevich 2020
# GNU General Public License v3.0
# -----------------------------------------
import pickle
import re
import sys

from patterns import get_pattern_commands, get_pattern_scope


class ToStep:
    def __init__(self, filename):

        # Regular expressions
        self.re_begin = re.compile(get_pattern_scope("begin"))
        self.re_end = re.compile(get_pattern_scope("end"))
        self.re_conflicts = re.compile(r"\[ *[012][\.\,][0-9]+\]")
        self.re_comment = re.compile(r"(?<!\\)[%].*")
        self.re_command = re.compile(get_pattern_commands())

        self.to_ncomment = 0
        self.to_nc = 0
        self.latex = []

        if not filename.endswith(".tex"):
            sys.exit("The input should be .tex file. Exit.")

        source = None
        with open(filename, "r") as source_file:
            source = source_file.read()

        self.filename = filename
        self.source = source

    def hide_latex_constructs(self):
        start_values = []
        end_values = []

        for m in self.re_begin.finditer(self.text):
            start_values.append(m.start())

        for m in self.re_end.finditer(self.text):
            end_values.append(m.end())

        nitems = len(start_values)
        assert (
            len(end_values) == nitems
        ), f"Missmatch: {self.text}\n, start:\n\t{start_values}\nend:\n\t{end_values}"

        if nitems > 0:
            newtext = self.text[: start_values[0]]

            for neq in range(nitems - 1):
                self.latex.append(self.text[start_values[neq] : end_values[neq]])
                _text = self.text[end_values[neq] : start_values[neq + 1]]
                newtext += f"[1.{len(self.latex) -1 }{_text}]"

            self.latex.append(self.text[start_values[nitems - 1] : end_values[nitems - 1]])
            _text = self.text[end_values[nitems - 1] :]
            newtext += f"[1.{len(self.latex) - 1}{_text}]"

            self.text = newtext

    def hide_latex_comments(self):
        comments = []
        for m in self.re_comment.finditer(self.text):
            comments.append(m.group())

        self.text = self.re_comment.sub(self.repl_comment, self.text)
        with open("gtexfix_comments", "wb") as fp:
            pickle.dump(comments, fp)

    def hide_latex_commands(self):
        commands = []
        for m in self.re_command.finditer(self.text):
            commands.append(m.group())

        self.text = self.re_command.sub(self.repl_f, self.text)
        with open("gtexfix_commands", "wb") as fp:
            pickle.dump(commands, fp)

    def repl_comment(self, obj):
        self.to_ncomment += 1
        return f"___GTEXFIXCOMMENT{self.to_ncomment - 1}___"

    def repl_f(self, obj):
        self.to_nc += 1
        return f"[2.{self.to_nc - 1}]"

    def process(self):

        # Search for possible token conflicts
        conflicts = self.re_conflicts.findall(self.source)
        if conflicts:
            print("Token conflicts detected: ", conflicts)
            sys.exit(
                "Tokens may overlap with the content. Change tokens or remove the source of conflict."
            )

        # Hide everything that is beyond \begin{document} ... \end{document}
        bdoc = re.search(r"\\begin{document}", self.source)
        edoc = re.search(r"\\end{document}", self.source)
        if bdoc is not None:
            preamble = self.source[: bdoc.end()]
            self.latex.append(preamble)
            if edoc is not None:
                self.text = "[1.0]" + self.source[bdoc.end() : edoc.start()]
                postamble = self.source[edoc.start() :]
            else:
                self.text = "[1.0]" + self.source[bdoc.end() :]
                postamble = []
        else:
            self.text = self.source
            postamble = []

        # Hide all comments
        self.hide_latex_comments()

        # Hide LaTeX constructs \begin{...} ... \end{...}
        self.hide_latex_constructs()

        if postamble:
            self.latex.append(postamble)
            elements = len(self.latex) - 1
            self.text += f"[1.{elements}]"
        with open("gtexfix_latex", "wb") as fp:
            pickle.dump(self.latex, fp)

        # Replace LaTeX commands, formulas and comments by tokens
        # Regular expression r'(\$+)(?:(?!\1)[\s\S])*\1' for treatment of $...$ and $$...$$ from:
        # https://stackoverflow.com/questions/54663900/how-to-use-regular-expression-to-remove-all-math-expression-in-latex-file
        self.hide_latex_commands()

        # Save the processed output to .txt file
        limit = 30000  # Estimated Google Translate character limit
        filebase = re.sub(".tex$", "", self.filename)
        start = 0
        npart = 0
        for m in re.finditer(r"\.\n", self.text):
            if m.end() - start < limit:
                end = m.end()
            else:
                output_filename = f"{filebase}_{npart}.txt"
                npart += 1
                with open(output_filename, "w") as txt_file:
                    txt_file.write(self.text[start:end])
                start = end
                end = m.end()

        output_filename = f"{filebase}_{npart}.txt"
        with open(output_filename, "w") as txt_file:
            txt_file.write(self.text[start:])
