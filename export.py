import pandas as pd
from db import ApplicationDatabase
from io import BytesIO

def export_to_excel(output_file="applications_export.xlsx"):
    # Export all applications from the database to an Excel file
    db = ApplicationDatabase()

    applications = db.get_all_applications()

    df = pd.DataFrame(applications)

    column_order = ['company', 'status', 'applied_date', 'updated_date', 'summary']
    df = df[column_order]

    df.to_excel(output_file, index=False, sheet_name='Applications')
    print(f"Successfully exported {len(applications)} applications to {output_file}")

def get_excel_file():
    """
    Generate Excel file in memory and return bytes for API response
    Returns:
        bytes: Excel file content as bytes
    """
    db = ApplicationDatabase()
    applications = db.get_all_applications()

    df = pd.DataFrame(applications)
    column_order = ['company', 'status', 'applied_date', 'updated_date', 'summary']
    df = df[column_order]

    # Create a bytes buffer
    excel_buffer = BytesIO()

    # Write DataFrame to Excel bytes buffer
    df.to_excel(excel_buffer, index=False, sheet_name='Applications')

    # Get the bytes value
    excel_buffer.seek(0)
    excel_bytes = excel_buffer.getvalue()

    return excel_bytes

if __name__ == "__main__":
    export_to_excel()
