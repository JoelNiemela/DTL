import configparser
import os

def load_config(config_path):
	config = configparser.ConfigParser()
	config.read(config_path)

	if not config.has_section('DTL'):
		config.add_section('DTL')

	return {
		'DTL_dir': os.path.expanduser(config.get('DTL', 'DTL_dir', fallback='~/.DTL/')),
	}
