# DTL
DTL — or Declarative Time Language — is a language used to describe a time period, which can be used to automate different tasks.

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
 - `dtl [file] begin [description]`
   - Same as `dtl add`, but marks the entry as ongoing.
 - `dtl [file] end [description]`
   - Closes an ongoing entry in the given file with the given description.

# Installation
To install DTL, clone this repository and run `pip install .`.
```
git clone https://github.com/JoelNiemela/DTL.git
cd DTL
pip install .
```

Note: you might have to use `sudo -H pip install .` if you want to install DTL to `/usr/bin`.
