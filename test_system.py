"""
Test Suite for ADF Monitoring System
"""
import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import modules to test
from database import DatabaseManager, PipelineRun, MonitoringAction
from genai_analyzer import GenAIAnalyzer, should_rerun_pipeline, log_decision_and_action
from adf_client import ADFClient
from mock_data import MockDataGenerator, create_test_scenario

class TestDatabaseManager:
    """Test database functionality"""
    
    def setup_method(self):
        """Setup test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test database"""
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database tables are created"""
        import sqlite3
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['pipeline_runs', 'monitoring_actions', 'error_patterns']
        for table in expected_tables:
            assert table in tables
        
        conn.close()
    
    def test_insert_pipeline_run(self):
        """Test inserting pipeline run"""
        pipeline_run = PipelineRun(
            run_id="test-run-001",
            pipeline_name="TestPipeline",
            status="Failed",
            start_time=datetime.now(),
            end_time=datetime.now(),
            error_message="Test error",
            factory_name="TestFactory"
        )
        
        success = self.db_manager.insert_pipeline_run(pipeline_run)
        assert success
        
        # Verify data was inserted
        failed_runs = self.db_manager.get_failed_runs_last_hours(1)
        assert len(failed_runs) == 1
        assert failed_runs[0]['run_id'] == "test-run-001"
    
    def test_get_dashboard_stats(self):
        """Test dashboard statistics"""
        # Insert some test data
        pipeline_run = PipelineRun(
            run_id="test-run-002",
            pipeline_name="TestPipeline",
            status="Succeeded",
            start_time=datetime.now(),
            end_time=datetime.now(),
            error_message=None,
            factory_name="TestFactory"
        )
        
        self.db_manager.insert_pipeline_run(pipeline_run)
        
        stats = self.db_manager.get_dashboard_stats()
        assert 'total_runs_today' in stats
        assert 'failed_runs_today' in stats
        assert 'success_rate_today' in stats
        assert stats['total_runs_today'] >= 1

class TestGenAIAnalyzer:
    """Test GenAI analyzer functionality"""
    
    def setup_method(self):
        """Setup test analyzer"""
        self.analyzer = GenAIAnalyzer()
    
    def test_mock_analysis_transient_error(self):
        """Test mock analysis for transient errors"""
        error_message = "Connection timeout occurred while connecting to database"
        result = self.analyzer._get_mock_analysis(error_message)
        
        assert result['success'] is True
        assert result['analysis']['error_type'] == 'transient'
        assert result['analysis']['should_retry'] is True
        assert result['analysis']['confidence_score'] > 0
    
    def test_mock_analysis_data_quality_error(self):
        """Test mock analysis for data quality errors"""
        error_message = "Validation failed: Missing required column 'customer_id'"
        result = self.analyzer._get_mock_analysis(error_message)
        
        assert result['success'] is True
        assert result['analysis']['error_type'] == 'data_quality'
        assert result['analysis']['should_retry'] is False
        assert result['analysis']['manual_intervention_required'] is True
    
    def test_should_rerun_pipeline_logic(self):
        """Test pipeline rerun decision logic"""
        # Test case: should retry
        analysis_result = {
            "success": True,
            "analysis": {
                "error_type": "transient",
                "should_retry": True,
                "confidence_score": 85
            }
        }
        
        should_retry, reason = should_rerun_pipeline(analysis_result, "TestPipeline")
        assert should_retry is True
        assert "transient" in reason.lower()
        
        # Test case: should not retry
        analysis_result = {
            "success": True,
            "analysis": {
                "error_type": "data_quality",
                "should_retry": False,
                "confidence_score": 90
            }
        }
        
        should_retry, reason = should_rerun_pipeline(analysis_result, "TestPipeline")
        assert should_retry is False
        assert "manual intervention" in reason.lower()

class TestADFClient:
    """Test ADF client functionality"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = ADFClient()
    
    def test_mock_data_generation(self):
        """Test mock data is generated properly"""
        mock_response = self.client._get_mock_data("/pipelineruns", "GET")
        
        assert 'value' in mock_response
        assert len(mock_response['value']) > 0
        
        # Check first run has required fields
        first_run = mock_response['value'][0]
        required_fields = ['runId', 'pipelineName', 'status', 'runStart']
        for field in required_fields:
            assert field in first_run
    
    def test_get_pipeline_runs(self):
        """Test getting pipeline runs"""
        runs = self.client.get_pipeline_runs(hours_back=1)
        
        assert isinstance(runs, list)
        if runs:
            assert 'runId' in runs[0]
            assert 'pipelineName' in runs[0]
            assert 'status' in runs[0]

