import pandas as pd
from db import ApplicationDatabase

def export_to_excel(output_file="applications_export.xlsx"):
    # Export all applications from the database to an Excel file
    db = ApplicationDatabase()

    applications = db.get_all_applications()

    df = pd.DataFrame(applications)

    column_order = ['company', 'status', 'applied_date', 'updated_date', 'summary']
    df = df[column_order]

    df.to_excel(output_file, index=False, sheet_name='Applications')
    print(f"Successfully exported {len(applications)} applications to {output_file}")

if __name__ == "__main__":
    export_to_excel()
