#!/usr/bin/env python3

import sys

from parse import Parser

if __name__ == "__main__":
	flags    = [flag for flag in sys.argv[1:] if flag[0] == '-']
	commands = [cmd  for cmd  in sys.argv[1:] if  cmd[0] != '-']

	if len(commands) < 1:
		print('Error: expected at a command')
		exit(1)

	cmd, *args = commands

	if cmd == 'parse':
		if len(args) < 1:
			print('Error: expected an argument')
			exit(1)

		file_path = args[0]

		parser = Parser()
		with open(file_path, 'r') as file:
			print(parser.parse(file.read()))

