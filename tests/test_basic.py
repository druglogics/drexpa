"""
Basic tests for DREXPA package
"""
import sys


def test_version():
    """Test that version is accessible"""
    import drexpa
    assert hasattr(drexpa, '__version__')
    assert isinstance(drexpa.__version__, str)
    assert len(drexpa.__version__) > 0
    print("✓ Version test passed")


def test_lazy_import():
    """Test that pandas is not imported at package level"""
    # Clear any previous imports
    modules_before = set(sys.modules.keys())

    import drexpa

    modules_after = set(sys.modules.keys())
    new_modules = modules_after - modules_before

    # pandas should not be in newly imported modules
    assert 'pandas' not in new_modules
    print("✓ Lazy import test passed")


def test_config_loading():
    """Test that default config can be loaded"""
    from drexpa.config import get_default_config
    config = get_default_config()
    assert isinstance(config, dict)
    assert 'global' in config
    assert 'paths' in config
    print("✓ Config loading test passed")


if __name__ == "__main__":
    test_version()
    test_lazy_import()
    test_config_loading()
    print("\nAll basic tests passed!")