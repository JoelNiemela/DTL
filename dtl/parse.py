from dtl.ast import Cmd, File, Option, Segment, Time
from dtl.tokenize import Lexer, Token

from functools import partial
from typing import Callable


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, debug: bool = False) -> None:
        self.lexer = Lexer(debug=debug)

    def parse(self, src: str) -> File:
        self.lexer.tokenize(src)

        header_time_tokens = {}
        if self.lexer.peak().type == 'FOR':
            self.lexer.pop()

            while self.lexer.peak().type != 'COLON':
                time: Token = self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])
                header_time_tokens[time.type] = time.value

            self.lexer.assert_token('COLON')
            self.lexer.assert_token('NL')

        header_time = Time(header_time_tokens)

        segments: list[Segment] = []
        while self.lexer.peak().type == 'AT':
            segments.append(self.parse_time(header_time))

        tree: File = File(header_time, segments)
        tree.validate(header_time)

        return tree

    def parse_block[T](self, fn: Callable[[], T]) -> list[T]:
        self.lexer.assert_token('OPEN')

        ln: list[T] = []
        while self.lexer.peak().type != 'END':
            ln.append(fn())

        self.lexer.assert_token('END')

        return ln

    def parse_attributes(self, parent_time: Time) -> list[Segment | Cmd]:
        return self.parse_block(partial(self.parse_attribute, parent_time))

    def parse_attribute(self, parent_time: Time) -> Segment | Cmd:
        match self.lexer.peak().type:
            case 'AT':
                return self.parse_time(parent_time)
            case 'CMD':
                return self.parse_cmd()
            case err:
                print(f'Error: expected CMD, AT, found {err}')
                raise ParseError(f'Error: expected CMD, AT, found {err}')

    def parse_time(self, parent_time: Time) -> Segment:
        self.lexer.assert_token('AT')
        time_tokens: list[Token] = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
        while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
            time_tokens.append(self.lexer.pop())

        time: Time = Time({t.type: t.value for t in time_tokens}, parent=parent_time)

        if self.lexer.peak().type == 'PERIOD':
            self.lexer.assert_token('PERIOD')
            period_end_tokens: list[Token] = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
            while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
                period_end_tokens.append(self.lexer.pop())

            period_end: Time = Time({t.type: t.value for t in period_end_tokens}, parent=parent_time)

            time.period = True
            time.end = period_end

        ongoing: bool = False
        if self.lexer.peak().type == 'ONGOING':
            self.lexer.assert_token('ONGOING')
            ongoing = True

        desc: str | None = None
        if self.lexer.peak().type == 'DESC':
            desc = self.lexer.assert_token('DESC').value

        self.lexer.assert_token('NL')

        attributes: list[Segment | Cmd] = []
        if self.lexer.peak().type == 'OPEN':
            attributes = self.parse_attributes(time)

        segments: list[Segment] = [seg for seg in attributes if isinstance(seg, Segment)]
        commands: list[Cmd]     = [cmd for cmd in attributes if isinstance(cmd, Cmd)]

        return Segment(time, desc, segments, commands, ongoing)

    def parse_cmd(self) -> Cmd:
        cmd = self.lexer.assert_token('CMD')

        desc = self.lexer.assert_token('DESC')

        self.lexer.assert_token('NL')

        options: list[Option] = []
        if self.lexer.peak().type == 'OPEN':
            options = self.parse_options()

        return Cmd(cmd.value, desc.value, options)

    def parse_options(self) -> list[Option]:
        return self.parse_block(self.parse_option)

    def parse_option(self) -> Option:
        option: Token = self.lexer.assert_token('OPTION')

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

        return Option(option.value, value)
