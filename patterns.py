import re


def get_pattern_scope(v):
    words = [
        "equation",
        "figure",
        "eqnarray",
        "multiline",
        "thebibliography",
        "verbatim",
        "table",
        "subequations",
        "align",
        "displaymath",
        "gather",
        "tikzpicture",
    ]
    patterns = [fr"\\{v}{{ *{w}\** *}}" for w in words]
    if v == "begin":
        patterns.append(fr"\\\[")
    elif v == "end":
        patterns.append(fr"\\\]")

    return "|".join(patterns)

def get_pattern_commands():
    commands = [
        r"___GTEXFIXCOMMENT[0-9]*___",
        r"\\title",
        r"\\chapter\**",
        r"\\section\**",
        r"\\subsection\**",
        r"\\subsubsection\**",
        r"\\textbf\**",
        r"\\textit\**",
        r"\\plain\**",
        r"\\emph\**",
        r"\\underline\**",
        r"~*\\footnote[0-9]*",
        r"(\$+)(?:(?!\1)[\s\S])*\1",
        r"~*\\\w*\s*{[^}]*}\s*{[^}]*}",
        r"~*\\\w*\s*{[^}]*}|~*\\\w*",
    ]
    return "|".join(commands)
