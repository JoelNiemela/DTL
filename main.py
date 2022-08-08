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

		with open(file_path, 'r') as file:
			parser = Parser(debug=False)
			print(parser.parse(file.read()))

			file.seek(0)
			print(parser.parse(file.read()).format())

	if cmd == 'format':
		if len(args) < 1:
			print('Error: expected an argument')
			exit(1)

		file_path = args[0]

		with open(file_path, 'r+') as file:
			parser = Parser()
			ast = parser.parse(file.read())

			file.seek(0)
			file.write(ast.format())

	if cmd == 'add':
		if len(args) < 2:
			print('Error: expected an argument')
			exit(1)

		description = args[0]
		file_path   = args[1]

		with open(file_path, 'r+') as file:
			parser = Parser()
			ast = parser.parse(file.read())

			file.seek(0)
			file.write(ast.format())
