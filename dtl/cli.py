#!/usr/bin/env python3

import sys

from dtl.parse import Parser
from dtl import ast

def assert_argc(args, count):
	if len(args) < count:
		if count == 1:
			print('Error: expected an argument')
		else:
			print(f'Error: expected {count} arguments')
		exit(1)

def parse_file(file_path):
	parser = Parser(debug = False)

	try:
		with open(file_path, 'r') as file:
			tree = parser.parse(file.read())
	except FileNotFoundError:
		print(f'Error: can\'t find file "{file_path}"')
		exit(1)

	return tree

def write_file(file_path, tree):
	with open(file_path, 'w') as file:
		file.write(tree.format())

def parse_cmd(file_path, args):
	print(parse_file(file_path))
	print(parse_file(file_path).format())

def format_cmd(file_path, args):
	tree = parse_file(file_path)

	write_file(file_path, tree)

def find_cmd(file_path, args):
	assert_argc(args, 1)

	if args[0] == 'ongoing':
		ongoing = True
		description = args[1]
	elif args[0] == 'static':
		ongoing = False
		description = args[1]
	else:
		ongoing = None
		description = args[0]

	tree = parse_file(file_path)

	print(''.join([f.format(full_time = True) for f in tree.find(description, ongoing=ongoing)]))

def add_cmd(file_path, args):
	assert_argc(args, 1)

	description = args[0]

	tree = parse_file(file_path)

	tree.create_entry(ast.Time.now(), description)

	print(tree.format())

	write_file(file_path, tree)

def begin_cmd(file_path, args):
	assert_argc(args, 1)

	description = args[0]

	tree = parse_file(file_path)

	already_ongoing = tree.find(description, ongoing = True)
	if len(already_ongoing) > 0:
		if len(already_ongoing) == 1:
			print(f'There\'s already an ongoing entry with the name "{description}":')
		else:
			print(f'There are already ongoing entries with the name "{description}":')

		print()
		print(''.join(['\t' + f.format(full_time = True) for f in already_ongoing]))
		exit(0)

	tree.create_entry(ast.Time.now(), description, ongoing = True)

	print(tree.format())

	write_file(file_path, tree)

def end_cmd(file_path, args):
	assert_argc(args, 1)

	description = args[0]

	tree = parse_file(file_path)

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

	write_file(file_path, tree)

def main():
	flags    = [flag.lstrip('-') for flag in sys.argv[1:] if flag[0] == '-']
	commands = [cmd              for cmd  in sys.argv[1:] if  cmd[0] != '-']

	if len(commands) < 2:
		print('Error: expected a file path and a command')
		exit(1)

	file, cmd, *args = commands

	if cmd == 'parse':
		parse_cmd(file, args)
	if cmd == 'format':
		format_cmd(file, args)
	if cmd == 'find':
		find_cmd(file, args)
	if cmd == 'add':
		add_cmd(file, args)
	if cmd == 'begin':
		begin_cmd(file, args)
	if cmd == 'end':
		end_cmd(file, args)

if __name__ == "__main__":
	main()

