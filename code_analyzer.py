#!/usr/bin/env python3
"""
INTELLIGENT CODE ANALYZER & AUTO-GENERATOR
Detects issues, prevents duplicates, validates code quality
"""

import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

class CodeAnalyzer:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.content = ""
        self.lines = []
        self.issues = []
        self.duplicates = []
        
    def load_file(self):
        """Load file content"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()
            self.lines = self.content.split('\n')
        return self
    
    def detect_duplicate_functions(self) -> List[Tuple[str, int, int]]:
        """Detect duplicate function definitions"""
        func_pattern = r'^\s*def\s+(\w+)\s*\('
        functions = defaultdict(list)
        
        for i, line in enumerate(self.lines, 1):
            match = re.match(func_pattern, line)
            if match:
                func_name = match.group(1)
                functions[func_name].append(i)
        
        duplicates = []
        for func_name, line_numbers in functions.items():
            if len(line_numbers) > 1:
                duplicates.append((func_name, line_numbers[0], line_numbers[1]))
                self.issues.append(f"⚠️  DUPLICATE FUNCTION: '{func_name}' at lines {line_numbers}")
        
        return duplicates
    
    def detect_duplicate_blocks(self) -> List[Dict]:
        """Detect duplicate code blocks"""
        block_hashes = defaultdict(list)
        current_block = []
        block_start = 0
        
        for i, line in enumerate(self.lines):
            # If line is empty or new block starts, process previous
            if not line.strip() or (line and not line[0].isspace() and current_block):
                if current_block:
                    block_text = '\n'.join(current_block)
                    block_hash = hashlib.md5(block_text.encode()).hexdigest()
                    block_hashes[block_hash].append((block_start, i, block_text[:50]))
                current_block = []
                block_start = i
            else:
                current_block.append(line)
        
        duplicates_found = []
        for block_hash, occurrences in block_hashes.items():
            if len(occurrences) > 1:
                for idx, (start, end, preview) in enumerate(occurrences):
                    if idx > 0:  # Only report second occurrence onwards
                        duplicates_found.append({
                            'lines': f"{start}-{end}",
                            'preview': preview,
                            'count': len(occurrences)
                        })
                        self.issues.append(f"🔄 DUPLICATE BLOCK: Lines {start}-{end} (appears {len(occurrences)} times)")
        
        return duplicates_found
    
    def detect_conflicting_conditions(self) -> List[str]:
        """Detect conflicting if statements"""
        conflicts = []
        auth_checks = []
        
        pattern = r'if\s+(?:st\.)?session_state\.get\(["\'](\w+)["\']'
        
        for i, line in enumerate(self.lines, 1):
            match = re.search(pattern, line)
            if match:
                key = match.group(1)
                auth_checks.append((key, i))
        
        # Check for same key checked multiple times
        key_lines = defaultdict(list)
        for key, line_num in auth_checks:
            key_lines[key].append(line_num)
        
        for key, lines in key_lines.items():
            if len(lines) > 2:  # If checked more than twice
                conflicts.append(f"⚠️  REDUNDANT CHECK: '{key}' checked at lines {lines}")
                self.issues.append(f"⚠️  REDUNDANT AUTH CHECK: '{key}' appears {len(lines)} times")
        
        return conflicts
    
    def detect_unused_imports(self) -> List[str]:
        """Detect potentially unused imports"""
        unused = []
        imports = re.findall(r'from\s+(\w+)\s+import\s+(.+)|import\s+(\w+)', self.content)
        
        # This is simplified - would need AST analysis for perfection
        return unused
    
    def check_syntax(self) -> bool:
        """Verify Python syntax"""
        try:
            compile(self.content, self.filepath, 'exec')
            return True
        except SyntaxError as e:
            self.issues.append(f"❌ SYNTAX ERROR: {e}")
            return False
    
    def validate_st_stop_placement(self) -> List[str]:
        """Ensure st.stop() is placed correctly"""
        problems = []
        stop_lines = []
        
        for i, line in enumerate(self.lines, 1):
            if 'st.stop()' in line:
                stop_lines.append(i)
                # Check if there's code after this st.stop() at same level
                if i < len(self.lines):
                    next_lines = self.lines[i:i+5]
                    for j, next_line in enumerate(next_lines):
                        if next_line.strip() and not next_line.strip().startswith('#'):
                            # Make sure it's not indented (part of conditional block)
                            if not next_line[0].isspace():
                                problems.append(f"⚠️  Code after st.stop() at line {i}")
        
        return problems
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        self.load_file()
        
        report = []
        report.append("=" * 70)
        report.append("CODE QUALITY ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"File: {self.filepath}")
        report.append(f"Lines: {len(self.lines)}")
        report.append("")
        
        # Run all checks
        syntax_ok = self.check_syntax()
        self.detect_duplicate_functions()
        self.detect_duplicate_blocks()
        self.detect_conflicting_conditions()
        self.validate_st_stop_placement()
        
        # Report results
        report.append("📋 ISSUES FOUND:")
        report.append("-" * 70)
        
        if not self.issues:
            report.append("✅ NO ISSUES DETECTED")
        else:
            for issue in self.issues:
                report.append(f"  {issue}")
        
        report.append("")
        report.append("📊 SUMMARY:")
        report.append(f"  • Total Issues: {len(self.issues)}")
        report.append(f"  • Syntax OK: {'✅ YES' if syntax_ok else '❌ NO'}")
        report.append(f"  • Duplicates: {len([i for i in self.issues if 'DUPLICATE' in i])}")
        report.append(f"  • Conflicts: {len([i for i in self.issues if 'REDUNDANT' in i])}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def print_report(self):
        """Print and save report"""
        report = self.generate_report()
        print(report)
        
        # Save to file
        report_file = self.filepath.replace('.py', '_ANALYSIS.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Report saved to: {report_file}")
        return report


class CodeAutoFixer:
    """Automatically fix common issues"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.content = ""
        
    def load_file(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()
        return self
    
    def remove_duplicate_imports(self) -> str:
        """Remove duplicate import statements"""
        lines = self.content.split('\n')
        seen = set()
        unique_lines = []
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if line not in seen:
                    unique_lines.append(line)
                    seen.add(line)
            else:
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    def fix_redundant_checks(self) -> str:
        """Remove redundant authentication checks"""
        # This would be more complex in practice
        return self.content
    
    def save_fixed(self, backup=True):
        """Save fixed code"""
        if backup:
            backup_file = self.filepath.replace('.py', '_BACKUP.py')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(self.content)
            print(f"✅ Backup created: {backup_file}")
        
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write(self.content)
        print(f"✅ Fixed file saved: {self.filepath}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "app.py"
    
    # Analyze
    analyzer = CodeAnalyzer(filepath)
    analyzer.print_report()
    
    # Auto-fix if requested
    if len(sys.argv) > 2 and sys.argv[2] == "--fix":
        print("\n🔧 Running auto-fixes...")
        fixer = CodeAutoFixer(filepath)
        fixer.load_file()
        fixer.content = fixer.remove_duplicate_imports()
        fixer.save_fixed()
        print("✅ Auto-fixes applied!")
