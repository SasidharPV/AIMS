# SQL Scripts for Test Database Setup

-- Create staging table for data ingestion
CREATE TABLE CustomerStaging (
    CustomerId INT PRIMARY KEY,
    FirstName NVARCHAR(50),
    LastName NVARCHAR(50),
    Email NVARCHAR(100),
    Phone NVARCHAR(20),
    RegistrationDate DATE,
    Status NVARCHAR(20),
    CreatedDate DATETIME2 DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 DEFAULT GETUTCDATE()
);

-- Create production table
CREATE TABLE Customer (
    CustomerId INT PRIMARY KEY,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(100) NOT NULL,
    Phone NVARCHAR(20),
    RegistrationDate DATE NOT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'active',
    CreatedDate DATETIME2 DEFAULT GETUTCDATE(),
    ModifiedDate DATETIME2 DEFAULT GETUTCDATE()
);

-- Create report tables
CREATE TABLE ReportExecution (
    ReportId INT IDENTITY(1,1) PRIMARY KEY,
    ReportType NVARCHAR(50),
    ReportDate DATE,
    ExecutionDate DATETIME2 DEFAULT GETUTCDATE(),
    Status NVARCHAR(20),
    RecordCount INT,
    ExecutionTimeMs INT
);

-- Create stored procedure for report generation
CREATE PROCEDURE [dbo].[GenerateReport]
    @ReportType NVARCHAR(50),
    @ReportDate NVARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @RecordCount INT;
    
    -- Simulate different report types
    IF @ReportType = 'CustomerSummary'
    BEGIN
        SELECT 
            CustomerId,
            FirstName + ' ' + LastName as FullName,
            Email,
            Status,
            RegistrationDate
        FROM Customer 
        WHERE CAST(RegistrationDate AS DATE) = TRY_CAST(@ReportDate AS DATE)
        ORDER BY CustomerId;
        
        SET @RecordCount = @@ROWCOUNT;
    END
    ELSE IF @ReportType = 'SalesReport'
    BEGIN
        -- Simulate sales data
        SELECT 
            CustomerId,
            'Product_' + CAST(CustomerId % 10 AS VARCHAR) as ProductName,
            RAND() * 1000 as SalesAmount,
            @ReportDate as SalesDate
        FROM Customer 
        WHERE Status = 'active'
        ORDER BY CustomerId;
        
        SET @RecordCount = @@ROWCOUNT;
    END
    ELSE IF @ReportType = 'InventoryReport'
    BEGIN
        -- Simulate inventory data
        SELECT 
            'INV_' + CAST(ROW_NUMBER() OVER (ORDER BY CustomerId) AS VARCHAR) as InventoryId,
            'Product_' + CAST(CustomerId % 10 AS VARCHAR) as ProductName,
            ABS(CHECKSUM(NEWID())) % 100 + 1 as Quantity,
            @ReportDate as ReportDate
        FROM Customer 
        ORDER BY CustomerId;
        
        SET @RecordCount = @@ROWCOUNT;
    END
    ELSE
    BEGIN
        -- Unknown report type - cause an error
        RAISERROR('Unknown report type: %s', 16, 1, @ReportType);
        RETURN;
    END
    
    -- Log the report execution
    INSERT INTO ReportExecution (ReportType, ReportDate, Status, RecordCount, ExecutionTimeMs)
    VALUES (@ReportType, TRY_CAST(@ReportDate AS DATE), 'Success', @RecordCount, ABS(CHECKSUM(NEWID())) % 5000 + 100);
    
END;

-- Create error logging table
CREATE TABLE PipelineErrors (
    ErrorId INT IDENTITY(1,1) PRIMARY KEY,
    PipelineName NVARCHAR(100),
    RunId NVARCHAR(100),
    ErrorType NVARCHAR(50),
    ErrorMessage NVARCHAR(MAX),
    ErrorCode NVARCHAR(20),
    ActivityName NVARCHAR(100),
    ErrorTimestamp DATETIME2 DEFAULT GETUTCDATE(),
    Severity NVARCHAR(20),
    Environment NVARCHAR(20)
);

-- Insert sample error data for testing
INSERT INTO PipelineErrors (PipelineName, RunId, ErrorType, ErrorMessage, ErrorCode, ActivityName, Severity, Environment)
VALUES 
('DataIngestionPipeline', 'run-001-prod', 'transient', 'Connection timeout to source database', 'CONN_TIMEOUT', 'CopyCustomerData', 'High', 'Production'),
('ETLTransformPipeline', 'run-002-prod', 'data_quality', 'Schema validation failed: Missing column customer_id', 'SCHEMA_ERROR', 'TransformData', 'Critical', 'Production'),
('ReportGenerationPipeline', 'run-003-prod', 'configuration', 'Access denied: Insufficient permissions', 'ACCESS_DENIED', 'CheckPermissions', 'Medium', 'Production'),
('DataValidationPipeline', 'run-001-stg', 'transient', 'Temporary storage account access issue', 'STORAGE_THROTTLE', 'ExecuteValidationRule', 'Low', 'Staging'),
('DataIngestionPipeline', 'run-001-dev', 'configuration', 'Invalid connection string format', 'CONFIG_ERROR', 'ValidateSourceData', 'Low', 'Development'),
('ETLTransformPipeline', 'run-002-dev', 'data_quality', 'Test data contains invalid date formats', 'DATA_FORMAT', 'ValidateTransformation', 'Medium', 'Development');

