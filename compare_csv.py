#!/usr/bin/env python3
"""
CSV Comparison Tool
Compares CSV results between different folders/submissions or specific CSV files.

Features:
    - Compare two specific CSV files
    - Compare two specific folders
    - Compare one folder against all others in the parent directory
    - Shows detailed line-by-line differences
    - Displays summary with difference counts

Usage:
    # Compare two specific CSV files
    python compare_csv.py my_results/1.csv other_results/1.csv
    
    # Compare two specific folders
    python compare_csv.py my_results other_results
    
    # Compare your folder against all others
    python compare_csv.py my_results --all
    
Repository: https://github.com/yourname/repo
For more info, see README.md

"""

import sys
import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from io import StringIO


class OutputCapture:
    """Captures console output to both print and save to file."""
    
    def __init__(self, enable_save=True):
        self.enable_save = enable_save
        self.buffer = StringIO()
        self.original_print = print
    
    def write(self, text=""):
        """Write text to both console and buffer."""
        self.original_print(text)
        self.buffer.write(text + "\n")
    
    def get_output(self):
        """Get captured output."""
        return self.buffer.getvalue()
    
    def save_to_file(self, filename):
        """Save captured output to a file."""
        if not self.enable_save:
            return
        content = self.get_output()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        self.original_print(f"\n💾 Results saved to: {filename}")


def format_folder_names(folder1, folder2):
    """Format folder names for filename."""
    name1 = Path(folder1).name
    name2 = Path(folder2).name
    return f"{name1}_{name2}.txt"


def compare_csv_files(file1_path, file2_path, verbose=True):
    """
    Compare two CSV files and return differences.
    
    Args:
        file1_path: Path to first CSV file
        file2_path: Path to second CSV file
        verbose: If False, only return difference count
    
    Returns:
        List of differences and total count
    """
    
    # Check if files exist
    if not Path(file1_path).exists():
        return None, f"❌ Error: File '{file1_path}' not found."
    
    if not Path(file2_path).exists():
        return None, f"❌ Error: File '{file2_path}' not found."
    
    differences = []
    
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1, \
             open(file2_path, 'r', encoding='utf-8') as f2:
            reader1 = csv.reader(f1)
            reader2 = csv.reader(f2)
            
            for line_num, (row1, row2) in enumerate(zip(reader1, reader2), start=1):
                if row1 != row2:
                    differences.append({
                        'line': line_num,
                        'file1': row1,
                        'file2': row2
                    })
            
            # Check if one file has more rows
            remaining_file1 = list(reader1)
            remaining_file2 = list(reader2)
            if remaining_file2:
                line_num += len(remaining_file1)
            line_num = line_num if differences or (not remaining_file1 and not remaining_file2) else line_num
            
            if remaining_file1:
                for idx, row in enumerate(remaining_file1, start=line_num + 1):
                    differences.append({
                        'line': idx,
                        'file1': row,
                        'file2': []
                    })
            
            if remaining_file2:
                for idx, row in enumerate(remaining_file2, start=line_num + 1):
                    differences.append({
                        'line': idx,
                        'file1': [],
                        'file2': row
                    })
    
    except Exception as e:
        return None, f"❌ Error reading files: {e}"
    
    return differences, None


def display_comparison(file1_path, file2_path, folder1_name="Folder 1", folder2_name="Folder 2", capture=None):
    """Display comparison results between two CSV files."""
    
    if capture is None:
        capture = OutputCapture(enable_save=False)
    
    differences, error = compare_csv_files(file1_path, file2_path)
    
    if error:
        return error, 0
    
    file_name = Path(file1_path).name
    
    if not differences:
        capture.write(f"  ✅ {file_name}: Identical")
        return None, 0
    else:
        capture.write(f"  ⚠️  {file_name}: {len(differences)} difference(s)")
        capture.write(f"      {'-' * 80}")
        
        for diff in differences:
            capture.write(f"      Line {diff['line']}:")
            capture.write(f"        {folder1_name}: {diff['file1']}")
            capture.write(f"        {folder2_name}: {diff['file2']}")
        
        capture.write(f"      {'-' * 80}\n")
        return None, len(differences)


def compare_folders(folder1, folder2, capture=None):
    """Compare all CSV files in two folders."""
    
    if capture is None:
        capture = OutputCapture(enable_save=True)
    
    folder1_path = Path(folder1)
    folder2_path = Path(folder2)
    
    if not folder1_path.is_dir():
        capture.write(f"❌ Error: '{folder1}' is not a directory.")
        return
    
    if not folder2_path.is_dir():
        capture.write(f"❌ Error: '{folder2}' is not a directory.")
        return
    
    csv_files1 = sorted(folder1_path.glob("*.csv"))
    csv_files2 = sorted(folder2_path.glob("*.csv"))
    
    if not csv_files1 or not csv_files2:
        capture.write("❌ Error: No CSV files found in one or both folders.")
        return
    
    capture.write(f"\n📊 Comparing: '{folder1}' vs '{folder2}'\n")
    capture.write("=" * 100)
    
    total_differences = 0
    file_differences = {}
    
    for file1 in csv_files1:
        file2 = folder2_path / file1.name
        
        if not file2.exists():
            capture.write(f"  ⚠️  {file1.name}: Missing in '{folder2}'")
            continue
        
        error, diff_count = display_comparison(
            str(file1), 
            str(file2),
            folder1_name=folder1,
            folder2_name=folder2,
            capture=capture
        )
        
        if error:
            capture.write(f"  {error}")
        else:
            file_differences[file1.name] = diff_count
            total_differences += diff_count
    
    # Summary
    capture.write("=" * 100)
    capture.write(f"\n📈 SUMMARY:")
    capture.write(f"   Total files compared: {len(file_differences)}")
    capture.write(f"   Files with differences: {sum(1 for v in file_differences.values() if v > 0)}")
    capture.write(f"   Total line differences: {total_differences}\n")
    
    # Save to file
    output_filename = format_folder_names(folder1, folder2)
    capture.save_to_file(output_filename)


