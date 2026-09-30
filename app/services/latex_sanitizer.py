import re


def sanitize_latex(code: str) -> str:
    """
    Post-injection safety pass on generated Manim code.
    Fixes unescaped backslashes inside Python string literals
    so that LaTeX commands like \\int, \\frac don't become
    invalid escape sequences at parse time.

    This is a regex-based approach that targets triple-quoted
    and regular string literals and doubles any lone backslash
    that isn't already doubled.
    """
    # Match triple-quoted strings (both kinds) and regular strings
    # and fix single backslashes inside them.
    # We use a replacer that processes each string match.
    STRING_RE = re.compile(
        r'(r""".*?"""|r\'\'\'.*?\'\'\'|""".*?"""|\'\'\'.*?\'\'\'|r".*?"|r\'.*?\'|".*?"|\'.*?\')',
        re.DOTALL
    )

    def _fix_escapes(m: re.Match) -> str:
        s = m.group(0)
        # Skip raw strings entirely — they're already correct
        if s.startswith("r"):
            return s
        # Within non-raw strings, replace single backslash with double
        # A single backslash: not preceded by another backslash
        # and not followed by another backslash
        inner = s[1:-1] if len(s) >= 2 and s[0] == s[-1] == '"' else s
        # Actually work on the interior of the string
        quote = s[0]
        if s[:3] in ('"""', "'''"):
            quote = s[:3]
            interior = s[3:-3]
        else:
            quote = s[0]
            interior = s[1:-1]

        # Replace a lone backslash (not doubled) with a double backslash
        # Lone backslash: a \ not preceded by another \, and not followed by another \
        fixed = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', interior)
        return quote + fixed + quote

    return STRING_RE.sub(_fix_escapes, code)
