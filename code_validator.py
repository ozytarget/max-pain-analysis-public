#!/usr/bin/env python3
"""
INTELLIGENT CODE VALIDATOR
Pre-commit validation to prevent issues
"""

import subprocess
import sys
from pathlib import Path

class CodeValidator:
    def __init__(self, filepath: str = "app.py"):
        self.filepath = filepath
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def check_syntax(self) -> bool:
        """Check Python syntax"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                compile(f.read(), self.filepath, 'exec')
            self.passed.append("✅ Syntax check PASSED")
            return True
        except SyntaxError as e:
            self.errors.append(f"❌ SYNTAX ERROR: {e}")
            return False
    
    def check_imports(self) -> bool:
        """Check if all imports exist"""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", self.filepath],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            self.passed.append("✅ Import check PASSED")
            return True
        else:
            self.errors.append(f"❌ IMPORT ERROR: {result.stderr}")
            return False
    
    def check_line_length(self, max_length: int = 120) -> bool:
        """Check line length"""
        issues = []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if len(line.rstrip()) > max_length:
                    issues.append(f"  Line {i}: {len(line.rstrip())} chars")
        
        if issues:
            self.warnings.append(f"⚠️  Long lines detected:\n" + "\n".join(issues[:5]))
            return False
        else:
            self.passed.append("✅ Line length check PASSED")
            return True
    
    def check_duplicates(self) -> bool:
        """Check for obvious duplicates"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        functions = re.findall(r'def\s+(\w+)\s*\(', content)
        
        duplicates = [func for func in functions if functions.count(func) > 1]
        
        if duplicates:
            self.warnings.append(f"⚠️  DUPLICATE FUNCTIONS: {set(duplicates)}")
            return False
        else:
            self.passed.append("✅ Duplicate check PASSED")
            return True
    
    def check_st_stop_placement(self) -> bool:
        """Validate st.stop() placement"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        issues = []
        for i, line in enumerate(lines):
            if 'st.stop()' in line:
                # Check context
                if i < len(lines) - 1:
                    next_line = lines[i + 1]
                    if next_line.strip() and not next_line.strip().startswith('#'):
                        if not next_line[0].isspace():  # Same indentation level
                            issues.append(f"  Line {i+1}: Code after st.stop()")
        
        if issues:
            self.warnings.append(f"⚠️  st.stop() placement issues:\n" + "\n".join(issues))
            return False
        else:
            self.passed.append("✅ st.stop() placement check PASSED")
            return True
    
    def run_all_checks(self) -> bool:
        """Run all validation checks"""
        print("=" * 70)
        print("CODE VALIDATION REPORT")
        print("=" * 70)
        print(f"File: {self.filepath}\n")
        
        all_passed = True
        
        # Run checks
        all_passed &= self.check_syntax()
        all_passed &= self.check_imports()
        all_passed &= self.check_line_length()
        all_passed &= self.check_duplicates()
        all_passed &= self.check_st_stop_placement()
        
        # Report
        print("\n✅ PASSED:")
        for item in self.passed:
            print(f"  {item}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for item in self.errors:
                print(f"  {item}")
        
        print("\n" + "=" * 70)
        if all_passed and not self.errors:
            print("✅ VALIDATION PASSED - Ready for commit!")
            print("=" * 70)
            return True
        else:
            print("❌ VALIDATION FAILED - Fix issues before commit")
            print("=" * 70)
            return False


if __name__ == "__main__":
    import sys
    filepath = sys.argv[1] if len(sys.argv) > 1 else "app.py"
    
    validator = CodeValidator(filepath)
    success = validator.run_all_checks()
    
    sys.exit(0 if success else 1)
