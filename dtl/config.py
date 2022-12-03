import configparser
import os

def load_config(config_path: str) -> dict[str, str]:
    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')

    if not config.has_section('DTL'):
        config.add_section('DTL')

    return {
        'DTL_dir': os.path.expanduser(config.get('DTL', 'DTL_dir', fallback='~/.DTL/')),
    }
