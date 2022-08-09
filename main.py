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

	if cmd == 'find':
		if len(args) < 2:
			print('Error: expected an argument')
			exit(1)

		if args[0] == 'ongoing':
			ongoing = True
			description = args[1]
			file_path   = args[2]
		elif args[0] == 'static':
			ongoing = False
			description = args[1]
			file_path   = args[2]
		else:
			ongoing = None
			description = args[0]
			file_path   = args[1]

		parser = Parser(debug=False)
		with open(file_path, 'r') as file:
			tree = parser.parse(file.read())

		print(''.join([f.format(full_time = True) for f in tree.find(description, ongoing=ongoing)]))

	if cmd == 'add':
		if len(args) < 2:
			print('Error: expected an argument')
			exit(1)

		description = args[0]
		file_path   = args[1]

		parser = Parser(debug=False)
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

		already_ongoing = tree.find(description, ongoing = True)
		if len(already_ongoing) > 0:
			if len(already_ongoing) == 1:
				print(f'There\'s already an ongoing entry with the name "{description}":')
			else:
				print(f'There are already ongoing entries with the name "{description}":')

			print()
			print(''.join(['\t' + f.format(full_time = True) for f in already_ongoing]))
			exit(0)

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

	if cmd == 'end':
		if len(args) < 2:
			print('Error: expected an argument')
			exit(1)

		description = args[0]
		file_path   = args[1]

		parser = Parser(debug=False)
		with open(file_path, 'r') as file:
			tree = parser.parse(file.read())

		finds = tree.find(description, ongoing = True, with_parent = True)

		if len(finds) == 0:
			print(f'No ongoing entry with the name "{description}"')
			exit(0)
		elif len(finds) > 1:
			print(f'There are multiple ongoing entries with the name "{description}":')
			print()
			print(''.join(['\t' + f[0].format(full_time = True) for f in finds]))
			while True:
				print(f'Which one would you like to end?')
				index = input(f'[1-{len(finds)}]: ')
				if index.isnumeric() and int(index) > 0 and int(index) <= len(finds):
					segment, parent = finds[int(index)-1]
					break
				else:
					if index == 'none':
						exit(0)
					print(f'Invalid index "{index}"')
					print(f'(type "none" to cancle)')
		else:
			print(f'Currently ongoing entry "{description}":')
			print()
			print(''.join(['\t' + f[0].format(full_time = True) for f in finds]))
			print('Are you sure you want to end this entry?')
			ans = input('(y/n): ')
			if ans != 'y':
				exit(0)

			segment, parent = finds[0]

		parent.segments = [e for e in parent.segments if e is not segment]

		with open(file_path, 'w') as file:
			file.write(tree.format())
