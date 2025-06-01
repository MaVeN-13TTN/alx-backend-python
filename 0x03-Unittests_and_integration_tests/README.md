# 0x03. Unittests and Integration Tests

## Overview

This project focuses on implementing comprehensive unit tests and integration tests for Python applications. The main objectives are to understand the differences between unit and integration testing, learn common testing patterns, and implement robust test suites using Python's unittest framework.

## Learning Objectives

By the end of this project, you should be able to explain:

- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations and fixtures
- How to use the `unittest` framework effectively
- Best practices for writing maintainable and reliable tests

## Testing Concepts

### Unit Testing

**Unit testing** is the process of testing that a particular function returns expected results for different sets of inputs. Key characteristics:

- Tests individual functions in isolation
- Should test standard inputs and corner cases
- Most calls to additional functions should be mocked, especially network or database calls
- Answers the question: "If everything defined outside this function works as expected, does this function work as expected?"

### Integration Testing

**Integration tests** aim to test a code path end-to-end. Key characteristics:

- Test interactions between every part of your code
- Only low-level functions that make external calls (HTTP requests, file I/O, database I/O) are mocked
- Verify that different modules work together correctly
- Test real workflows and user scenarios

### Testing Patterns

#### Mocking
- Replace external dependencies with controlled test doubles
- Isolate the code under test from external systems
- Use `unittest.mock` for creating mock objects
- **HTTP Mocking**: Use `@patch` decorator to mock network calls
- **Mock Verification**: Validate mock calls with `assert_called_once_with()`
- **Response Mocking**: Create mock response objects with configurable return values

#### Parametrization
- Run the same test with different input values
- Use `@parameterized.expand` decorator to reduce code duplication
- Test multiple scenarios efficiently

#### Exception Testing
- Test that functions raise expected exceptions
- Use `assertRaises` context manager to capture exceptions
- Verify both exception type and error messages
- Test edge cases and error conditions

#### Decorator Testing
- Test decorator behavior and side effects
- Use `patch.object()` for mocking methods on specific classes
- Verify optimization patterns like memoization and caching
- Test that decorators preserve function behavior while adding features

#### Fixtures
- Set up test data and environment before tests run
- Clean up resources after tests complete
- Use `setUp()` and `tearDown()` methods in unittest

## Project Requirements

- All files interpreted/compiled on Ubuntu 18.04 LTS using Python 3.7
- Files should end with a new line
- First line: `#!/usr/bin/env python3`
- Code should follow pycodestyle (version 2.5)
- All files must be executable
- Comprehensive documentation for modules, classes, and functions
- All functions and coroutines must be type-annotated

## Testing Execution

Run tests using the unittest module:

```bash
# Run a specific test file
python -m unittest path/to/test_file.py

# Run with verbose output
python -m unittest path/to/test_file.py -v

# Run a specific test class
python -m unittest test_file.TestClassName

# Run a specific test method
python -m unittest test_file.TestClassName.test_method_name
```

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── README.md
├── utils.py                 # Utility functions to be tested
├── client.py               # Client module for integration tests
├── fixtures.py             # Test fixtures and data
├── test_utils.py           # Unit tests for utils module
└── test_client.py          # Integration tests for client module
```

## Dependencies

Install required packages:

```bash
pip install parameterized requests
```

**Note**: `unittest` and `unittest.mock` are part of Python's standard library and don't need to be installed separately.

## Tasks

### Project Progress Overview
- ✅ **Task 0**: Parameterized unit tests for successful scenarios (3 tests)
- ✅ **Task 1**: Parameterized unit tests for exception scenarios (2 tests)
- ✅ **Task 2**: Mock HTTP calls for external API testing (2 tests)
- ✅ **Task 3**: Parameterize and patch with memoization testing (1 test)
- ✅ **Task 4**: Parameterize and patch as decorators for client testing (2 tests)
- ✅ **Task 5**: Mocking a property for testing dependent properties (1 test)
- ✅ **Task 6**: More patching - testing complex method interactions (1 test)
- ✅ **Task 7**: Parameterize static method testing (2 tests)
- **Total**: 14 tests passing

### Task 0: Parameterize a unit test ✅

**Objective**: Create parameterized unit tests for the `utils.access_nested_map` function.

**Implementation**: 
- Created `TestAccessNestedMap` class inheriting from `unittest.TestCase`
- Implemented `test_access_nested_map` method with `@parameterized.expand` decorator
- Tested three scenarios:
  1. `nested_map={"a": 1}, path=("a",)` → expected: `1`
  2. `nested_map={"a": {"b": 2}}, path=("a",)` → expected: `{"b": 2}`
  3. `nested_map={"a": {"b": 2}}, path=("a", "b")` → expected: `2`

**Key Features**:
- Parameterized testing reduces code duplication
- Tests multiple input scenarios efficiently
- Method body kept to 2 lines as required
- All assertions use `assertEqual` for clear expectations

**Code Example**:
```python
@parameterized.expand([
    ({"a": 1}, ("a",), 1),
    ({"a": {"b": 2}}, ("a",), {"b": 2}),
    ({"a": {"b": 2}}, ("a", "b"), 2),
])
def test_access_nested_map(self, nested_map, path, expected):
    """Test that access_nested_map returns the expected result."""
    self.assertEqual(access_nested_map(nested_map, path), expected)
