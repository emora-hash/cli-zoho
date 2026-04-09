"""Tests for shared pagination utilities."""

from cli_zoho.shared.zoho_cli_shared_pagination import paginate_all


class TestPaginateAll:
    def test_paginate_all_three_pages(self):
        """Verify paginate_all aggregates records across multiple pages."""
        pages = {
            1: {"data": [{"id": "1"}, {"id": "2"}], "has_more": True, "count": 2},
            2: {"data": [{"id": "3"}, {"id": "4"}], "has_more": True, "count": 2},
            3: {"data": [{"id": "5"}], "has_more": False, "count": 1},
        }

        def fetch_page(page_num):
            return pages[page_num]

        result = paginate_all(fetch_page)
        assert len(result["data"]) == 5
        assert result["has_more"] is False
        assert result["count"] == 5
        ids = [r["id"] for r in result["data"]]
        assert ids == ["1", "2", "3", "4", "5"]

    def test_paginate_all_empty_first_page(self):
        """Verify paginate_all handles an empty first page gracefully."""

        def fetch_page(page_num):
            return {"data": [], "has_more": False, "count": 0}

        result = paginate_all(fetch_page)
        assert result["data"] == []
        assert result["count"] == 0
        assert result["has_more"] is False

    def test_paginate_all_safety_cap(self):
        """Verify paginate_all stops at max_records even if has_more is True."""

        def fetch_page(page_num):
            # Each page returns 200 records, has_more always True
            return {
                "data": [{"id": str(i + (page_num - 1) * 200)} for i in range(200)],
                "has_more": True,
                "count": 200,
            }

        result = paginate_all(fetch_page, max_records=500)
        assert len(result["data"]) == 500
        assert result["count"] == 500
