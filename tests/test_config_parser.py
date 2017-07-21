import json

import pytest

from chaps.configparser import ConfigParser


@pytest.fixture
def cfg_file(tmpdir):
    data = {
        'deps': {
            'config': 'chaps.configparser.ConfigParser',
            'container': 'chaps.Container'
        },
        'scopes': {
            'thread': 'chaps.scope.thread.ThreadScope'
        }
    }

    f = tmpdir.join('cfg.json')
    f.write(json.dumps(data))
    return f.realpath()


def test_module_import():
    config_parser = ConfigParser._import('chaps.configparser.ConfigParser')
    assert config_parser is ConfigParser


def test_deps_parse(cfg_file):
    config = ConfigParser(cfg_file)
    deps = config.deps()
    assert {'config', 'container'} == set(deps)