```

**Test Results**: All 3 parameterized test cases pass successfully.

### Task 1: Parameterize a unit test (Exception Testing) ✅

**Objective**: Create parameterized unit tests for exception scenarios in `utils.access_nested_map` function.

**Implementation**: 
- Added `test_access_nested_map_exception` method to `TestAccessNestedMap` class
- Used `@parameterized.expand` decorator for exception test cases
- Implemented `assertRaises` context manager to verify KeyError exceptions
- Tested two exception scenarios:
  1. `nested_map={}, path=("a",)` → expected KeyError: `'a'`
  2. `nested_map={"a": 1}, path=("a", "b")` → expected KeyError: `'b'`

**Key Features**:
- Exception testing with `assertRaises` context manager
- Verification of both exception type and error message
- Parameterized testing for multiple exception scenarios
- Proper error message validation using `str(context.exception)`

**Code Example**:
```python
@parameterized.expand([
    ({}, ("a",), "a"),
    ({"a": 1}, ("a", "b"), "b"),
])
def test_access_nested_map_exception(self, nested_map, path, expected_key):
    """Test that access_nested_map raises KeyError with expected message."""
    with self.assertRaises(KeyError) as context:
        access_nested_map(nested_map, path)
    self.assertEqual(str(context.exception), f"'{expected_key}'")
```

**Test Results**: All 5 total test cases pass successfully (3 success + 2 exception cases).

### Task 2: Mock HTTP calls ✅

**Objective**: Create unit tests for `utils.get_json` function using HTTP mocking to avoid external calls.

**Implementation**: 
- Created `TestGetJson` class inheriting from `unittest.TestCase`
- Implemented `test_get_json` method with `@parameterized.expand` and `@patch` decorators
- Used `unittest.mock.patch` to mock `requests.get` and avoid actual HTTP calls
- Tested two HTTP scenarios:
  1. `test_url="http://example.com", test_payload={"payload": True}`
  2. `test_url="http://holberton.io", test_payload={"payload": False}`

**Key Features**:
- **HTTP Mocking**: Complete isolation from external dependencies
- **Mock Verification**: Validates that `requests.get` was called exactly once per test
- **Return Value Testing**: Confirms function returns expected JSON payload
- **No Network Calls**: Tests run fast and reliably without internet dependency

**Technical Implementation**:
- Used `@patch('utils.requests.get')` to intercept HTTP calls
- Created `Mock` response objects with configurable `json()` method
- Verified mock call count and arguments using `assert_called_once_with()`
- Combined parameterization with mocking for efficient test coverage

**Code Example**:
```python
@parameterized.expand([
    ("http://example.com", {"payload": True}),
    ("http://holberton.io", {"payload": False}),
])
@patch('utils.requests.get')
def test_get_json(self, test_url, test_payload, mock_get):
    """Test that get_json returns expected result and makes correct HTTP call."""
    # Configure mock response
    mock_response = Mock()
    mock_response.json.return_value = test_payload
    mock_get.return_value = mock_response
    
    # Call the function
    result = get_json(test_url)
    
    # Assert that requests.get was called once with the correct URL
    mock_get.assert_called_once_with(test_url)
    
    # Assert that the result matches the expected payload
    self.assertEqual(result, test_payload)
