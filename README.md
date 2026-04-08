# CSV Comparison Tool

Compare your SQL query results against others.

## Usage

Create a folder with your name.
Place CSV files in folders with names in format: `1.csv`, `2.csv`, etc.

**Compare two specific CSV files:**
```bash
python compare_csv.py your_folder/1.csv other_folder/1.csv
```

**Compare two folders:**
```bash
python compare_csv.py your_folder other_folder
```

**Compare your folder against all others:**
```bash
python compare_csv.py your_folder --all
```

## Output

Shows line-by-line differences and summary with total difference count between files.

- ✅ Identical files
- ⚠️ Files with differences (line number and mismatched values)
- 📈 Summary with total changes
