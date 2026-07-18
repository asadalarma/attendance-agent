"""
from client import load_excel
import pandas as pd

df = load_excel("TvBQHm.xls")
print("COLUMNS:", df.columns.tolist())
print("RAW sample of Date column(s):")
print(df.filter(like="Date").head(10))

d = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
print("Weekday distribution (dayfirst=True):")
print(d.dt.day_name().value_counts())

d2 = pd.to_datetime(df["Date"], errors="coerce")
print("Weekday distribution (default parsing):")
print(d2.dt.day_name().value_counts())
"""

from client import load_excel

df = load_excel("TvBQHm.xls")
df = df.dropna(subset=["Student ID"])

# See what Schedule/Batch values exist per student
print(df[["Student ID", "Student Name", "Batch", "Schedule"]].drop_duplicates())

print("\nUnique Schedule values:", df["Schedule"].unique())
print("Unique Batch values:", df["Batch"].unique())