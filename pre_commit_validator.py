#!/usr/bin/env python3
"""
PRE-COMMIT VALIDATOR - Run automatically before git commit
"""

import subprocess
import sys
from pathlib import Path

def run_validation():
    """Run all validation checks"""
    
    print("=" * 70)
    print("PRE-COMMIT VALIDATION")
    print("=" * 70)
    
    checks_passed = 0
    checks_failed = 0
    
    # Check 1: Syntax
    print("\n1️⃣  Checking Python syntax...")
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "app.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ Syntax OK")
        checks_passed += 1
    else:
        print(f"   ❌ Syntax error: {result.stderr}")
        checks_failed += 1
    
    # Check 2: Code Analysis
    print("\n2️⃣  Running code analysis...")
    result = subprocess.run(
        [sys.executable, "code_analyzer.py", "app.py"],
        capture_output=True,
        text=True
    )
    
    if "NO ISSUES" in result.stdout:
        print("   ✅ No duplicates or issues found")
        checks_passed += 1
    else:
        print("   ⚠️  Some issues detected")
        print(result.stdout[:500])
        checks_failed += 1
    
    # Check 3: Validation
    print("\n3️⃣  Running code validator...")
    result = subprocess.run(
        [sys.executable, "code_validator.py", "app.py"],
        capture_output=True,
        text=True
    )
    
    if "VALIDATION PASSED" in result.stdout:
        print("   ✅ Validation passed")
        checks_passed += 1
    else:
        print("   ⚠️  Some validation warnings")
        checks_failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Checks Passed: {checks_passed}/3")
    print(f"Checks Failed: {checks_failed}/3")
    print("=" * 70)
    
    if checks_failed == 0:
        print("✅ All checks passed! Safe to commit.")
        return True
    else:
        print("⚠️  Some checks failed. Review issues above.")
        return False


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
