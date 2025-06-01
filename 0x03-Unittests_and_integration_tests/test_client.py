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

    def test_public_repos_url(self):
        """Test that _public_repos_url returns the expected URL"""
        # Known payload with repos_url
        known_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"
        }

        # Use patch as context manager to mock the org property
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = known_payload

            # Create client instance
            client = GithubOrgClient("google")

            # Test that _public_repos_url returns the expected URL
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

            # Verify that org property was accessed
            mock_org.assert_called_once()

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns expected list of repos"""
        # Mock payload for get_json - list of repositories
        test_payload = [
            {"name": "google/repo1", "license": {"key": "apache-2.0"}},
            {"name": "google/repo2", "license": {"key": "mit"}},
            {"name": "google/repo3", "license": None},
        ]
        mock_get_json.return_value = test_payload

        # Use patch as context manager to mock _public_repos_url
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                "https://api.github.com/orgs/google/repos"
            )

            # Create client instance
            client = GithubOrgClient("google")

            # Call public_repos method
            result = client.public_repos()

            # Expected list of repo names
            expected_repos = ["google/repo1", "google/repo2", "google/repo3"]

            # Assert that the result matches expected repos
            self.assertEqual(result, expected_repos)

            # Verify that _public_repos_url property was accessed once
            mock_public_repos_url.assert_called_once()

        # Verify that get_json was called once
        mock_get_json.assert_called_once()


if __name__ == "__main__":
    unittest.main()
