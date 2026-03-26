"""Tests for CRM Notes commands."""

import json


class TestCRMNotesList:
    def test_list_json(self, invoke):
        payload = {
            "data": [
                {"id": "n1", "Note_Content": "Spoke to customer", "Note_Title": "Call"},
                {"id": "n2", "Note_Content": "Sent quote", "Note_Title": "Quote"},
            ],
            "info": {"more_records": False, "count": 2},
        }
        result = invoke(["crm", "notes", "list", "Deals", "111", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2
        assert data["data"][0]["Note_Content"] == "Spoke to customer"

    def test_list_empty_204(self, invoke):
        result = invoke(["crm", "notes", "list", "Deals", "111", "--json"], status_code=204)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"] == []

    def test_list_pagination(self, invoke):
        payload = {
            "data": [{"id": "n1", "Note_Content": "First"}],
            "info": {"more_records": False, "count": 1},
        }
        result = invoke(["crm", "notes", "list", "Deals", "111", "--page", "2", "--json"], mock_response=payload)
        assert result.exit_code == 0


class TestCRMNotesCreate:
    def test_create_json(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "details": {"id": "n3"}, "status": "success"}]}
        result = invoke(
            ["crm", "notes", "create", "Deals", "111", "--note", "Follow up needed", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_create_with_title(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "details": {"id": "n4"}, "status": "success"}]}
        result = invoke(
            ["crm", "notes", "create", "Deals", "111", "--note", "Body text", "--title", "My Title", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0

    def test_create_dry_run(self, invoke):
        result = invoke(["crm", "notes", "create", "Deals", "111", "--note", "Test note", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "POST" in result.output
        assert "Notes" in result.output


class TestCRMNotesDelete:
    def test_delete_json(self, invoke):
        payload = {"data": [{"code": "SUCCESS", "status": "success"}]}
        result = invoke(["crm", "notes", "delete", "n1", "--json"], mock_response=payload)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["code"] == "SUCCESS"

    def test_delete_dry_run(self, invoke):
        result = invoke(["crm", "notes", "delete", "n1", "--dry-run"])
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "DELETE" in result.output
