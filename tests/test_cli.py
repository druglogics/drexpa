"""
Tests for DREXPA CLI functionality
"""
import subprocess
import sys
from pathlib import Path
from drexpa import __version__
from drexpa.step_registry import until_choices


class TestCLI:
    """Test CLI functionality"""

    def test_cli_version(self):
        """Test CLI version command"""
        result = subprocess.run(
            [sys.executable, "-m", "drexpa", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0
        assert f"DREXPA {__version__}" in result.stdout

    def test_cli_help(self):
        """Test CLI help command"""
        result = subprocess.run(
            [sys.executable, "-m", "drexpa", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode == 0
        assert "drug panel generation pipeline" in result.stdout
        assert "--config" in result.stdout
        assert "--until" in result.stdout
        assert "--steps" in result.stdout

    def test_cli_invalid_until_option(self):
        """Test CLI with invalid --until option"""
        result = subprocess.run(
            [sys.executable, "-m", "drexpa", "--until", "invalid"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        assert result.returncode != 0  # Should fail with invalid option

    def test_cli_valid_until_options(self):
        """Test CLI --until options are accepted"""
        for option in until_choices():
            result = subprocess.run(
                [sys.executable, "-m", "drexpa", "--until", option, "--help"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            # Just check that the option is accepted (help will show)
            assert result.returncode == 0