```

**Test Results**: All 7 total test cases pass successfully (5 previous + 2 HTTP mocking tests).

### Task 3: Parameterize and patch (Memoization Testing) ✅

**Objective**: Test the `utils.memoize` decorator to ensure it properly caches method calls and avoids redundant executions.

**Memoization Concept**: 
Memoization is an optimization technique that stores the results of expensive function calls and returns the cached result when the same inputs occur again. The `utils.memoize` decorator converts a method into a cached property.

**Implementation**: 
- Created `TestMemoize` class inheriting from `unittest.TestCase`
- Implemented `test_memoize` method that defines a nested `TestClass` with:
  - `a_method()`: Returns 42 (the method to be cached)
  - `a_property()`: Decorated with `@memoize`, calls `a_method()`
- Used `patch.object()` to mock the `a_method` for call verification
- Tested that multiple property accesses return correct results but method is called only once

**Key Features**:
- **Caching Verification**: Confirms that repeated calls return cached values
- **Call Count Testing**: Uses `assert_called_once()` to verify optimization
- **Method Patching**: Demonstrates `patch.object()` for instance method mocking
- **Decorator Testing**: Shows how to test decorators and their behavior

**Technical Implementation**:
- Used `patch.object(TestClass, 'a_method')` to mock the underlying method
- Called the memoized property twice to test caching behavior
- Verified both return values and call count with separate assertions
- Demonstrated that memoization converts methods to cached properties

**Code Example**:
```python
def test_memoize(self):
    """Test that memoize decorator caches method calls correctly."""
    
    class TestClass:
        def a_method(self):
            return 42

        @memoize
        def a_property(self):
            return self.a_method()

    # Create an instance and patch the a_method
    with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
        test_instance = TestClass()
        
        # Call a_property twice
        result1 = test_instance.a_property
        result2 = test_instance.a_property
        
        # Assert both calls return the correct result
        self.assertEqual(result1, 42)
        self.assertEqual(result2, 42)
        
        # Assert a_method was called only once due to memoization
        mock_method.assert_called_once()
```

**Memoization Benefits**:
- **Performance Optimization**: Avoids repeated expensive computations
- **Caching Strategy**: Automatically stores results on first access
- **Property Conversion**: Makes methods behave like cached attributes
- **Memory vs. CPU Trade-off**: Uses memory to save computation time

**Test Results**: All 8 total test cases pass successfully (7 previous + 1 memoization test).

### Task 4: Parameterize and patch as decorators (Client Testing) ✅

**Objective**: Create unit tests for the `client.GithubOrgClient.org` property using both `@parameterized.expand` and `@patch` decorators to test the client class without making external HTTP calls.

**Client Overview**: 
The `GithubOrgClient` class provides an interface to interact with GitHub's organization API. The `org` property is decorated with `@memoize`, making it a cached property that fetches organization data from the GitHub API using the `get_json` utility function.

**Implementation**: 
- Created `TestGithubOrgClient` class inheriting from `unittest.TestCase`
- Implemented `test_org` method with both decorators:
  - `@parameterized.expand` for testing multiple organization names
  - `@patch('client.get_json')` for mocking the HTTP call
- Tested two organization scenarios:
  1. `"google"` - Google's GitHub organization
  2. `"abc"` - A simple test organization name

**Key Features**:
- **Combined Decorators**: Shows how to use both parameterization and patching together
- **Property Testing**: Tests memoized properties (accessed without parentheses)
- **Client Class Testing**: Demonstrates testing of class-based API clients
- **No External Calls**: Complete isolation from GitHub API using mocking

**Technical Implementation**:
- Used `@patch('client.get_json')` to mock the utility function import
- Configured mock return value with realistic GitHub API response structure
- Verified that `get_json` is called with the correct GitHub API URL format
- Tested that the property returns the mocked response correctly

**Understanding Memoized Properties**:
The `@memoize` decorator in `utils.py` converts methods into properties:
```python
@memoize
def org(self) -> Dict:
    return get_json(self.ORG_URL.format(org=self._org_name))
