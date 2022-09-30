# DTL
DTL — or Declarative Time Language — is a language used to describe a time period, which can be used to automate different tasks.

## DTL Syntax
DTL is an indentation based language. This means that whitespace is semantically important in DTL.

A DTL file consists of a list of segments. A segment consists of a time or timeperiod, and optionally also a description and a list of nested segments and commands.

### Segments
All segments in DTL begin with the charachter `@`. Following this is a list of 1 or more time units, in descending order of magnitude. E.g., `@2022 August 9th 12:00`, `@12:00`, `@Monday 7:00`, and `@2022`. Note that if a weekday is specified, neither a year, month, or date may be specified in that segment or its parent/child segments.

### Time units
- Year
  - Can be any 4-digit number.
  - E.g., `2022`, `1920`, `0102`
  - Note that DTL currently doesn't support years before `0000`.
- Month
  - `January`, `February`, `March`, `April`, `May`, `June`, `July`, `August`, `September`, `October`, `November`, `December`
- Date
  - `1st`, `21st`, `31st`
  - `2nd`, `22nd`
  - `3rd`, `23rd`
  - `4th` - `20th`, `24th` - `30th`
- Weekday
  - `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`
- Time
  - Can be any 3 or 4 digits with a colon before the 2 last digits.
  - E.g., `12:00`, `7:00`, `4:45`, `24:05`
  - Note that DTL uses 24-hour notation.

### Descriptions
A descriptions is any text within square brackets (`[...]`).

### Commands
All commands start with the charachter `!`. Any command can have an optional description. Currently commands have no effect.

### Sample DTL file
```
@August 1st
	@12:00 [Something happened]
		!note [This is a command, with some text attatched]
```
In the above example, `@August 1st` and `@12:00` are segment headers, `[Something happened]` is the description of the `@12:00` segment, and `!note [...]` is a command attatched to the `@12:00` segment.

# DTL command line interface
The DTL command line interface can be used to automatically record tasks into a DTL file, or to process an existing DTL file to extract any relevant data.

## Supported CLI commands:
 - `dtl [file] parse`
   - Parse and print parse-tree of the given file.
 - `dtl [file] format`
   - Reformat the given file to conform to the standard style guide.
 - `dtl [file] find (ongoing|static) [description]`
   - Prints a list of entries in the given file with the given description. Only returns ongoing or static entries with `ongoing` or `static` options; returns both by default.
 - `dtl [file] add [description]`
   - Adds an entry to the given file with the given description and the current time as its timestamp.
 - `dtl [file] begin [description]`\*
   - Same as `dtl add`, but marks the entry as ongoing.
 - `dtl [file] end [description]`\*
   - Closes an ongoing entry in the given file with the given description.

\*partial support

# Installation
To install DTL, clone this repository and run `pip install .`.
```
git clone https://github.com/JoelNiemela/DTL.git
cd DTL
pip install .
```

Note: you might have to use `sudo -H pip install .` if you want to install DTL to `/usr/bin`.

## Configuration
To configure DTL, create the file `~/.config/DTL/config.ini`.

### DTL config syntax:
`config.ini` is a `ini` file with the section `[DTL]`. The following properties are allowed:
- `DTL_dir`: The directory DTL will look for when trying to open files with the syntax `@<filename>`. Default value: `~/.DTL/`
