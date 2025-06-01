#!/usr/bin/env python3
"""Unit tests for client module"""

import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


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

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns expected result"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests"""
        # Define the side effect function for requests.get
        def side_effect(url):
            """Mock side effect for requests.get"""
            # Create a mock response object
            mock_response = Mock()

            # Check if the URL is for organization data
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            # Check if the URL is for repositories data
            elif url == cls.org_payload.get("repos_url"):
                mock_response.json.return_value = cls.repos_payload
            else:
                mock_response.json.return_value = {}

            return mock_response

        # Start the patcher for requests.get
        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class fixtures after running tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Integration test for public_repos method"""
        # Create client instance  
        client = GithubOrgClient("google")
        
        # Test that public_repos returns expected repos
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)
        
    def test_public_repos_with_license(self):
        """Integration test for public_repos method with license filter"""
        # Create client instance
        client = GithubOrgClient("google")
        
        # Test that public_repos with apache-2.0 license returns expected repos
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
