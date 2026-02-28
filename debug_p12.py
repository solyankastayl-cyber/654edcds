#!/usr/bin/env python3
"""
Debug P12 Response Data
Get full response data to understand the calculation issue
"""

import requests
import json

def debug_endpoints():
    base_url = "https://spx-bitcoin-module-1.preview.emergentagent.com"
    
    print("=" * 70)
    print("  P12 RESPONSE DATA DEBUG")
    print("=" * 70)
    
    # Get engine baseline
    print("🔍 Getting Engine Global Baseline...")
    try:
        response = requests.get(f"{base_url}/api/engine/global", timeout=30)
        baseline_data = response.json()
        print("✅ Baseline Response OK")
        print(f"   SPX: {baseline_data.get('allocations', {}).get('spxSize', 'N/A')}")
        print(f"   BTC: {baseline_data.get('allocations', {}).get('btcSize', 'N/A')}")
        print(f"   Cash: {baseline_data.get('allocations', {}).get('cashSize', 'N/A')}")
    except Exception as e:
        print(f"❌ Baseline Error: {e}")
        return
    
    print()
    
    # Get engine with brain+optimizer
    print("🔍 Getting Engine Global with Brain+Optimizer...")
    try:
        response = requests.get(f"{base_url}/api/engine/global?brain=1&optimizer=1", timeout=30)
        brain_data = response.json()
        print("✅ Brain+Optimizer Response OK")
        
        # Extract allocations
        allocations = brain_data.get('allocations', {})
        print(f"   SPX: {allocations.get('spxSize', 'N/A')}")
        print(f"   BTC: {allocations.get('btcSize', 'N/A')}")
        print(f"   Cash: {allocations.get('cashSize', 'N/A')}")
        
        # Extract brain section
        brain_section = brain_data.get('brain', {})
        
        # Check overrideIntensity
        override_intensity = brain_section.get('overrideIntensity', {})
        if override_intensity:
            print(f"\n   Override Intensity:")
            print(f"     Brain: {override_intensity.get('brain', 'N/A')}")
            print(f"     MetaRiskScale: {override_intensity.get('metaRiskScale', 'N/A')}")
            print(f"     Optimizer: {override_intensity.get('optimizer', 'N/A')}")
            print(f"     Total: {override_intensity.get('total', 'N/A')}")
            print(f"     Cap: {override_intensity.get('cap', 'N/A')}")
            print(f"     WithinCap: {override_intensity.get('withinCap', 'N/A')}")
        
        # Check bridge steps
        bridge_steps = brain_section.get('bridgeSteps', [])
        if bridge_steps:
            print(f"\n   Bridge Steps ({len(bridge_steps)} steps):")
            for step in bridge_steps:
                step_name = step.get('step', 'unknown')
                spx_val = step.get('spx', 'N/A')
                btc_val = step.get('btc', 'N/A')
                print(f"     {step_name}: SPX={spx_val}, BTC={btc_val}")
        
    except Exception as e:
        print(f"❌ Brain+Optimizer Error: {e}")
        return
    
    print()
    
    # Calculate actual deltas
    print("🔍 Manual Delta Calculation:")
    try:
        base_spx = baseline_data['allocations']['spxSize']
        final_spx = brain_data['allocations']['spxSize']
        base_btc = baseline_data['allocations']['btcSize']
        final_btc = brain_data['allocations']['btcSize']
        
        spx_delta = abs(final_spx - base_spx)
        btc_delta = abs(final_btc - base_btc)
        max_delta = max(spx_delta, btc_delta)
        
        print(f"   Base → Final SPX: {base_spx:.4f} → {final_spx:.4f} (Δ = {spx_delta:.4f})")
        print(f"   Base → Final BTC: {base_btc:.4f} → {final_btc:.4f} (Δ = {btc_delta:.4f})")
        print(f"   Max Delta: {max_delta:.4f}")
        
        reported_total = override_intensity.get('total', 0)
        print(f"   Reported Total: {reported_total:.4f}")
        
        if abs(max_delta - reported_total) > 0.001:
            print(f"   ❌ MISMATCH: Expected {max_delta:.4f}, got {reported_total:.4f}")
        else:
            print(f"   ✅ MATCH: Calculation is correct")
            
    except Exception as e:
        print(f"❌ Calculation Error: {e}")

if __name__ == "__main__":
    debug_endpoints()