class TestMockDataGenerator:
    """Test mock data generator"""
    
    def setup_method(self):
        """Setup test generator"""
        self.generator = MockDataGenerator()
    
    def test_generate_pipeline_runs(self):
        """Test pipeline run generation"""
        runs = self.generator.generate_pipeline_runs(count=5, failed_percentage=0.5)
        
        assert len(runs) == 5
        
        # Check run structure
        for run in runs:
            assert 'runId' in run
            assert 'pipelineName' in run
            assert 'status' in run
            assert 'runStart' in run
            assert 'runEnd' in run
            
        # Check some runs are failed
        failed_runs = [r for r in runs if r['status'] == 'Failed']
        assert len(failed_runs) > 0
    
    def test_generate_genai_responses(self):
        """Test GenAI response generation"""
        responses = self.generator.generate_mock_genai_responses()
        
        assert 'transient_network' in responses
        assert 'data_quality_schema' in responses
        assert 'configuration_access' in responses
        
        # Check response structure
        for response in responses.values():
            assert 'error_type' in response
            assert 'should_retry' in response
            assert 'confidence_score' in response
            assert 'analysis_summary' in response

class TestIntegration:
    """Integration tests"""
    
    def setup_method(self):
        """Setup integration test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.analyzer = GenAIAnalyzer()
    
    def teardown_method(self):
        """Cleanup"""
        os.unlink(self.temp_db.name)
    
    def test_full_pipeline_processing(self):
        """Test full pipeline from failure detection to action logging"""
        # 1. Create mock failed pipeline run
        pipeline_run = PipelineRun(
            run_id="integration-test-001",
            pipeline_name="IntegrationTestPipeline",
            status="Failed",
            start_time=datetime.now() - timedelta(minutes=10),
            end_time=datetime.now() - timedelta(minutes=5),
            error_message="Connection timeout to source database",
            factory_name="TestFactory"
        )
        
        # 2. Store in database
        success = self.db_manager.insert_pipeline_run(pipeline_run)
        assert success
        
        # 3. Analyze with GenAI (mock)
        analysis_result = self.analyzer.analyze_failure_with_genai(
            pipeline_run.pipeline_name,
            pipeline_run.error_message,
            pipeline_run.run_id
        )
        
        assert analysis_result['success'] is True
        assert 'analysis' in analysis_result
        
        # 4. Make rerun decision
        should_retry, reason = should_rerun_pipeline(analysis_result, pipeline_run.pipeline_name)
        
        # 5. Log decision
        action_id = log_decision_and_action(
            pipeline_run.run_id,
            analysis_result,
            "retry" if should_retry else "manual_intervention",
            True
        )
        
        assert action_id is not None
        
        # 6. Verify logged action
        retry_history = self.db_manager.get_retry_history(pipeline_run.pipeline_name, hours=1)
        assert len(retry_history) > 0
        assert retry_history[0]['run_id'] == pipeline_run.run_id

def run_tests():
    """Run all tests"""
    print("🧪 Running ADF Monitoring System Tests")
    print("=====================================")
    
    # Create test scenarios
    test_scenarios = create_test_scenario()
    print(f"✅ Created {len(test_scenarios)} test scenarios")
    
    # Run database tests
    print("\n🗄️  Testing Database Manager...")
    db_test = TestDatabaseManager()
    db_test.setup_method()
    try:
        db_test.test_database_initialization()
        db_test.test_insert_pipeline_run()
        db_test.test_get_dashboard_stats()
        print("✅ Database tests passed")
    finally:
        db_test.teardown_method()
    
    # Run GenAI analyzer tests
    print("\n🤖 Testing GenAI Analyzer...")
    genai_test = TestGenAIAnalyzer()
    genai_test.setup_method()
    genai_test.test_mock_analysis_transient_error()
    genai_test.test_mock_analysis_data_quality_error()
    genai_test.test_should_rerun_pipeline_logic()
    print("✅ GenAI analyzer tests passed")
    
    # Run ADF client tests
    print("\n📡 Testing ADF Client...")
    adf_test = TestADFClient()
    adf_test.setup_method()
    adf_test.test_mock_data_generation()
    adf_test.test_get_pipeline_runs()
    print("✅ ADF client tests passed")
    
    # Run mock data generator tests
    print("\n🎭 Testing Mock Data Generator...")
    mock_test = TestMockDataGenerator()
    mock_test.setup_method()
    mock_test.test_generate_pipeline_runs()
    mock_test.test_generate_genai_responses()
    print("✅ Mock data generator tests passed")
    
    # Run integration tests
    print("\n🔄 Testing Integration...")
    integration_test = TestIntegration()
    integration_test.setup_method()
    try:
        integration_test.test_full_pipeline_processing()
        print("✅ Integration tests passed")
    finally:
        integration_test.teardown_method()
    
    print("\n🎉 All tests passed successfully!")
    return True

if __name__ == "__main__":
    run_tests()
