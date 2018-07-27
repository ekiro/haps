import pytest

from haps.config import Config, Configuration


@pytest.fixture
def base_config():
    Configuration.set('var_a', 'a')
    Configuration.set('var_b', 3)

    @Configuration.resolver('var_c')
    def _() -> str:
        return 'c'


@pytest.fixture
def env_config(monkeypatch):
    monkeypatch.setenv('HAPS_var_a', 'a')
    monkeypatch.setenv('VAR_B', 'b')
    Configuration.env_resolver('var_a')
    Configuration.env_resolver('var_b', 'VAR_B')
    Configuration.env_resolver('var_c', default='c')
    Configuration.env_resolver('var_d', default=lambda: 'd')


def test_base_config(base_config):
    assert Configuration().get_var('var_a') == 'a'
    assert Configuration().get_var('var_b') == 3
    assert Configuration().get_var('var_c') == 'c'


def test_base_config_injection(base_config):
    class SomeClass:
        var_a: str = Config()
        var_b: int = Config(default=10)
        c: str = Config('var_c')

        d_def: int = Config(default=11)
        d_def2: int = Config('var2', default=12)
        d_cal: int = Config(default=lambda: 5)

    sc = SomeClass()

    assert sc.var_a == 'a'
    assert sc.var_b == 3
    assert sc.c == 'c'

    assert sc.d_def == 11
    assert sc.d_def2 == 12
    assert sc.d_cal == 5


def test_env_config(env_config):
    assert Configuration().get_var('var_a') == 'a'
    assert Configuration().get_var('var_b') == 'b'
    assert Configuration().get_var('var_c') == 'c'
    assert Configuration().get_var('var_d') == 'd'


def test_configuration_chaining():
    Configuration().set("a", 1).set("b", 2).env_resolver("d").set("c", 3)
    assert Configuration().get_var('a') == 1
    assert Configuration().get_var('b') == 2
    assert Configuration().get_var('c') == 3
    assert Configuration().get_var('d', None) is None
