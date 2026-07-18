# 🎓 Student Attendance AI Agent

A Python-based attendance analysis system that reads student attendance from Excel files, automatically infers class schedules per batch, calculates missing days, and answers natural language questions via an LLM — powered by OpenRouter.

---

## ✨ Features

- 📂 **Auto-detects header row** in messy Excel files — no manual row configuration needed
- 📅 **Infers batch schedule automatically** from attendance history — no need to hardcode MWF or TTS per student
- 📊 **Per-student missing day report** — present days, missing days, missing dates, attendance %
- 💬 **Natural language Q&A** — ask any attendance question and get a plain-English answer from an LLM
- 📤 **Excel export** — full report saved to `attendance_report.xlsx`
- 🔁 **Multi-batch support** — handles any number of batches with different schedules in one file

---

## 📁 Project Structure

```
.
├── client.py              # Core logic (load, infer schedule, build report, LLM agent)
├── main.py                # CLI entry point
├── requirements.txt       # Python dependencies
├── attendance_report.xlsx # Auto-generated output report (gitignored)
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/attendance-ai-agent.git
cd attendance-ai-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get a free API key at [openrouter.ai](https://openrouter.ai).

### 4. Add your Excel file

Place your attendance `.xls` or `.xlsx` file in the project root. The file must have a row containing `Student ID` as a column header — the loader scans for it automatically regardless of how many rows are above it.

### 5. Update the file path in `main.py`

```python
file_path = "your_attendance_file.xls"   # 👈 change this
```

---

## 🚀 Run

```bash
python3 main.py
```

```
🤖 Attendance AI Agent Started
Type 'exit' to stop

Ask attendance question: █
```

---

## 💬 Example Queries

```
Ask attendance question: Who has the worst attendance this month?
Ask attendance question: List all students missing more than 5 days
Ask attendance question: What is the attendance percentage of Muhammad Asad?
Ask attendance question: Which batch has the most absences overall?
Ask attendance question: How many students have less than 70% attendance?
Ask attendance question: Show me missing dates for Areeba Asif
Ask attendance question: Which students attended every class in June?
```

---

## 📊 How Batch Schedule Inference Works

Rather than requiring you to manually tag each student or batch as `MWF` or `TTS`, the system **reads the weekday distribution of actual attendance records** for each batch and infers which days it meets.

```
Batch AI-202504E+02E attendance records
        ↓
Weekday counts:  Mon=45  Wed=41  Fri=38  Tue=2  Thu=1
        ↓
Active days (≥ 20% of peak):  Mon, Wed, Fri
        ↓
Expected class dates for June generated from Mon/Wed/Fri
        ↓
Missing dates = Expected dates − Student's present dates
```

This means the system works correctly even if you have multiple batches on different schedules in the same Excel file.

---

## 🗂️ Excel File Format

The system expects an Excel sheet with at least these columns (extra columns are ignored):

| Column       | Required | Notes                                   |
|--------------|----------|-----------------------------------------|
| Student ID   | ✅       | Used to identify unique students        |
| Student Name | ✅       | Displayed in results                    |
| Date         | ✅       | Parsed automatically (e.g. 1-Jun-2026)  |
| Batch        | ✅       | Used to infer class schedule per group  |
| Schedule     | ❌       | Not used — schedule is auto-inferred    |

> The header row can be anywhere in the sheet — the loader detects it automatically by scanning for `Student ID`.

---

## 📤 Output Report

After each run, `attendance_report.xlsx` is generated in the project root with the following columns:

| Column            | Description                                  |
|-------------------|----------------------------------------------|
| Student ID        | Unique student identifier                    |
| Student Name      | Full name                                    |
| Batch             | Batch code from the Excel file               |
| Inferred Weekdays | Schedule detected automatically (e.g. Mon, Wed, Fri) |
| Expected Classes  | Total class sessions in the selected month   |
| Present Days      | Days the student actually attended           |
| Missing Days      | Number of classes missed                     |
| Missing Dates     | Comma-separated list of missed dates         |

---

## 🧩 Tech Stack

| Component       | Tool                                              |
|-----------------|---------------------------------------------------|
| Data processing | `pandas`, `numpy`                                 |
| Excel I/O       | `openpyxl`, `xlrd`                                |
| LLM             | `meta-llama/llama-3.1-8b-instruct` via OpenRouter |
| API client      | `openai` SDK (OpenRouter-compatible)              |
| Config          | `python-dotenv`                                   |

---

## 🛠️ Troubleshooting

**`Cannot detect header row` error**
Make sure a row in your sheet contains the exact text `Student ID` (case-insensitive) in one of its cells.

**Wrong or missing students in report**
Check that the `Student ID` and `Date` columns are not empty for those rows. Rows with a blank `Student ID` are skipped automatically.

**Attendance report shows 0 present days**
The target `year` and `month` in `main.py` must match the dates in your Excel file. Double-check both values.

**OpenRouter API errors**
Verify your `.env` file contains a valid `OPENROUTER_API_KEY` and your account has remaining credits.

**Date parsing issues**
Dates like `01-Jun-2026` are handled automatically. If your file uses a different format (e.g. `2026/06/01`), open `client.py` and update the `dayfirst` parameter in:
```python
df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🙌 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.