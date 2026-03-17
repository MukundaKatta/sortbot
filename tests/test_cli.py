"""Tests for the CLI commands."""

from click.testing import CliRunner

from sortbot.cli import cli


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_cli_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "SORTBOT" in result.output

    def test_simulate_command(self):
        result = self.runner.invoke(cli, ["simulate", "--items", "10", "--seed", "42"])
        assert result.exit_code == 0
        assert "Simulating" in result.output

    def test_report_command_table(self):
        result = self.runner.invoke(cli, ["report", "--items", "10", "--seed", "42"])
        assert result.exit_code == 0

    def test_report_command_summary(self):
        result = self.runner.invoke(cli, ["report", "--items", "10", "--seed", "42", "--format", "summary"])
        assert result.exit_code == 0
        assert "Diversion Rate" in result.output

    def test_info_command(self):
        result = self.runner.invoke(cli, ["info", "recyclable"])
        assert result.exit_code == 0
        assert "Recyclable" in result.output
