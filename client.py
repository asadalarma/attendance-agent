import pandas as pd
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# ---------------------------
# Load Excel
# ---------------------------
def load_excel(file_path: str):
    raw = pd.read_excel(file_path, header=None)

    # find row that contains "Student ID"
    header_row_index = None

    for i in range(len(raw)):
        row = raw.iloc[i].astype(str).str.lower()
        if "student id" in row.values:
            header_row_index = i
            break

    if header_row_index is None:
        raise Exception("Cannot detect header row")

    df = pd.read_excel(file_path, header=header_row_index)

    df.columns = df.columns.astype(str).str.strip()

    print("DETECTED COLUMNS:", df.columns.tolist())

    return df

# ---------------------------
# Attendance Calculation
# ---------------------------
def build_attendance_report(df: pd.DataFrame):
    df = df.dropna(subset=["Student ID"])

    report = df.groupby("Student ID").agg(
        Student_Name=("Student Name", "first"),
        Total_Sessions=("Date", "count"),
        Present_Days=("Date", "nunique"),
    ).reset_index()

    report["Attendance_%"] = (
        report["Present_Days"] / report["Total_Sessions"]
    ) * 100

    return report


# ---------------------------
# AI Agent
# ---------------------------
def attendance_agent(query: str, excel_path: str):
    df = load_excel(excel_path)
    report = build_attendance_report(df)

    data = report.to_dict(orient="records")

    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an attendance AI agent. "
                    "You analyze student attendance data and answer questions. "
                    "Be precise and use only given data."
                ),
            },
            {
                "role": "user",
                "content": f"""
User Query:
{query}

Attendance Data:
{json.dumps(data, indent=2, default=str)}
"""
            }
        ],
    )

    return response.choices[0].message.content




def june_missing_attendance(excel_path: str,total_classes: int = 13):
    df = load_excel(excel_path)
    # clean data
    df = df.dropna(subset=["Student ID"])

    # convert date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # count present per student
    present = df.groupby("Student ID")["Date"].nunique().reset_index()

    present.columns = ["Student ID", "Present_Days"]

    # missing calculation
    present["Missing_Days"] = total_classes - present["Present_Days"]

    # safety (no negative values)
    present["Missing_Days"] = present["Missing_Days"].clip(lower=0)

    return present



def june_missing_detailed_report(excel_path: str, total_classes: int = 13, output_file="june_attendance_report.xlsx"):
    df = load_excel(excel_path)
    # clean
    df = df.dropna(subset=["Student ID"])

    # convert date
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # remove duplicates
    df = df.drop_duplicates(["Student ID", "Date"])

    # filter June only
    df_june = df[df["Date"].dt.month == 6]

    # all class dates in June
    all_dates = sorted(df_june["Date"].dropna().unique())

    # day mapping
    date_map = pd.DataFrame({
        "Date": all_dates
    })
    date_map["Day"] = pd.to_datetime(date_map["Date"]).dt.day_name()

    results = []

    students = df_june["Student ID"].unique()

    for student in students:
        student_data = df_june[df_june["Student ID"] == student]

        present_dates = set(student_data["Date"])

        missing_dates = [d for d in all_dates if d not in present_dates]

        missing_days = [pd.to_datetime(d).day_name() for d in missing_dates]

        results.append({
            "Student ID": student,
            "Student Name": student_data["Student Name"].iloc[0],
            "Present Days": len(present_dates),
            "Missing Days Count": len(missing_dates),
            "Missing Dates": ", ".join([str(d.date()) for d in missing_dates]),
            "Missing Weekdays": ", ".join(missing_days)
        })

    report = pd.DataFrame(results)

    # export to excel
    report.to_excel(output_file, index=False)

    return report




def generate_class_dates(year: int, month: int, pattern: str):
    start = pd.to_datetime(f"{year}-{month:02d}-01")
    end = start + pd.offsets.MonthEnd(0)

    month_range = pd.date_range(start=start, end=end)

    if pattern.upper() == "MWF":
        valid_days = [0, 2, 4]
    elif pattern.upper() == "TTS":
        valid_days = [1, 3, 5]
    else:
        raise ValueError("Invalid pattern")

    return [d for d in month_range if d.weekday() in valid_days]

