# Test Scenarios Configuration

## Overview
This file defines various test scenarios for the ADF Monitor Pro testing environment. These scenarios will be automatically executed to generate realistic success and failure patterns for monitoring.

## Scenario Categories

### 1. Success Scenarios
- **Normal Data Processing**: Regular successful pipeline runs with expected data volumes
- **Edge Case Handling**: Successful processing of boundary conditions
- **Recovery Scenarios**: Successful retries after transient failures

### 2. Failure Scenarios
- **Data Quality Issues**: Missing values, incorrect formats, schema mismatches
- **Configuration Errors**: Wrong connection strings, missing permissions
- **Transient Errors**: Network timeouts, storage throttling, temporary service unavailability
- **Resource Constraints**: Memory limits, timeout errors, concurrent execution limits

### 3. Monitoring Test Cases
- **Alert Generation**: Scenarios that should trigger specific alerts
- **Performance Metrics**: Load testing with various data volumes
- **Cross-Environment Testing**: Failures that affect multiple environments

## Test Scenario Definitions

### Scenario 1: Data Ingestion Success
```yaml
name: "DataIngestionSuccess"
pipeline: "DataIngestionPipeline"
frequency: "Every 30 minutes"
data_file: "customer_data_good.csv"
expected_outcome: "Success"
parameters:
  sourceFileName: "customer_data_good.csv"
  forceFailure: false
```

### Scenario 2: Data Quality Failure
```yaml
name: "DataQualityFailure"
pipeline: "DataIngestionPipeline"
frequency: "Every 2 hours"
data_file: "customer_data_with_errors.csv"
expected_outcome: "Failure"
parameters:
  sourceFileName: "customer_data_with_errors.csv"
  forceFailure: false
error_type: "data_quality"
```

### Scenario 3: Schema Mismatch Error
```yaml
name: "SchemaMismatchError"
pipeline: "ETLTransformPipeline"
frequency: "Every 4 hours"
data_file: "customer_data_wrong_format.csv"
expected_outcome: "Failure"
parameters:
  batchDate: "@formatDateTime(utcnow(), 'yyyy-MM-dd')"
  simulateFailure: false
error_type: "configuration"
```

### Scenario 4: Permission Denied Error
```yaml
name: "PermissionDeniedError"
pipeline: "ReportGenerationPipeline"
frequency: "Daily at 2 AM"
expected_outcome: "Failure"
parameters:
  reportDate: "@formatDateTime(subtractFromTime(utcnow(), 1, 'Day'), 'yyyy-MM-dd')"
  accessToken: "invalid_token"
error_type: "configuration"
```

### Scenario 5: Storage Throttling
```yaml
name: "StorageThrottling"
pipeline: "DataValidationPipeline"
frequency: "Every 6 hours"
expected_outcome: "Success after retries"
parameters:
  simulateThrottling: true
error_type: "transient"
```

### Scenario 6: Database Connection Timeout
```yaml
name: "DatabaseTimeout"
pipeline: "ETLTransformPipeline"
frequency: "Every 3 hours"
expected_outcome: "Failure"
parameters:
  batchDate: "@formatDateTime(utcnow(), 'yyyy-MM-dd')"
  simulateFailure: true
error_type: "transient"
```

### Scenario 7: Memory Exhaustion
```yaml
name: "MemoryExhaustion"
pipeline: "DataIngestionPipeline"
frequency: "Daily at 6 AM"
data_file: "large_dataset.csv"
expected_outcome: "Failure"
error_type: "resource_constraint"
```

### Scenario 8: Concurrent Pipeline Conflict
```yaml
name: "ConcurrentConflict"
pipeline: "ETLTransformPipeline"
frequency: "Every hour"
expected_outcome: "Failure"
parameters:
  batchDate: "@formatDateTime(utcnow(), 'yyyy-MM-dd')"
error_type: "resource_constraint"
```

## Environment-Specific Scenarios

### Production Environment
- Higher success rate (95%)
- Critical failures should trigger immediate alerts
- Longer retry intervals
- More conservative resource usage

### Staging Environment
- Moderate success rate (90%)
- Testing new configurations
- Shorter retry intervals
- Regular deployment testing

### Development Environment
- Variable success rate (85%)
- Experimental features
- Quick failure recovery
- Resource constraint testing

## Monitoring Validation Points

### Key Metrics to Monitor
1. **Pipeline Success Rate**: Overall percentage of successful runs
2. **Failure Categories**: Distribution of error types
3. **Recovery Time**: Time from failure to successful retry
4. **Resource Utilization**: Memory, CPU, and storage usage
5. **Alert Response Time**: Time from failure to alert notification

### Expected Behavior Validation
- Transient errors should auto-retry within defined limits
- Data quality issues should fail immediately without retry
- Configuration errors should generate specific error codes
- Cross-environment failures should be correlated

### Performance Benchmarks
- Pipeline execution time should be within expected ranges
- Resource usage should not exceed defined thresholds
- Alert generation should occur within 5 minutes of failure
- Dashboard updates should reflect changes within 2 minutes

## Test Data Volume Scenarios

### Small Dataset (< 1MB)
- Quick processing for functional testing
- Low resource utilization
- Fast failure detection

### Medium Dataset (1MB - 100MB)
- Realistic production volumes
- Standard resource utilization
- Typical processing times

### Large Dataset (> 100MB)
- Stress testing scenarios
- High resource utilization
- Extended processing times
- Memory and timeout testing

## Failure Pattern Simulation

### Gradual Degradation
- Success rate slowly decreases over time
- Resource utilization increases gradually
- Response times get progressively slower

### Sudden Failure
- Immediate complete failure
- All pipelines fail simultaneously
- Resource unavailability

### Intermittent Issues
- Random success/failure pattern
- Network instability simulation
- Service availability fluctuation

### Cascading Failures
- One failure triggers additional failures
- Dependency chain failures
- Cross-pipeline impact

These scenarios provide comprehensive testing coverage for the ADF Monitor Pro monitoring capabilities and ensure realistic failure patterns for validation.