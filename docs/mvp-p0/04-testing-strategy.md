# 04. Testing Strategy (MVP P0)

**Version**: 1.0
**Status**: Draft

## 1. Testing Pyramid

### 1.1. Unit Tests (60%)
- **Scope**: Individual functions and classes (Wrappers, Models, Utils).
- **Tools**: `pytest`, `pytest-mock`.
- **Location**: `tests/test_core/`, `tests/test_servers/`.
- **Example**:
  ```python
  def test_nmap_parser():
      raw_xml = "<nmaprun>...</nmaprun>"
      result = parse_nmap_xml(raw_xml)
      assert result.open_ports == [80, 443]
  ```

### 1.2. Integration Tests (30%)
- **Scope**: Interaction between modules (Scheduler -> Server, Server -> Tool).
- **Tools**: `pytest-asyncio`, Docker (for tools).
- **Strategy**: Mock the actual MCP network calls but test the logic flow.
- **Distributed Scenarios**:
  - **Node Registration**: Verify scheduler accepts valid registration and rejects duplicates.
  - **Heartbeat Timeout**: Simulate node failure and verify scheduler marks it offline.
  - **Task Dispatch**: Verify scheduler routs task to correct node based on capabilities.

### 1.3. End-to-End (E2E) Tests (10%)
- **Scope**: Full CLI commands against a local test target (e.g., `dvwa` container).
- **Tools**: `pexpect` or shell scripts.
- **Example**:
  ```bash
  # run_e2e.sh
  python client/cli.py scan start --target localhost
  sleep 60
  python client/cli.py scan status <latest_id> | grep "COMPLETED"
  ```

## 2. Test Data Management
- **Fixtures**: Store sample Nmap XML/JSON outputs in `tests/data/samples/`.
- **Mocking**:
  - **Network**: Mock all external API calls.
  - **Subprocess**: Mock `subprocess.run` to avoid running actual Nmap during unit tests.

## 3. CI/CD Gates
- **Linting**: `flake8`, `black`, `isort`.
- **Type Check**: `mypy --strict`.
- **Tests**: Must pass 100% of Unit Tests.
- **Coverage**: Minimum 80% code coverage.

## 4. Performance Benchmarks
- **Startup Time**: CLI < 500ms.
- **Scheduler Throughput**: Handle 100 events/sec.
- **Memory**: < 200MB RSS under load.
