import re
from typing import Iterable

from datatypes.datatypes import (
    StaticToken,
    DynamicToken,
    Variable,
    IntLiteral,
    BoolLiteral,
    StringLiteral,
    IndexingAction, )

static_tokens: Iterable[tuple[str, StaticToken]] = list(
    map(
        lambda token: (re.escape(token), token),
        [
            StaticToken.INT,
            StaticToken.BOOL,
            StaticToken.STRING,
            StaticToken.INT_ARR,
            StaticToken.BOOL_ARR,
            StaticToken.STRING_ARR,
            StaticToken.IF,
            StaticToken.THEN_BEGIN,
            StaticToken.THEN_END,
            StaticToken.ELSE_BEGIN,
            StaticToken.ELSE_END,
            StaticToken.ASSIGN,
            StaticToken.ASSIGN_ARR,
            StaticToken.BREAK,
            StaticToken.CONTINUE,
            StaticToken.LPAREN,
            StaticToken.RPAREN,
            StaticToken.FOR_BEGIN,
            StaticToken.FOR_END,
            StaticToken.SEMICOLON,
            StaticToken.PLUS,
            StaticToken.MINUS,
            StaticToken.DIVIDE,
            StaticToken.MULTIPLY,
            StaticToken.LSHIFT,
            StaticToken.RSHIFT,
            StaticToken.BITWISE_OR,
            StaticToken.BITWISE_AND,
            StaticToken.XOR,
            StaticToken.EQUALS,
            StaticToken.LTE,
            StaticToken.GTE,
            StaticToken.LT,
            StaticToken.GT,
            StaticToken.NE,
            StaticToken.CMP_AND,
            StaticToken.CMP_OR,
            StaticToken.CMP_NOT,
        ],
    )
)

dynamic_tokens: Iterable[tuple[str, type[DynamicToken]]] = [
    ("[a-zA-Z_][a-zA-Z0-9_]*", Variable),
    ("[+-]?[0-9]+", IntLiteral),
    ("true|false", BoolLiteral),
    ('"([^"]*)"', StringLiteral),
    (r"([a-zA-Z_][a-zA-Z0-9_]*)\[([+-]?[0-9]+)\]", IndexingAction),
]


def consume_any_spaces(code: str) -> str:
    return code[0 if (pos := re.match(r"\s*", code)) is None else pos.end() :]


def maximal_munch(running_tokens: list[StaticToken | DynamicToken], code: str) -> str:
    max_len: int = 0
    longest_token: StaticToken | DynamicToken = StaticToken.EMPTY

    for pattern, dt_type in dynamic_tokens:
        regex_match = re.match(pattern, code)
        if regex_match:
            match_length = len(regex_match.group())
            if match_length >= max_len:
                max_len, longest_token = match_length, dt_type.from_rem(regex_match)

    for pattern, token in static_tokens:
        if re.match(pattern, code):
            if len(token) >= max_len:
                max_len, longest_token = len(token), token
    if (max_len, longest_token) == (0, StaticToken.EMPTY):
        raise Exception(f"Lexing failed at {code}.")

    running_tokens.append(longest_token)
    return code[max_len:]


def lex(code: str) -> list[StaticToken | DynamicToken]:
    # Replace all non-space whitespace with space
    code = " ".join(code.split())
    running_tokens: list[StaticToken | DynamicToken] = []
    while code:
        code = maximal_munch(running_tokens, consume_any_spaces(code))
    return running_tokens


if __name__ == "__main__":
    print(lex('i[] aa[5] (true) "hi" (4 + -5) (6 + 7);'))
