#!/usr/bin/env python3
"""
P12 Fix Validation Testing
Validates specific fixes: overrideIntensity structure and optimizerDeltaAbs
"""

import requests
import json
import sys
from datetime import datetime

class P12ValidationTester:
    def __init__(self, base_url="https://spx-bitcoin-module-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_result(self, test_name, success, details, error=None):
        """Log detailed test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        self.results.append(result)
        
        # Print result
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if error:
            print(f"    Error: {error}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")
        print()

    def make_request(self, endpoint):
        """Make HTTP request and return response data"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)

    def test_engine_global_override_intensity(self):
        """Test 1: Engine Global with Brain+Optimizer overrideIntensity structure"""
        print("🔍 Testing Engine Global overrideIntensity structure...")
        
        success, data = self.make_request("/api/engine/global?brain=1&optimizer=1")
        
        if not success:
            self.log_result("Engine Global overrideIntensity", False, {}, data)
            return False

        # Validate overrideIntensity structure
        details = {}
        errors = []
        
        try:
            brain_section = data.get('brain', {})
            override_intensity = brain_section.get('overrideIntensity', {})
            
            # Check required fields
            required_fields = ['brain', 'metaRiskScale', 'optimizer', 'total']
            for field in required_fields:
                if field in override_intensity:
                    details[f"has_{field}"] = f"✓ {override_intensity[field]}"
                else:
                    details[f"missing_{field}"] = "✗ Missing"
                    errors.append(f"Missing {field}")
            
            # Check if total is calculated correctly (should be actual delta from base to final)
            if 'total' in override_intensity:
                total_value = override_intensity['total']
                brain_value = override_intensity.get('brain', 0)
                meta_value = override_intensity.get('metaRiskScale', 0)
                opt_value = override_intensity.get('optimizer', 0)
                
                details['total_value'] = total_value
                details['components_sum'] = brain_value + meta_value + opt_value
                details['total_calculation'] = "Real delta from base→final allocations (not sum of components)"
            
            # Check additional fields
            if 'cap' in override_intensity:
                details['cap'] = override_intensity['cap']
            if 'withinCap' in override_intensity:
                details['withinCap'] = override_intensity['withinCap']
                
        except Exception as e:
            errors.append(f"Structure validation error: {str(e)}")
        
        success = len(errors) == 0
        error_msg = "; ".join(errors) if errors else None
        
        self.log_result("Engine Global overrideIntensity", success, details, error_msg)
        return success

    def test_brain_compare_optimizer_delta(self):
        """Test 2: Brain Compare optimizerDeltaAbs and overrideIntensity"""
        print("🔍 Testing Brain Compare optimizerDeltaAbs structure...")
        
        success, data = self.make_request("/api/brain/v2/compare")
        
        if not success:
            self.log_result("Brain Compare optimizerDeltaAbs", False, {}, data)
            return False

        # Validate compare structure
        details = {}
        errors = []
        
        try:
            diff_section = data.get('diff', {})
            
            # Check for optimizerDeltaAbs
            if 'optimizerDeltaAbs' in diff_section:
                details['optimizerDeltaAbs'] = f"✓ {diff_section['optimizerDeltaAbs']}"
            else:
                details['optimizerDeltaAbs'] = "✗ Missing"
                errors.append("Missing optimizerDeltaAbs")
            
            # Check for optimizerDelta breakdown
            if 'optimizerDelta' in diff_section:
                optimizer_delta = diff_section['optimizerDelta']
                details['optimizerDelta_structure'] = f"✓ {list(optimizer_delta.keys())}"
            else:
                details['optimizerDelta'] = "✗ Missing"
                errors.append("Missing optimizerDelta")
            
            # Check for overrideIntensity with metaRiskScale
            if 'overrideIntensity' in diff_section:
                override_intensity = diff_section['overrideIntensity']
                required_fields = ['brain', 'metaRiskScale', 'optimizer', 'total']
                
                for field in required_fields:
                    if field in override_intensity:
                        details[f"overrideIntensity.{field}"] = f"✓ {override_intensity[field]}"
                    else:
                        details[f"overrideIntensity.{field}"] = "✗ Missing"
                        errors.append(f"Missing overrideIntensity.{field}")
            else:
                details['overrideIntensity'] = "✗ Missing"
                errors.append("Missing overrideIntensity in diff")
                
        except Exception as e:
            errors.append(f"Structure validation error: {str(e)}")
        
        success = len(errors) == 0
        error_msg = "; ".join(errors) if errors else None
        
        self.log_result("Brain Compare optimizerDeltaAbs", success, details, error_msg)
        return success

    def test_total_calculation_accuracy(self):
        """Test 3: Verify that total = real delta from base to final allocations"""
        print("🔍 Testing total calculation accuracy...")
        
        # Get engine baseline (no brain)
        success_base, data_base = self.make_request("/api/engine/global")
        if not success_base:
            self.log_result("Total calculation - baseline", False, {}, data_base)
            return False
            
        # Get engine with brain+optimizer
        success_brain, data_brain = self.make_request("/api/engine/global?brain=1&optimizer=1")
        if not success_brain:
            self.log_result("Total calculation - brain+opt", False, {}, data_brain)
            return False

        details = {}
        errors = []
        
        try:
            # Extract base allocations
            base_alloc = data_base.get('allocations', {})
            base_spx = base_alloc.get('spxSize', 0)
            base_btc = base_alloc.get('btcSize', 0)
            
            # Extract final allocations
            final_alloc = data_brain.get('allocations', {})
            final_spx = final_alloc.get('spxSize', 0)
            final_btc = final_alloc.get('btcSize', 0)
            
            # Calculate actual delta
            actual_spx_delta = abs(final_spx - base_spx)
            actual_btc_delta = abs(final_btc - base_btc)
            actual_total_delta = max(actual_spx_delta, actual_btc_delta)
            
            # Get reported total from overrideIntensity
            override_intensity = data_brain.get('brain', {}).get('overrideIntensity', {})
            reported_total = override_intensity.get('total', 0)
            
            details['base_spx'] = base_spx
            details['final_spx'] = final_spx
            details['actual_spx_delta'] = actual_spx_delta
            details['base_btc'] = base_btc
            details['final_btc'] = final_btc
            details['actual_btc_delta'] = actual_btc_delta
            details['calculated_total_delta'] = actual_total_delta
            details['reported_total'] = reported_total
            
            # Check if they match (within reasonable tolerance)
            tolerance = 0.001
            delta_match = abs(actual_total_delta - reported_total) <= tolerance
            
            if delta_match:
                details['total_calculation_check'] = f"✓ Match within tolerance ({tolerance})"
            else:
                details['total_calculation_check'] = f"✗ Mismatch > {tolerance}"
                errors.append(f"Total calculation mismatch: actual={actual_total_delta:.4f}, reported={reported_total:.4f}")
                
        except Exception as e:
            errors.append(f"Calculation validation error: {str(e)}")
        
        success = len(errors) == 0
        error_msg = "; ".join(errors) if errors else None
        
        self.log_result("Total calculation accuracy", success, details, error_msg)
        return success

    def run_all_tests(self):
        """Run P12 validation tests"""
        print("=" * 70)
        print("  P12 FIX VALIDATION TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"Test started: {datetime.now().isoformat()}")
        print()

        # Run specific P12 validation tests
        test1_result = self.test_engine_global_override_intensity()
        test2_result = self.test_brain_compare_optimizer_delta()
        test3_result = self.test_total_calculation_accuracy()

        # Print Summary
        self.print_summary()
        return test1_result and test2_result and test3_result

    def print_summary(self):
        """Print test summary"""
        print("=" * 70)
        print("  P12 VALIDATION SUMMARY")
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
                error_msg = test['error'] or "Validation failed"
                print(f"  - {test['test']}: {error_msg}")
            print()

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"/app/test_reports/p12_validation_{timestamp}.json"
        
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

def main():
    tester = P12ValidationTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())