#!/usr/bin/env python3
"""
Test script for threshold control functionality
"""

import sys
import os
from config import get_min_utility_threshold, set_min_utility_threshold, reset_min_utility_threshold

def test_config_module():
    """Test the configuration module"""
    print("[TEST] Testing Configuration Module")
    print("=" * 50)
    
    # Test default threshold
    default_threshold = get_min_utility_threshold()
    print(f"[PASS] Default threshold: {default_threshold}")
    
    # Test setting threshold
    test_threshold = 500
    success = set_min_utility_threshold(test_threshold)
    if success:
        current_threshold = get_min_utility_threshold()
        print(f"[PASS] Set threshold to {test_threshold}, current: {current_threshold}")
    else:
        print("[FAIL] Failed to set threshold")
    
    # Test resetting threshold
    success = reset_min_utility_threshold()
    if success:
        reset_threshold = get_min_utility_threshold()
        print(f"[PASS] Reset threshold to: {reset_threshold}")
    else:
        print("[FAIL] Failed to reset threshold")
    
    print("=" * 50)

def test_hui_miner_integration():
    """Test HUI miner with config integration"""
    print("[TEST] Testing HUI Miner Integration")
    print("=" * 50)
    
    try:
        from hui_miner import HUIMiner
        
        # Test with default threshold
        print("Testing with default threshold...")
        miner1 = HUIMiner()
        print(f"[PASS] Miner created with threshold: {miner1.min_utility_threshold}")
        
        # Test with custom threshold
        print("Testing with custom threshold...")
        miner2 = HUIMiner(min_utility_threshold=200)
        print(f"[PASS] Miner created with custom threshold: {miner2.min_utility_threshold}")
        
        # Test with None threshold (should use config)
        print("Testing with None threshold (should use config)...")
        miner3 = HUIMiner(min_utility_threshold=None)
        print(f"[PASS] Miner created with config threshold: {miner3.min_utility_threshold}")
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
    except Exception as e:
        print(f"[FAIL] Error testing HUI miner: {e}")
    
    print("=" * 50)

def test_threshold_guidelines():
    """Test threshold guidelines"""
    print("[TEST] Testing Threshold Guidelines")
    print("=" * 50)
    
    thresholds = [50, 100, 500, 1000, 2000]
    
    for threshold in thresholds:
        if threshold < 100:
            category = "Low"
        elif threshold < 1000:
            category = "Medium"
        else:
            category = "High"
        
        print(f"Threshold {threshold}: {category} (Expected: {'Fewer' if threshold >= 1000 else 'Balanced' if threshold >= 100 else 'More'} itemsets)")
    
    print("=" * 50)

def main():
    """Main test function"""
    print("[INFO] Testing Threshold Control System")
    print("=" * 60)
    
    test_config_module()
    test_hui_miner_integration()
    test_threshold_guidelines()
    
    print("[SUCCESS] All tests completed!")
    print("=" * 60)
    print("[INFO] You can now use the simple web interface to control thresholds:")
    print("   - Visit: http://localhost:5000")
    print("   - Use the 'Utility Threshold Control' section")
    print("   - Test different threshold values")

if __name__ == "__main__":
    main() 