-- Create pipeline run history table
CREATE TABLE PipelineRuns (
    RunId NVARCHAR(100) PRIMARY KEY,
    PipelineName NVARCHAR(100),
    Environment NVARCHAR(20),
    Status NVARCHAR(20),
    StartTime DATETIME2,
    EndTime DATETIME2,
    DurationMs INT,
    TriggeredBy NVARCHAR(50),
    Parameters NVARCHAR(MAX),
    RecordsProcessed INT,
    CreatedDate DATETIME2 DEFAULT GETUTCDATE()
);

-- Insert sample pipeline run data
INSERT INTO PipelineRuns (RunId, PipelineName, Environment, Status, StartTime, EndTime, DurationMs, TriggeredBy, RecordsProcessed)
VALUES 
('run-001-prod', 'DataIngestionPipeline', 'Production', 'Failed', DATEADD(minute, -30, GETUTCDATE()), DATEADD(minute, -25, GETUTCDATE()), 300000, 'Schedule', 0),
('run-002-prod', 'ETLTransformPipeline', 'Production', 'Failed', DATEADD(hour, -2, GETUTCDATE()), DATEADD(hour, -1, GETUTCDATE()), 3600000, 'Manual', 0),
('run-003-prod', 'ReportGenerationPipeline', 'Production', 'Failed', DATEADD(hour, -4, GETUTCDATE()), DATEADD(hour, -3, GETUTCDATE()), 1800000, 'Schedule', 0),
('run-001-stg', 'DataValidationPipeline', 'Staging', 'Succeeded', DATEADD(minute, -45, GETUTCDATE()), DATEADD(minute, -40, GETUTCDATE()), 300000, 'Manual', 150),
('run-001-dev', 'DataIngestionPipeline', 'Development', 'Failed', DATEADD(hour, -1, GETUTCDATE()), DATEADD(minute, -50, GETUTCDATE()), 600000, 'Manual', 0),
('run-002-dev', 'ETLTransformPipeline', 'Development', 'Failed', DATEADD(hour, -3, GETUTCDATE()), DATEADD(hour, -2, GETUTCDATE()), 1200000, 'Schedule', 0);

-- Create indexes for better performance
CREATE INDEX IX_PipelineErrors_Timestamp ON PipelineErrors(ErrorTimestamp);
CREATE INDEX IX_PipelineErrors_Environment ON PipelineErrors(Environment);
CREATE INDEX IX_PipelineErrors_Severity ON PipelineErrors(Severity);
CREATE INDEX IX_PipelineRuns_Environment ON PipelineRuns(Environment);
CREATE INDEX IX_PipelineRuns_Status ON PipelineRuns(Status);
CREATE INDEX IX_PipelineRuns_StartTime ON PipelineRuns(StartTime);

-- Create view for monitoring dashboard
CREATE VIEW v_PipelineMonitoringSummary AS
SELECT 
    Environment,
    PipelineName,
    COUNT(*) as TotalRuns,
    SUM(CASE WHEN Status = 'Succeeded' THEN 1 ELSE 0 END) as SuccessfulRuns,
    SUM(CASE WHEN Status = 'Failed' THEN 1 ELSE 0 END) as FailedRuns,
    CAST(SUM(CASE WHEN Status = 'Succeeded' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS DECIMAL(5,2)) as SuccessRate,
    AVG(DurationMs) as AvgDurationMs,
    MAX(StartTime) as LastRunTime
FROM PipelineRuns
WHERE StartTime >= DATEADD(day, -7, GETUTCDATE())
GROUP BY Environment, PipelineName;

-- Stored procedure for generating test failures
CREATE PROCEDURE [dbo].[GenerateTestFailure]
    @PipelineName NVARCHAR(100),
    @Environment NVARCHAR(20),
    @ErrorType NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @RunId NVARCHAR(100) = 'test-' + CAST(NEWID() AS NVARCHAR(36));
    DECLARE @ErrorMessage NVARCHAR(MAX);
    DECLARE @ErrorCode NVARCHAR(20);
    DECLARE @Severity NVARCHAR(20);
    
    -- Generate appropriate error based on type
    IF @ErrorType = 'transient'
    BEGIN
        SET @ErrorMessage = 'Connection timeout to external service';
        SET @ErrorCode = 'CONN_TIMEOUT';
        SET @Severity = 'High';
    END
    ELSE IF @ErrorType = 'data_quality'
    BEGIN
        SET @ErrorMessage = 'Data validation failed: Invalid record format';
        SET @ErrorCode = 'DATA_QUALITY';
        SET @Severity = 'Critical';
    END
    ELSE IF @ErrorType = 'configuration'
    BEGIN
        SET @ErrorMessage = 'Configuration error: Missing required parameter';
        SET @ErrorCode = 'CONFIG_ERROR';
        SET @Severity = 'Medium';
    END
    ELSE
    BEGIN
        SET @ErrorMessage = 'Unknown error occurred during pipeline execution';
        SET @ErrorCode = 'UNKNOWN';
        SET @Severity = 'High';
    END
    
    -- Insert pipeline run record
    INSERT INTO PipelineRuns (RunId, PipelineName, Environment, Status, StartTime, EndTime, DurationMs, TriggeredBy, RecordsProcessed)
    VALUES (@RunId, @PipelineName, @Environment, 'Failed', GETUTCDATE(), DATEADD(minute, 5, GETUTCDATE()), 300000, 'Test', 0);
    
    -- Insert error record
    INSERT INTO PipelineErrors (PipelineName, RunId, ErrorType, ErrorMessage, ErrorCode, ActivityName, Severity, Environment)
    VALUES (@PipelineName, @RunId, @ErrorType, @ErrorMessage, @ErrorCode, 'TestActivity', @Severity, @Environment);
    
    SELECT @RunId as GeneratedRunId, @ErrorType as ErrorType, @Severity as Severity;
END;