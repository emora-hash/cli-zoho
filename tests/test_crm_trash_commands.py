"""Tests for CRM Recycle Bin (trash) commands."""

import json


class TestCRMTrashList:
    def test_list_json(self, invoke):
        payload = {
            "data": [
                {"id": "d1", "display_name": "Old Deal", "module": {"api_name": "Deals"}},
                {"id": "d2", "display_name": "Stale Lead", "module": {"api_name": "Leads"}},
            ],
            "info": {"more_records": False, "count": 2},
        }
        result = invoke(["crm", "trash", "list", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2
        assert data["data"][0]["display_name"] == "Old Deal"

    def test_list_with_module_filter(self, invoke):
        payload = {
            "data": [{"id": "d1", "display_name": "Old Deal", "module": {"api_name": "Deals"}}],
            "info": {"more_records": False, "count": 1},
        }
        result = invoke(["crm", "trash", "list", "--module", "Deals", "--json"], mock_response=payload)
        assert result.exit_code == 0

    def test_list_empty_204(self, invoke):
        result = invoke(["crm", "trash", "list", "--json"], status_code=204)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"] == []


class TestCRMTrashRestore:
    def test_restore_single(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success", "details": {"id": "d1"}}]}
        result = invoke(["crm", "trash", "restore", "d1", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_restore_multiple(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success"}]}
        result = invoke(["crm", "trash", "restore", "d1", "d2", "--json"], mock_response=payload)
        assert result.exit_code == 0

    def test_restore_dry_run(self, invoke):
        result = invoke(["crm", "trash", "restore", "d1", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "PUT" in result.output


class TestCRMTrashPurge:
    def test_purge_single(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success"}]}
        result = invoke(["crm", "trash", "purge", "d1", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_purge_dry_run(self, invoke):
        result = invoke(["crm", "trash", "purge", "d1", "d2", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "DELETE" in result.output
        assert "recycle_bin" in result.output