```
This means `client.org` (not `client.org()`) accesses the cached property.

**Code Example**:
```python
@parameterized.expand([
    ("google",),
    ("abc",),
])
@patch('client.get_json')
def test_org(self, org_name, mock_get_json):
    """Test that GithubOrgClient.org returns the correct value"""
    # Mock return value for get_json
    expected_response = {
        "name": org_name,
        "repos_url": f"https://api.github.com/orgs/{org_name}/repos"
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
```

**Decorator Stack Explanation**:
1. `@parameterized.expand` creates separate test methods for each parameter set
2. `@patch('client.get_json')` injects a mock object as the last method parameter
3. The test method receives: `(self, org_name, mock_get_json)`

**API URL Testing**:
- Verifies that the correct GitHub API URL is constructed: `https://api.github.com/orgs/{org_name}`
- Tests URL formatting for different organization names
- Ensures proper API endpoint usage without making real requests

**Test Results**: All 10 total test cases pass successfully (8 previous + 2 client tests).

### Task 5: Mocking a property (Property Testing) ✅

**Objective**: Test the `client.GithubOrgClient._public_repos_url` property by mocking the `org` property it depends on. This demonstrates how to test properties that rely on other memoized properties.

**Property Dependencies**: 
The `_public_repos_url` property depends on the `org` property:
```python
@property
def _public_repos_url(self) -> str:
    """Public repos URL"""
    return self.org["repos_url"]
```

**Implementation**: 
- Added `test_public_repos_url` method to `TestGithubOrgClient` class
- Used `patch.object()` as a context manager to mock the `org` property
- Used `PropertyMock` to properly mock a property (not a regular method)
- Tested that `_public_repos_url` returns the expected URL from the mocked payload

**Key Features**:
- **Property Mocking**: Demonstrates using `PropertyMock` for mocking properties
- **Context Manager Usage**: Shows `patch.object()` as context manager instead of decorator
- **Dependency Isolation**: Tests one property by mocking its dependencies
- **Mock Verification**: Confirms that the mocked property was accessed

**Technical Implementation**:
- Used `patch.object(GithubOrgClient, 'org', new_callable=PropertyMock)` to mock the property
- Created a known payload with the `repos_url` field
- Verified that the `_public_repos_url` property returns the correct URL
- Confirmed that the `org` property was accessed during the test

**Property Mocking Concepts**:
- **PropertyMock vs Mock**: Use `PropertyMock` for properties, `Mock` for methods
- **new_callable Parameter**: Tells patch to use `PropertyMock` instead of default `Mock`
- **Context Manager Pattern**: Allows fine-grained control over mock lifecycle
- **Property Access Testing**: Verifies that dependent properties work correctly

**Code Example**:
```python
def test_public_repos_url(self):
    """Test that _public_repos_url returns the expected URL"""
    # Known payload with repos_url
    known_payload = {
        "repos_url": "https://api.github.com/orgs/google/repos"
    }
    
    # Use patch as context manager to mock the org property
    with patch.object(
        GithubOrgClient, 'org', new_callable=PropertyMock
    ) as mock_org:
        mock_org.return_value = known_payload
        
        # Create client instance
        client = GithubOrgClient("google")
        
        # Test that _public_repos_url returns the expected URL
        result = client._public_repos_url
        self.assertEqual(result, known_payload["repos_url"])
        
        # Verify that org property was accessed
        mock_org.assert_called_once()
```

**Mocking Patterns Demonstrated**:
- **Property Chain Testing**: How to test properties that depend on other properties
- **Context Manager Mocking**: Using `with patch.object()` for controlled scope
- **PropertyMock Usage**: Specific mock type for testing property access
- **Isolation Testing**: Testing individual components by mocking dependencies

**Why This Matters**:
- **Real-world Pattern**: Many properties depend on other properties or methods
- **Testability**: Shows how to test complex property chains in isolation
- **Performance**: Avoids expensive operations when testing dependent properties
- **Reliability**: Ensures properties work correctly without external dependencies

**Test Results**: All 11 total test cases pass successfully (10 previous + 1 property test).

### Task 6: More patching (Complex Method Testing) ✅

**Objective**: Test the `client.GithubOrgClient.public_repos` method by combining decorator and context manager patching patterns. This demonstrates testing methods that have multiple dependencies and complex internal logic.

**Method Overview**: 
The `public_repos` method retrieves a list of repository names from GitHub's API:
```python
def public_repos(self, license: str = None) -> List[str]:
    """Public repos"""
    json_payload = self.repos_payload  # Calls get_json internally
    public_repos = [
        repo["name"]
        for repo in json_payload
        if license is None or self.has_license(repo, license)
    ]
    return public_repos
```

**Dependencies Chain**:
1. `public_repos()` → calls `self.repos_payload`
2. `repos_payload` (memoized) → calls `get_json(self._public_repos_url)`
3. `_public_repos_url` (property) → returns URL from `self.org["repos_url"]`

**Implementation**: 
- Added `test_public_repos` method to `TestGithubOrgClient` class
- Used `@patch("client.get_json")` decorator to mock the HTTP call
- Used `patch.object()` as context manager to mock `_public_repos_url` property
- Tested that `public_repos` returns expected list of repository names
- Verified both mocks were called exactly once

**Key Features**:
- **Mixed Mocking Patterns**: Combines decorator and context manager approaches
- **Complex Dependency Testing**: Mocks multiple levels of the dependency chain
- **List Processing Testing**: Verifies data transformation from API payload to repo names
- **Call Verification**: Ensures both mocked dependencies are invoked properly

**Technical Implementation**:
- **Decorator Mocking**: Used `@patch("client.get_json")` to mock the HTTP layer
- **Context Manager Mocking**: Used `patch.object()` to mock the property dependency
- **Mock Payload Design**: Created realistic GitHub API response structure
- **Assertion Strategy**: Tested both return value and mock interaction patterns

**Mock Payload Structure**:
```python
test_payload = [
    {"name": "google/repo1", "license": {"key": "apache-2.0"}},
    {"name": "google/repo2", "license": {"key": "mit"}},
    {"name": "google/repo3", "license": None}
]
```

**Code Example**:
```python
@patch("client.get_json")
def test_public_repos(self, mock_get_json):
    """Test that public_repos returns expected list of repos"""
    # Mock payload for get_json - list of repositories
    test_payload = [
        {"name": "google/repo1", "license": {"key": "apache-2.0"}},
        {"name": "google/repo2", "license": {"key": "mit"}},
        {"name": "google/repo3", "license": None}
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
```

**Advanced Mocking Concepts**:
- **Layered Mocking**: Mock different levels of the call stack independently
- **Decorator vs Context Manager**: Choose the right pattern based on scope needs
- **Property vs Method Mocking**: Use `PropertyMock` for properties, `Mock` for methods
- **Call Count Verification**: Ensure mocks are invoked the expected number of times

**Testing Strategy Benefits**:
- **Isolated Testing**: Each method is tested independently of its dependencies
- **Fast Execution**: No actual HTTP calls or file I/O operations
- **Predictable Results**: Controlled mock responses ensure consistent test outcomes
- **Comprehensive Coverage**: Tests both success scenarios and mock interaction patterns

**Real-world Applications**:
- **API Client Testing**: Common pattern for testing services that interact with external APIs
- **Database Layer Testing**: Similar approach for testing data access layers
- **Service Integration Testing**: Useful for testing service-to-service communications
- **Complex Business Logic**: Ideal for testing methods with multiple external dependencies

**Test Results**: All 12 total test cases pass successfully (11 previous + 1 complex method test).

### Task 7: Parameterize (Static Method Testing) ✅

**Objective**: Test the `client.GithubOrgClient.has_license` static method using parameterized testing to verify license key matching functionality across different scenarios.

**Static Method Overview**: 
The `has_license` method is a static utility method that checks if a repository has a specific license:
```python
@staticmethod
def has_license(repo: Dict[str, Dict], license_key: str) -> bool:
    """Static: has_license"""
    assert license_key is not None, "license_key cannot be None"
    try:
        has_license = access_nested_map(repo, ("license", "key")) == license_key
    except KeyError:
        return False
    return has_license
```

**Method Logic**:
1. **Input Validation**: Asserts that `license_key` is not `None`
2. **Nested Access**: Uses `access_nested_map` to safely access `repo["license"]["key"]`
3. **License Matching**: Compares the repository's license key with the expected license key
4. **Error Handling**: Returns `False` if a `KeyError` occurs (missing license data)

**Implementation**: 
- Added `test_has_license` method to `TestGithubOrgClient` class
- Used `@parameterized.expand` decorator to test multiple scenarios
- Tested both matching and non-matching license scenarios as specified
- Each test case includes repository data, license key, and expected result

**Test Scenarios**:
1. **License Match**: Repository with `"my_license"` matches `"my_license"` → `True`
2. **License Mismatch**: Repository with `"other_license"` doesn't match `"my_license"` → `False`

**Key Features**:
- **Static Method Testing**: Demonstrates testing class static methods directly
- **Parameterized Testing**: Uses `@parameterized.expand` for multiple test cases
- **Boolean Result Testing**: Tests methods that return boolean values
- **Edge Case Coverage**: Tests both positive and negative scenarios

**Technical Implementation**:
- **Direct Method Call**: Called `GithubOrgClient.has_license()` directly as a static method
- **No Instance Required**: Static methods don't need class instantiation
- **Simple Assertions**: Used `assertEqual` to verify boolean return values
- **Realistic Test Data**: Used dictionary structures that match GitHub API format

**Parameterization Pattern**:
```python
@parameterized.expand([
    ({"license": {"key": "my_license"}}, "my_license", True),
    ({"license": {"key": "other_license"}}, "my_license", False),
])
def test_has_license(self, repo, license_key, expected):
    """Test that has_license returns expected result"""
    result = GithubOrgClient.has_license(repo, license_key)
    self.assertEqual(result, expected)
```

**Code Example**:
```python
@parameterized.expand([
    ({"license": {"key": "my_license"}}, "my_license", True),
    ({"license": {"key": "other_license"}}, "my_license", False),
])
def test_has_license(self, repo, license_key, expected):
    """Test that has_license returns expected result"""
    result = GithubOrgClient.has_license(repo, license_key)
    self.assertEqual(result, expected)
```

**Static Method Testing Benefits**:
- **Isolation**: No dependencies on instance state or external resources
- **Fast Execution**: Direct method calls without setup overhead
- **Pure Logic Testing**: Focus on algorithm and business logic verification
- **Predictable Results**: Deterministic output based on input parameters

**Testing Strategy**:
- **Positive Testing**: Verify correct behavior when license matches
- **Negative Testing**: Verify correct behavior when license doesn't match
- **Input Validation**: Ensure method handles different input structures correctly
- **Return Value Verification**: Confirm boolean return values are accurate

**Real-world Applications**:
- **License Compliance**: Common in open-source project management
- **Repository Filtering**: Used in tools that filter repositories by license type
- **Compliance Auditing**: Essential for enterprise software compliance checks
- **API Client Utilities**: Typical utility method pattern in API client libraries

**Parameterization Advantages**:
- **Code Reuse**: Single test method handles multiple scenarios
- **Maintainability**: Easy to add new test cases by expanding the parameter list
- **Clear Documentation**: Parameter names clearly indicate what's being tested
- **Comprehensive Coverage**: Ensures multiple edge cases are tested systematically

**Test Results**: All 14 total test cases pass successfully (12 previous + 2 static method tests).

## Resources

- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [parameterized](https://pypi.org/project/parameterized/)
- [How to mock a readonly property with mock?](https://stackoverflow.com/questions/17883247/how-to-mock-a-readonly-property-with-mock)
- [PropertyMock — Mock object for properties](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock)
- [Memoization](https://en.wikipedia.org/wiki/Memoization)

## Best Practices

1. **Write Clear Test Names**: Test names should describe what is being tested
2. **Test Edge Cases**: Include boundary conditions and error scenarios
3. **Keep Tests Independent**: Each test should be able to run in isolation
4. **Use Descriptive Assertions**: Choose the most specific assertion method
5. **Mock External Dependencies**: Isolate units under test from external systems
6. **Verify Mock Interactions**: Always assert that mocks are called as expected
7. **Avoid Real Network Calls**: Use mocking to make tests fast and reliable
8. **Test Decorator Behavior**: Verify that decorators work correctly and preserve functionality
9. **Use patch.object for Instance Methods**: Mock specific methods on classes when needed
10. **Maintain Test Documentation**: Document complex test scenarios and expectations

## Author

This project is part of the ALX Backend Python curriculum focusing on advanced testing methodologies and best practices.
