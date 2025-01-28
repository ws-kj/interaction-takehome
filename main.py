from db import ApplicationDatabase
from export import export_to_excel

from email_processor import EmailProcessor
from email.mime import application

def main():
    # test main -- fastAPI app is in app.py
    email_processor = EmailProcessor()
    db = ApplicationDatabase()

    # Process new application emails
    updates = email_processor.process_new_updates(unread_only=False)
    for update in updates:
        db.update_application(
            update.company,
            update.status,
            update.sent_time,
            summary=update.summary
        )
    # Print some stats
    applications = db.get_all_applications()
    print("\nCurrent applications:")
    for  update in applications:
        print(f"- {update['company']}: {update['status']} (Updated {update['updated_date']}) -- Notes: {update['summary']}")

    export_to_excel()

if __name__ == '__main__':
    main()
