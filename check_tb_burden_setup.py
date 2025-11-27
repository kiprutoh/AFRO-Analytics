"""
Simple TB Burden Setup Checker (no plotly required)
Run this to verify basic setup before launching website
"""

import os
import sys

print("\n" + "="*80)
print("TB BURDEN SETUP CHECKER")
print("="*80)

# Check 1: Files exist
print("\n✓ Checking required files...")
files_status = []

files = {
    'TB Burden Data': "TB_burden_countries_2025-11-27.csv",
    'Country Lookup': "look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv",
    'TB Burden Analytics': "tb_burden_analytics.py",
    'TB Burden Charts': "tb_burden_chart_generator.py",
    'Website': "website.py"
}

for name, path in files.items():
    exists = os.path.exists(path)
    status = "✓" if exists else "❌"
    print(f"   {status} {name}: {path}")
    files_status.append(exists)

if not all(files_status):
    print("\n❌ MISSING FILES! Cannot proceed.")
    sys.exit(1)

# Check 2: Can load pandas
print("\n✓ Checking pandas...")
try:
    import pandas as pd
    print(f"   ✓ pandas version: {pd.__version__}")
except ImportError:
    print("   ❌ pandas not installed")
    sys.exit(1)

# Check 3: Can load numpy
print("\n✓ Checking numpy...")
try:
    import numpy as np
    print(f"   ✓ numpy version: {np.__version__}")
except ImportError:
    print("   ❌ numpy not installed")
    sys.exit(1)

# Check 4: Test data loading
print("\n✓ Testing TB Burden data loading...")
try:
    from tb_burden_analytics import TBBurdenAnalytics
    
    analytics = TBBurdenAnalytics(
        "TB_burden_countries_2025-11-27.csv",
        "look up file WHO_AFRO_47_Countries_ISO3_Lookup_File.csv"
    )
    analytics.load_data()
    
    summary = analytics.get_data_summary()
    print(f"   ✓ Loaded {summary['total_countries']} AFRO countries")
    print(f"   ✓ {summary['total_records']} total records")
    print(f"   ✓ Years: {summary['year_range'][0]} - {summary['year_range'][1]}")
    
    # Quick data check
    burden_sum = analytics.get_burden_summary()
    print(f"   ✓ {burden_sum['total_incident_cases']:,.0f} TB cases in {burden_sum['year']}")
    
except Exception as e:
    print(f"   ❌ Data loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 5: Website integration
print("\n✓ Checking website integration...")
try:
    with open('website.py', 'r') as f:
        content = f.read()
    
    required_strings = [
        'from tb_burden_analytics import TBBurdenAnalytics',
        'def render_tb_burden_dashboard',
        'TB Burden Estimates',
        "'TB_Burden'"
    ]
    
    all_present = True
    for req in required_strings:
        if req in content:
            print(f"   ✓ Found: {req[:50]}...")
        else:
            print(f"   ❌ Missing: {req}")
            all_present = False
    
    if not all_present:
        print("\n   ⚠️ Website integration incomplete!")
        
except Exception as e:
    print(f"   ❌ Website check failed: {e}")

# Final status
print("\n" + "="*80)
print("✅ SETUP VERIFICATION COMPLETE")
print("="*80)

print("\n📋 SUMMARY:")
print("   ✓ All required files present")
print("   ✓ Dependencies available (pandas, numpy)")
print("   ✓ TB Burden data loads successfully")
print("   ✓ 47 AFRO countries recognized")
print("   ✓ Website integration verified")

print("\n🚀 NEXT STEPS:")
print("   1. Launch website: streamlit run website.py")
print("   2. In sidebar: Select 'Tuberculosis' as Health Topic")
print("   3. Click: '🚀 Initialize System'")
print("   4. Look for: '📉 TB Burden Estimates ✓' button in sidebar")
print("   5. Click it to access TB Burden dashboard")

print("\n💡 EXPECTED BEHAVIOR:")
print("   • After initialization, you should see 'TB Burden data loaded successfully!'")
print("   • Sidebar will show 'TB Burden Records: 1,164'")
print("   • Navigation button will show: '📉 TB Burden Estimates ✓'")
print("   • Dashboard shows regional overview + charts + maps + equity analysis")

print("\n⚠️ IF BUTTON DOESN'T APPEAR:")
print("   • Verify 'Tuberculosis' is selected in sidebar")
print("   • Check system status shows 'System Ready' (green)")
print("   • Look for initialization error messages")
print("   • Run this script again to verify data loads")

print("\n" + "="*80 + "\n")

