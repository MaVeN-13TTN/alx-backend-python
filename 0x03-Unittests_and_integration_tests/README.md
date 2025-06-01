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
- **Total**: 7 tests passing

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

## Resources

- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [parameterized](https://pypi.org/project/parameterized/)
- [How to mock a readonly property with mock?](https://stackoverflow.com/questions/17883247/how-to-mock-a-readonly-property-with-mock)
- [Memoization](https://en.wikipedia.org/wiki/Memoization)

## Best Practices

1. **Write Clear Test Names**: Test names should describe what is being tested
2. **Test Edge Cases**: Include boundary conditions and error scenarios
3. **Keep Tests Independent**: Each test should be able to run in isolation
4. **Use Descriptive Assertions**: Choose the most specific assertion method
5. **Mock External Dependencies**: Isolate units under test from external systems
6. **Verify Mock Interactions**: Always assert that mocks are called as expected
7. **Avoid Real Network Calls**: Use mocking to make tests fast and reliable
8. **Maintain Test Documentation**: Document complex test scenarios and expectations

## Author

This project is part of the ALX Backend Python curriculum focusing on advanced testing methodologies and best practices.
