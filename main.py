from client import missing_attendance_auto_schedule

if __name__ == "__main__":
    file_path = "TvBQHm.xls"  # 👈 use xlsx (recommended)

    print("\n🤖 Attendance AI Agent Started")
    print("Type 'exit' to stop\n")

    while True:
        query = input("Ask attendance question: ")

        if query.lower() == "exit":
            print("Goodbye 👋")
            break

        try:
            ##result = attendance_agent(query, file_path)

            result = missing_attendance_auto_schedule(
    file_path,
    year=2026,
    month=6,
   # pattern="MWF"   # or "TTS"
)
            print("\n--- AI RESULT ---")
            print(result)
            print("\n" + "-" * 40)

        except Exception as e:
            print("\n❌ Error:", str(e))