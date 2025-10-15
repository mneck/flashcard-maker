## Flashcards

A tiny project to turn a master vocabulary spreadsheet into a CSV and (optionally) load it into PostgreSQL. The repo includes a simple converter script and a database schema dump you can apply to a database.

### Files
- `arabic-vocabulary-master-list.xlsx`: Source spreadsheet with the vocabulary.
- `flashcard-maker.py`: Converts the spreadsheet to `output.csv` using pandas.
- `output.csv`: Generated CSV (created by the script).
- `schema.sql`: PostgreSQL schema dump containing `public.languages`, `public.terms`, and `public.vocab_raw`.

### Prerequisites
- Python 3.10+
- PostgreSQL installed and accessible via `psql`

Python packages:
```bash
pip install pandas openpyxl
```

### Generate CSV from the spreadsheet
```bash
python flashcard-maker.py
```
This reads `arabic-vocabulary-master-list.xlsx` and writes `output.csv` (and prints the first few rows).

### Create the PostgreSQL schema
1) Create a database (if you don’t already have one):
```bash
createdb flashcards
```

2) Apply the schema dump:
```bash
psql -d flashcards -f schema.sql
```

This creates the following tables:
- `public.languages`
- `public.terms`
- `public.vocab_raw` (staging table that mirrors the CSV layout)

### Import the CSV into the staging table
After generating `output.csv`, load it into `public.vocab_raw`:
```bash
psql -d flashcards -c "\\copy public.vocab_raw FROM 'output.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')"
```

Verify the load:
```bash
psql -d flashcards -c "SELECT COUNT(*) FROM public.vocab_raw;"
```

### Notes
- The CSV columns map to `public.vocab_raw` columns: `english`, `target_script`, `transliteration`, `sample_sentence_target`, `sample_sentence_explained`, `notes`, `learned`, `correct_counter`.
- The dump in `schema.sql` is suitable for direct application with `psql`; it uses sequences and defaults as exported.
- You can later transform rows from `public.vocab_raw` into `public.terms` according to your own rules.

### Git
```bash
git add README.md
git commit -m "Add basic README with setup and usage"
```


