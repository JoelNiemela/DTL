from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    long_description = file.read()

setup(
	name='DTL',
	version='0.1.3',
	author='Joel Niemela',
	author_email='joel@niemela.se',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/JoelNiemela/DTL',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3'
	],
	packages=find_packages(),
    python_requires='>=3.10',
	entry_points={
		'console_scripts': [
			'dtl=dtl.cli:main',
		],
	},
)
