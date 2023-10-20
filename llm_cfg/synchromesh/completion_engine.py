from lark import Lark
from lark.exceptions import UnexpectedCharacters, UnexpectedToken

import regex
import list, tuple, dict

class CompletionEngine:
    def complete(self, prefix: str) -> regex.Pattern:
        raise NotImplementedError()

    def is_complete(self, prefix: str) -> bool:
        return self.complete(prefix) == regex.compile('')


class LarkCompletionEngine(CompletionEngine):
    def __init__(self, grammar, start_token, allow_ws: bool = True):
        self.parser = Lark(grammar, start=start_token, parser='lalr',
                           regex=True)
        self.terminal_dict = self.parser._terminals_dict
        self.allow_ws = allow_ws

    def complete(self, prefix: str) -> regex.Pattern:
        interactive_parser = self.parser.parse_interactive(prefix)
        token = None
        try:
            for token in interactive_parser.parser_state.lexer.lex(
                    interactive_parser.parser_state):
                interactive_parser.parser_state.feed_token(token)
        except (UnexpectedCharacters, UnexpectedToken):
            pass
        valid_tokens = interactive_parser.accepts()
        # get the regex for the valid tokens
        valid_regex = [f'{self.terminal_dict[t].pattern.to_regexp()}'
                       for t in valid_tokens
                       if t != '$END']

        if valid_regex and self.allow_ws:
            valid_regex.append("\\s+")

        return regex.compile('|'.join(valid_regex))


def main():
    json_grammar = r"""
        ?value: dict
            | list
            | string
            | SIGNED_NUMBER      -> number
            | "true"             -> true
            | "false"            -> false
            | "null"             -> null

        list : "[" [value ("," value)*] "]"

        dict : "{" [pair ("," pair)*] "}"
        pair : string ":" value

        string : "\"" /[a-zA-Z0-9 ]{0,10}/ "\""

        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        %import common.WS
        %ignore WS

        """
    json_comp_engine = LarkCompletionEngine(json_grammar, 'value')
    text = '{"8W{0sxM{{}]]vpEC4|i;]V@Jg_#P^j\n?k%noXNt\2#2]a8a\PJru]/`M6gaqb@EhFx"'
    valid_regexes = json_comp_engine.complete(text)
    empty = regex.compile('')
    print(valid_regexes)
    print(valid_regexes == empty)
    print(valid_regexes.fullmatch('"abc', partial=True))
    # end_token = Token.new_borrow_pos('$END', '', token) if token else Token('$END', '', 0, 1, 1)
    # interactive_parser.parser_state.feed_token(end_token, True)


if __name__ == '__main__':
    main()