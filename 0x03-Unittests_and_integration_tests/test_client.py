#!/usr/bin/env python3
"""Unit tests for client module"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient"""

    @parameterized.expand(
        [
            ("google",),
            ("abc",),
        ]
    )
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        # Mock return value for get_json
        expected_response = {
            "name": org_name,
            "repos_url": f"https://api.github.com/orgs/{org_name}/repos",
        }
        mock_get_json.return_value = expected_response

        # Create an instance of GithubOrgClient
        client = GithubOrgClient(org_name)

        # Access the org property
        result = client.org

        # Assert that the result is the expected response
        self.assertEqual(result, expected_response)

        # Assert that get_json was called once with the correct URL
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)


if __name__ == "__main__":
    unittest.main()
