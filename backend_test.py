#!/usr/bin/env python3
"""
Fractal Multi-Asset Platform - Backend API Testing
Tests: Health, Brain v2, Stress Simulation, Cross-Asset, Engine Global
"""

import requests
import json
import sys
from datetime import datetime
import time

class FractalAPITester:
    def __init__(self, base_url="https://spx-bitcoin-module-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name, success, status_code, response_data, error=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": test_name,
            "success": success,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        # Add response summary for successful tests
        if success and response_data:
            if isinstance(response_data, dict):
                if 'ok' in response_data:
                    result['response_summary'] = {'ok': response_data['ok']}
                elif 'status' in response_data:
                    result['response_summary'] = {'status': response_data['status']}
                else:
                    # Get first few keys for summary
                    keys = list(response_data.keys())[:3]
                    result['response_summary'] = {k: str(response_data[k])[:100] for k in keys}
        
        self.results.append(result)
        
        # Print result
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name} (HTTP {status_code})")
        if error:
            print(f"    Error: {error}")
        elif success and 'response_summary' in result:
            print(f"    Response: {result['response_summary']}")
        print()

    def test_endpoint(self, name, method, endpoint, expected_status=200, data=None):
        """Test a single API endpoint"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            self.log_result(name, success, response.status_code, response_data)
            return success, response_data

        except requests.exceptions.Timeout:
            self.log_result(name, False, 0, None, "Request timeout (30s)")
            return False, None
        except requests.exceptions.ConnectionError:
            self.log_result(name, False, 0, None, "Connection error")
            return False, None
        except Exception as e:
            self.log_result(name, False, 0, None, str(e))
            return False, None

    def run_all_tests(self):
        """Run comprehensive test suite for P12 Adaptive features"""
        print("=" * 70)
        print("  FRACTAL P12 ADAPTIVE TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()

        # Test 1: Health endpoint
        print("🔍 Testing Core Health...")
        self.test_endpoint("Health Check", "GET", "/api/health")

        # Test 2: P12 Adaptive Schema
        print("🔍 Testing P12 Adaptive Schema...")
        self.test_endpoint("P12 Adaptive Schema", "GET", "/api/brain/v2/adaptive/schema")

        # Test 3: P12 Adaptive Params for DXY
        print("🔍 Testing P12 Adaptive Params for DXY...")
        self.test_endpoint("P12 Adaptive Params DXY", "GET", "/api/brain/v2/adaptive/params?asset=dxy")

        # Test 4: Engine Global with Brain + Optimizer + overrideIntensity breakdown + adaptive section
        print("🔍 Testing Engine Global with Brain + Optimizer...")
        self.test_endpoint("Engine Global Brain+Optimizer", "GET", "/api/engine/global?brain=1&optimizer=1")

        # Test 5: Brain Compare with optimizerDeltaAbs
        print("🔍 Testing Brain Compare with optimizerDeltaAbs...")
        self.test_endpoint("Brain Compare", "GET", "/api/brain/v2/compare")

        # Test 6: Additional P12 endpoints
        print("🔍 Testing Additional P12 Endpoints...")
        self.test_endpoint("Adaptive History DXY", "GET", "/api/brain/v2/adaptive/history?asset=dxy&limit=5")
        
        # Test 7: Engine Global without Brain (baseline)
        print("🔍 Testing Engine Global Baseline...")
        self.test_endpoint("Engine Global Baseline", "GET", "/api/engine/global")

        # Test 8: Brain v2 Status
        print("🔍 Testing Brain v2 Status...")
        self.test_endpoint("Brain v2 Status", "GET", "/api/brain/v2/status")

        # Test 9: Cross-Asset Regime (for context)
        print("🔍 Testing Cross-Asset Regime...")
        self.test_endpoint("Cross-Asset Regime", "GET", "/api/brain/v2/cross-asset")

        # Print Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        print()

        # Show failed tests
        failed_tests = [r for r in self.results if not r['success']]
        if failed_tests:
            print("❌ FAILED TESTS:")
            for test in failed_tests:
                error_msg = test['error'] or f"HTTP {test['status_code']}"
                print(f"  - {test['test']}: {error_msg}")
            print()

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/app/test_reports/backend_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'tests_run': self.tests_run,
                    'tests_passed': self.tests_passed,
                    'success_rate': (self.tests_passed/self.tests_run*100) if self.tests_run > 0 else 0,
                    'timestamp': datetime.now().isoformat(),
                    'backend_url': self.base_url
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved: {results_file}")
        return self.tests_passed == self.tests_run

def main():
    tester = FractalAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())