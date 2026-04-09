"""Tests for output formatting."""

import json
from click.testing import CliRunner
from cli_zoho.shared.zoho_cli_shared_output import render, _filter_fields


class TestFilterFields:
    def test_filter_envelope(self):
        data = {"data": [{"a": 1, "b": 2, "c": 3}], "has_more": False}
        result = _filter_fields(data, "a,c")
        assert result["data"] == [{"a": 1, "c": 3}]
        assert result["has_more"] is False

    def test_filter_list(self):
        data = [{"x": 10, "y": 20, "z": 30}]
        result = _filter_fields(data, "x,z")
        assert result == [{"x": 10, "z": 30}]

    def test_no_filter_passes_through(self):
        data = {"data": [{"a": 1}]}
        result = _filter_fields(data, None)
        assert result == data

    def test_missing_fields_return_none(self):
        data = [{"a": 1}]
        result = _filter_fields(data, "a,missing")
        assert result == [{"a": 1, "missing": None}]


class TestRender:
    def test_json_mode_outputs_json(self, capsys):
        data = {"key": "value"}
        render(data, json_mode=True, quiet=False)
        output = capsys.readouterr().out
        parsed = json.loads(output)
        assert parsed["key"] == "value"

    def test_quiet_mode_suppresses_output(self, capsys):
        render({"key": "value"}, json_mode=False, quiet=True)
        output = capsys.readouterr().out
        assert output == ""

    def test_table_mode_shows_records(self, capsys):
        data = {"data": [{"name": "Bucket", "price": 100}]}
        render(data, json_mode=False, quiet=False)
        output = capsys.readouterr().out
        assert "Bucket" in output
        assert "1 records" in output

    def test_empty_data_shows_message(self, capsys):
        data = {"data": []}
        render(data, json_mode=False, quiet=False)
        output = capsys.readouterr().out
        assert "No records" in output
