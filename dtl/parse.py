from dtl.tokenize import Lexer, Token
import dtl.ast as ast

from functools import partial
from typing import Callable

class Parser:
    def __init__(self, debug: bool = False) -> None:
        self.lexer = Lexer(debug=debug)

    def parse(self, src: str) -> ast.File:
        self.lexer.tokenize(src)

        header_time_tokens = {}
        if self.lexer.peak().type == 'FOR':
            self.lexer.pop()

            while self.lexer.peak().type != 'COLON':
                time: Token | None = self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])
                header_time_tokens[time.type] = time.value

            self.lexer.assert_token('COLON')
            self.lexer.assert_token('NL')

        header_time = ast.Time(header_time_tokens)

        segments: list[ast.Segment] = []
        while self.lexer.peak().type == 'AT':
            segments.append(self.parse_time(header_time))

        tree: ast.File = ast.File(header_time, segments)
        tree.validate(header_time)

        return tree

    def parse_block[T](self, fn: Callable[[], T]) -> list[T]:
        self.lexer.assert_token('OPEN')

        ln: list[T] = []
        while self.lexer.peak().type != 'END':
            ln.append(fn())

        self.lexer.assert_token('END')

        return ln

    def parse_attributes(self, parent_time: ast.Time) -> list[ast.Segment | ast.Cmd | None]:
        return self.parse_block(partial(self.parse_attribute, parent_time))

    def parse_attribute(self, parent_time: ast.Time) -> ast.Segment | ast.Cmd | None:
        match self.lexer.peak().type:
            case 'AT':
                return self.parse_time(parent_time)
            case 'CMD':
                return self.parse_cmd()
            case err:
                print(f'Error: expected CMD, AT, found {err}')
                return None

    def parse_time(self, parent_time: ast.Time) -> ast.Segment:
        self.lexer.assert_token('AT')
        time_tokens: list[Token | None] = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
        while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
            time_tokens.append(self.lexer.pop())

        time: ast.Time = ast.Time({t.type: t.value for t in time_tokens}, parent=parent_time)

        if self.lexer.peak().type == 'PERIOD':
            self.lexer.assert_token('PERIOD')
            period_end_tokens: list[Token | None] = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
            while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
                period_end_tokens.append(self.lexer.pop())

            period_end: ast.Time = ast.Time({t.type: t.value for t in period_end_tokens}, parent=parent_time)

            time.period = True
            time.end = period_end

        if self.lexer.peak().type == 'ONGOING':
            self.lexer.assert_token('ONGOING')
            ongoing = True
        else:
            ongoing = False

        if self.lexer.peak().type == 'DESC':
            desc = self.lexer.assert_token('DESC').value
        else:
            desc = None

        self.lexer.assert_token('NL')

        attributes: list[ast.Segment | ast.Cmd | None] = []
        if self.lexer.peak().type == 'OPEN':
            attributes = self.parse_attributes(time)

        segments: list[ast.Segment] = [seg for seg in attributes if isinstance(seg, ast.Segment)]
        commands: list[ast.Cmd]     = [cmd for cmd in attributes if isinstance(cmd, ast.Cmd)]

        return ast.Segment(time, desc, segments, commands, ongoing)

    def parse_cmd(self) -> ast.Cmd:
        cmd = self.lexer.assert_token('CMD')

        desc = self.lexer.assert_token('DESC')

        self.lexer.assert_token('NL')

        if self.lexer.peak().type == 'OPEN':
            options = self.parse_options()
        else:
            options = []

        return ast.Cmd(cmd.value, desc.value, options)

    def parse_options(self) -> list[ast.Option]:
        return self.parse_block(self.parse_option)

    def parse_option(self) -> ast.Option:
        option: Token | None = self.lexer.assert_token('OPTION')

        match self.lexer.peak().type:
            case 'DURATION':
                value = self.lexer.assert_token('DURATION').value
            case 'DESC':
                value = self.lexer.assert_token('DESC').value
            case 'NL':
                value = ''
            case err:
                print(f'Error: expected (DURATION, DESC), found {err}')

        self.lexer.assert_token('NL')

        return ast.Option(option.value, value)
