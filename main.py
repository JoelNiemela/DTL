#!/usr/bin/env python3

import sys
from datetime import datetime

from parse import Parser
import ast

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

		parser = Parser()
		with open(file_path, 'r') as file:
			ast = parser.parse(file.read())

		with open(file_path, 'w') as file:
			file.write(ast.format())

	if cmd == 'add':
		if len(args) < 2:
			print('Error: expected an argument')
			exit(1)

		description = args[0]
		file_path   = args[1]

		parser = Parser(debug=True)
		with open(file_path, 'r') as file:
			tree = parser.parse(file.read())

		now = datetime.now()

		year = now.strftime('%Y')
		month = now.strftime('%B')

		date = int(now.strftime('%d'))
		if 4 <= date <= 20 or 24 <= date <= 30:
			date = str(date) + "th"
		else:
			date = str(date) + ["st", "nd", "rd"][date % 10 - 1]

		time = now.strftime('%H:%M')

		tree.create_entry([
			ast.Time('YEAR', year),
			ast.Time('MONTH', month),
			ast.Time('DATE', date),
			ast.Time('TIME', time)
		], description)

		print(tree.format())

		with open(file_path, 'w') as file:
			file.write(tree.format())

	if cmd == 'begin':
		if len(args) < 2:
			print('Error: expected an argument')
			exit(1)

		description = args[0]
		file_path   = args[1]

		parser = Parser()
		with open(file_path, 'r') as file:
			tree = parser.parse(file.read())

		now = datetime.now()

		year = now.strftime('%Y')
		month = now.strftime('%B')

		date = int(now.strftime('%d'))
		if 4 <= date <= 20 or 24 <= date <= 30:
			date = str(date) + "th"
		else:
			date = str(date) + ["st", "nd", "rd"][date % 10 - 1]

		time = now.strftime('%H:%M')

		tree.create_entry([
			ast.Time('YEAR', year),
			ast.Time('MONTH', month),
			ast.Time('DATE', date),
			ast.Time('TIME', time)
		], description
		, ongoing=True)

		print(tree.format())

		with open(file_path, 'w') as file:
			file.write(tree.format())