"""
def missing_attendance_auto_schedule(excel_path: str, year: int, month: int, pattern: str):
    df = load_excel(excel_path)
    df = df.dropna(subset=["Student ID"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.drop_duplicates(["Student ID", "Date"])

    class_dates = generate_class_dates(year, month, pattern)

    students = df["Student ID"].unique()

    results = []

    for student in students:
        student_df = df[df["Student ID"] == student]

        present_dates = set(student_df["Date"].dt.date)

        missing_dates = [
            d.date() for d in class_dates
            if d.date() not in present_dates
        ]

        results.append({
            "Student ID": student,
            "Student Name": student_df["Student Name"].iloc[0],
            "Present Days": len(present_dates),
            "Missing Days": len(missing_dates),
            "Missing Dates": ", ".join(str(d) for d in missing_dates)
        })

    report = pd.DataFrame(results)

    report.to_excel("attendance_report.xlsx", index=False)

    return report
"""

"""
def missing_attendance_auto_schedule(
        excel_path: str,
        year: int,
        month: int,
        pattern: str
):

    df = load_excel(excel_path)

    df = df.dropna(subset=["Student ID"])

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # remove duplicate attendance
    df = df.drop_duplicates(
        ["Student ID", "Date"]
    )


    # Generate expected classes
    class_dates = generate_class_dates(
        year,
        month,
        pattern
    )


    # only selected month
    df = df[
        (df["Date"].dt.year == year) &
        (df["Date"].dt.month == month)
    ]


    students = df[
        ["Student ID","Student Name"]
    ].drop_duplicates()


    results = []


    for _, student in students.iterrows():

        student_id = student["Student ID"]

        attendance = df[
            df["Student ID"] == student_id
        ]


        present_dates = set(
            attendance["Date"]
            .dt.date
        )


        missing_dates = []

        for class_date in class_dates:

            if class_date.date() not in present_dates:
                missing_dates.append(
                    class_date.date()
                )


        results.append({

            "Student ID": student_id,

            "Student Name": student["Student Name"],

            "Total Classes":
                len(class_dates),

            "Present Days":
                len(present_dates),

            "Missing Days":
                len(missing_dates),

            "Missing Dates":
                ", ".join(
                    str(x)
                    for x in missing_dates
                )

        })


    report = pd.DataFrame(results)


    report.to_excel(
        "attendance_report.xlsx",
        index=False
    )


    return report    
"""


def infer_batch_weekdays(df: pd.DataFrame, group_col: str = "Batch", threshold_ratio: float = 0.2):
    """
    For each batch, figure out which weekdays it actually meets on,
    based on the frequency of weekdays across ALL that batch's attendance rows.
    Returns {batch_name: [0,2,4]} style dict (0=Mon ... 6=Sun).
    """
    weekday_map = {}
    for batch, group in df.groupby(group_col):
        counts = group["Date"].dt.weekday.value_counts()
        if counts.empty:
            weekday_map[batch] = []
            continue
        threshold = counts.max() * threshold_ratio
        active_days = sorted(counts[counts >= threshold].index.tolist())
        weekday_map[batch] = active_days
    return weekday_map


def missing_attendance_auto_schedule(excel_path: str, year: int, month: int):
    df = load_excel(excel_path)
    df = df.dropna(subset=["Student ID"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    df = df.dropna(subset=["Date"])
    df = df.drop_duplicates(["Student ID", "Date"])

    # infer each batch's real meeting weekdays from its full attendance history
    batch_weekdays = infer_batch_weekdays(df, group_col="Batch")

    # restrict to the target month/year for missing-day comparison
    start = pd.Timestamp(year=year, month=month, day=1)
    end = start + pd.offsets.MonthEnd(0)
    month_range = pd.date_range(start=start, end=end)

    results = []
    for student_id, student_df in df.groupby("Student ID"):
        batch = student_df["Batch"].dropna().iloc[0] if student_df["Batch"].notna().any() else None
        active_days = batch_weekdays.get(batch, [])

        class_dates = [d for d in month_range if d.weekday() in active_days]
        class_date_set = {d.date() for d in class_dates}

        present_in_month = student_df[
            (student_df["Date"].dt.year == year) & (student_df["Date"].dt.month == month)
        ]
        present_dates = set(present_in_month["Date"].dt.date)

        missing_dates = sorted(class_date_set - present_dates)

        results.append({
            "Student ID": student_id,
            "Student Name": student_df["Student Name"].iloc[0],
            "Batch": batch,
            "Inferred Weekdays": ", ".join(
                ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][d] for d in active_days
            ),
            "Expected Classes": len(class_date_set),
            "Present Days": len(present_dates & class_date_set),
            "Missing Days": len(missing_dates),
            "Missing Dates": ", ".join(str(d) for d in missing_dates),
        })

    report = pd.DataFrame(results)
    report.to_excel("attendance_report.xlsx", index=False)
    return report