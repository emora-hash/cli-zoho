"""Tests for CRM Related Records commands."""

import json


class TestCRMRelatedList:
    def test_list_json(self, invoke):
        payload = {
            "data": [
                {"id": "c1", "Full_Name": "John Smith", "Email": "john@example.com"},
                {"id": "c2", "Full_Name": "Jane Doe", "Email": "jane@example.com"},
            ],
            "info": {"more_records": False, "count": 2},
        }
        result = invoke(
            ["crm", "related", "list", "Deals", "999", "Contacts", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 2
        assert data["data"][0]["Full_Name"] == "John Smith"

    def test_list_empty_204(self, invoke):
        result = invoke(
            ["crm", "related", "list", "Deals", "999", "Products", "--json"],
            status_code=204,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"] == []

    def test_list_with_fields_filter(self, invoke):
        payload = {
            "data": [{"id": "c1", "Full_Name": "John Smith", "Email": "john@example.com"}],
            "info": {"more_records": False, "count": 1},
        }
        result = invoke(
            ["crm", "related", "list", "Deals", "999", "Contacts", "--fields", "Full_Name", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "Full_Name" in data["data"][0]

    def test_list_pagination(self, invoke):
        payload = {
            "data": [{"id": "c1", "Full_Name": "John"}],
            "info": {"more_records": False, "count": 1},
        }
        result = invoke(
            ["crm", "related", "list", "Accounts", "888", "Contacts", "--page", "2", "--json"],
            mock_response=payload,
        )
        assert result.exit_code == 0

    def test_list_table_output(self, invoke):
        payload = {
            "data": [{"id": "c1", "Full_Name": "John Smith"}],
            "info": {"more_records": False, "count": 1},
        }
        result = invoke(["crm", "related", "list", "Deals", "999", "Contacts"], mock_response=payload)
        assert result.exit_code == 0
        assert "John Smith" in result.output