def compare_against_all(my_folder):
    """Compare my folder against all other CSV folders."""
    
    my_path = Path(my_folder)
    
    if not my_path.is_dir():
        print(f"❌ Error: '{my_folder}' is not a directory.")
        return
    
    parent_dir = my_path.parent
    
    # Find all directories with CSV files
    other_folders = []
    for item in parent_dir.iterdir():
        if item.is_dir() and item.name != my_path.name:
            if list(item.glob("*.csv")):
                other_folders.append(item)
    
    if not other_folders:
        print(f"❌ Error: No other folders with CSV files found in '{parent_dir}'")
        return
    
    # Create main capture for overall output
    main_capture = OutputCapture(enable_save=True)
    main_capture.write(f"\n📊 Comparing: '{my_folder}' against all other folders\n")
    main_capture.write("=" * 100)
    
    all_comparisons = defaultdict(lambda: {"count": 0, "folders": []})
    
    for other_folder in sorted(other_folders):
        main_capture.write(f"\n📂 vs '{other_folder.name}':")
        main_capture.write(f"   {'-' * 80}")
        
        csv_files = sorted(my_path.glob("*.csv"))
        total_diff = 0
        
        for file1 in csv_files:
            file2 = other_folder / file1.name
            
            if not file2.exists():
                main_capture.write(f"   ⚠️  {file1.name}: Not found in '{other_folder.name}'")
                continue
            
            differences, error = compare_csv_files(str(file1), str(file2))
            
            if error:
                main_capture.write(f"   {error}")
                continue
            
            if differences:
                diff_count = len(differences)
                main_capture.write(f"   ⚠️  {file1.name}: {diff_count} difference(s)")
                total_diff += diff_count
                all_comparisons[file1.name]["count"] += diff_count
            else:
                main_capture.write(f"   ✅ {file1.name}: Identical")
            
            all_comparisons[file1.name]["folders"].append(other_folder.name)
        
        main_capture.write(f"   Total differences: {total_diff}\n")
    
    # Final summary
    main_capture.write("=" * 100)
    main_capture.write(f"\n📈 FINAL SUMMARY (comparing '{my_folder}' against {len(other_folders)} folder(s)):\n")
    
    for file_name, data in sorted(all_comparisons.items()):
        if data["count"] > 0:
            main_capture.write(f"   {file_name}: {data['count']} total difference(s)")
    
    total_all = sum(d["count"] for d in all_comparisons.values())
    main_capture.write(f"\n   Total differences across all comparisons: {total_all}\n")
    
    # Save to file with format: folder_vs_all.txt
    output_filename = f"{my_path.name}_vs_all.txt"
    main_capture.save_to_file(output_filename)


def main():
    if len(sys.argv) < 2:
        print("CSV Comparison Tool - Compare your results with others")
        print("\nUsage:")
        print("  python compare_csv.py <csv_file> <csv_file>")
        print("    Compare two specific CSV files")
        print("\n  python compare_csv.py <folder> <folder>")
        print("    Compare all CSV files in two folders")
        print("\n  python compare_csv.py <folder> --all")
        print("    Compare your folder against all others (must be in same parent directory)")
        print("\nExamples:")
        print("  python compare_csv.py my_results/1.csv other_results/1.csv")
        print("  python compare_csv.py my_results other_results")
        print("  python compare_csv.py my_results --all")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        print("❌ Error: Missing comparison argument")
        print("   Use: python compare_csv.py <csv_file> <csv_file>")
        print("   Or:  python compare_csv.py <folder> <folder>")
        print("   Or:  python compare_csv.py <folder> --all")
        sys.exit(1)
    
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    
    # Check if comparing CSV files
    if arg1.endswith('.csv') and arg2.endswith('.csv'):
        capture = OutputCapture(enable_save=True)
        
        differences, error = compare_csv_files(arg1, arg2)
        
        if error:
            print(error)
            sys.exit(1)
        
        file1_name = Path(arg1).name
        file2_name = Path(arg2).name
        file1_folder = Path(arg1).parent.name
        file2_folder = Path(arg2).parent.name
        
        capture.write(f"\n📊 Comparing: '{arg1}' vs '{arg2}'\n")
        capture.write("=" * 100)
        
        if not differences:
            capture.write(f"✅ Files are identical!\n")
        else:
            capture.write(f"⚠️  Found {len(differences)} difference(s):\n")
            for diff in differences:
                capture.write(f"Line {diff['line']}:")
                capture.write(f"  {arg1}: {diff['file1']}")
                capture.write(f"  {arg2}: {diff['file2']}\n")
        
        capture.write("=" * 100)
        capture.write(f"\n📈 SUMMARY:")
        capture.write(f"   Total differences: {len(differences) if differences else 0}\n")
        
        # Save to file
        output_filename = f"{file1_folder}_{file2_folder}_{file1_name.replace('.csv', '')}.txt"
        capture.save_to_file(output_filename)
        return
    
    # Check for invalid mix of files and folders
    is_csv_arg1 = arg1.endswith('.csv')
    is_csv_arg2 = arg2.endswith('.csv')
    
    if is_csv_arg1 or is_csv_arg2:
        print("❌ Error: Cannot mix CSV files and folders")
        print("   Use two CSV files or two folders")
        sys.exit(1)
    
    # Compare folders
    if arg2 == "--all":
        compare_against_all(arg1)
    else:
        compare_folders(arg1, arg2)


if __name__ == "__main__":
    main()
