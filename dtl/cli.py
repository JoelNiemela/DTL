#!/usr/bin/env python3

import sys
import os

from dtl.parse import Parser
from dtl import ast
from dtl.config import load_config

from collections import defaultdict

VERSION = 'v0.1.6-alpha'

config = load_config(os.path.expanduser('~/.config/DTL/config.ini'))
DTL_dir = config['DTL_dir']

def assert_argc(args, count):
	if len(args) < count:
		if count == 1:
			print('Error: expected an argument')
		else:
			print(f'Error: expected {count} arguments')
		exit(1)

def require(name, value):
	if value == None:
		print(f'Error: argument "{name}" is required')
		exit(1)

def absoltue_path(file_path):
	if file_path is None:
		return None

	if len(file_path) > 0 and file_path[0] == '@':
		return f'{DTL_dir}/{file_path[1:]}.dtl'

	return file_path

def parse_file(file_path):
	require('file', file_path)

	parser = Parser(debug = False)

	try:
		with open(absoltue_path(file_path), 'r') as file:
			tree = parser.parse(file.read())
	except FileNotFoundError:
		print(f'Error: can\'t find file "{file_path}"')
		exit(1)

	return tree

def write_file(file_path, tree):
	require('file', file_path)

	with open(absoltue_path(file_path), 'w') as file:
		file.write(tree.format())

def parse_cmd(file_path, args):
	require('file', file_path)

	print(parse_file(file_path))
	print(parse_file(file_path).format())

def format_cmd(file_path, args):
	require('file', file_path)

	tree = parse_file(file_path)

	write_file(file_path, tree)

def find_cmd(file_path, args):
	require('file', file_path)

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

	print(''.join([f.format(ast.Time({})) for f in tree.find(description, ongoing=ongoing)]))

def add_cmd(file_path, args):
	require('file', file_path)

	assert_argc(args, 1)

	description = args[0]

	tree = parse_file(file_path)

	print(ast.Time.now())
	tree.insert_segment(ast.Segment(ast.Time.now(), description))

	print(tree.format())

	write_file(file_path, tree)

def begin_cmd(file_path, args):
	require('file', file_path)

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
		print(''.join(['\t' + f.format(ast.Time({})) for f in already_ongoing]))
		print('Are you sure you want to create another entry?')
		ans = input('(y/n): ')
		if ans != 'y':
			exit(0)

	tree.insert_segment(ast.Segment(ast.Time.now(), description, ongoing = True))

	print(tree.format())

	write_file(file_path, tree)

def end_cmd(file_path, args):
	require('file', file_path)

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
		print(''.join(['\t' + f[0].format(ast.Time({})) for f in finds]))
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
		print(''.join(['\t' + f[0].format(ast.Time({})) for f in finds]))
		print('Are you sure you want to end this entry?')
		ans = input('(y/n): ')
		if ans != 'y':
			exit(0)

		segment, parent = finds[0]

	parent_segments = defaultdict(list)
	for sub_time in parent.segments.keys():
		for seg in parent.segments[sub_time]:
			if seg is not segment:
				parent_segments[sub_time].append(seg)

	parent.segments = parent_segments

	segment.ongoing = False
	segment.time.period = True
	segment.time.end = ast.Time.now()

	tree.insert_segment(segment)

	write_file(file_path, tree)

def create_cmd(file_path, args):
	require('file', file_path)

	real_path = absoltue_path(file_path)

	if os.path.exists(real_path):
		print(f'Error: file "{file_path}" already exists.')
		exit(1)
	else:
		with open(real_path, 'w', encoding='utf-8'):
			pass

def help_cmd(file=None, cmd=None, args=[]):
	match cmd:
		case 'parse':
			print('dtl [file] parse\n')
			print('\tParse and print parse-tree of the given file.')
		case 'format':
			print('dtl [file] format\n')
			print('\tReformat the given file to conform to the standard style guide.')
		case 'find':
			print('dtl [file] find (ongoing|static) [description]\n')
			print('\tPrints a list of entries in the given file with the given description.')
			print('\tOnly returns ongoing or static entries with ongoing or static options;')
			print('\treturns both by default.')
		case 'add':
			print('dtl [file] add [description]\n')
			print('\tAdds an entry to the given file with the given description')
			print('\tand the current time as its timestamp.')
		case 'begin':
			print('dtl [file] begin [description]\n')
			print('\tSame as dtl add, but marks the entry as ongoing.')
		case 'end':
			print('dtl [file] end [description]\n')
			print('\tCloses an ongoing entry in the given file with the given description.')
		case None:
			print(f'DTL {VERSION}')
			print()
			print('Available commands:')
			print('\tdtl [file] parse')
			print('\t\tParse and print parse-tree of the given file.\n')
			print('\tdtl [file] format')
			print('\t\tReformat the given file to conform to the standard style guide.\n')
			print('\tdtl [file] find (ongoing|static) [description]')
			print('\t\tPrints a list of entries in the given file with the given description.')
			print('\t\tOnly returns ongoing or static entries with ongoing or static options;')
			print('\t\treturns both by default.\n')
			print('\tdtl [file] add [description]')
			print('\t\tAdds an entry to the given file with the given description')
			print('\t\tand the current time as its timestamp.\n')
			print('\tdtl [file] begin [description]')
			print('\t\tSame as dtl add, but marks the entry as ongoing.\n')
			print('\tdtl [file] end [description]')
			print('\t\tCloses an ongoing entry in the given file with the given description.\n')
			print()
			print('Flags:')
			print('\t--help')
			print('\t\tShow this message.')
			print('\t\tIf a command is specified: show more information about that command.\n')

		case _:
			print(f'Unknown command "{cmd}". Type "dtl --help" for a list of commands.')

def main():
	flags    = [flag.lstrip('-') for flag in sys.argv[1:] if flag[0] == '-']
	commands = [cmd              for cmd  in sys.argv[1:] if  cmd[0] != '-']

	cmd = None
	file = None
	match len(commands):
		case 0:
			args = commands
		case 1:
			cmd, *args = commands
		case _:
			file, cmd, *args = commands

	if 'help' in flags or 'h' in flags:
		help_cmd(file, cmd, args)
		exit(0)

	if 'version' in flags:
		print(f'DTL {VERSION}')
		exit(0)

	match cmd:
		case 'parse':
			parse_cmd(file, args)
		case 'format':
			format_cmd(file, args)
		case 'find':
			find_cmd(file, args)
		case 'add':
			add_cmd(file, args)
		case 'begin':
			begin_cmd(file, args)
		case 'end':
			end_cmd(file, args)
		case 'create':
			create_cmd(file, args)
		case _:
			help_cmd(file, cmd, args)

if __name__ == "__main__":
	main()

