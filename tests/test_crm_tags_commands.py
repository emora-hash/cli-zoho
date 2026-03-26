"""Tests for CRM Tags commands."""

import json


class TestCRMTagsList:
    def test_list_json(self, invoke):
        payload = {
            "tags": [
                {"id": "t1", "name": "Hot Lead", "color_code": "#FF0000"},
                {"id": "t2", "name": "VIP", "color_code": "#FFD700"},
            ]
        }
        result = invoke(["crm", "tags", "list", "Deals", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tags" in data

    def test_list_table(self, invoke):
        payload = {"tags": [{"id": "t1", "name": "Hot Lead"}]}
        result = invoke(["crm", "tags", "list", "Deals"], mock_response=payload)
        assert result.exit_code == 0


class TestCRMTagsAdd:
    def test_add_single_tag(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success"}]}
        result = invoke(
            ["crm", "tags", "add", "Deals", "111", "Hot Lead", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_add_multiple_tags(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success"}]}
        result = invoke(
            ["crm", "tags", "add", "Deals", "111", "VIP", "Priority", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0

    def test_add_dry_run(self, invoke):
        result = invoke(["crm", "tags", "add", "Deals", "111", "Hot Lead", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "POST" in result.output


class TestCRMTagsRemove:
    def test_remove_tag(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success"}]}
        result = invoke(
            ["crm", "tags", "remove", "Deals", "111", "Hot Lead", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_remove_dry_run(self, invoke):
        result = invoke(["crm", "tags", "remove", "Deals", "111", "VIP", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "DELETE" in result.output
