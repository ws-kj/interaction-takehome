from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from db import ApplicationDatabase
from export import export_to_excel, get_excel_file
from email_processor import EmailProcessor
from typing import List
from pydantic import BaseModel
from datetime import datetime
import io
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

email_processor = EmailProcessor()
db = ApplicationDatabase()

class Application(BaseModel):
    company: str
    status: str
    updated_date: datetime
    summary: str

@app.get("/")
async def root():
    return {"message": "Application Tracking API"}

@app.get("/applications", response_model=List[Application])
async def get_applications():
    # get all applications from the database
    try:
        applications = db.get_all_applications()
        return applications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/new")
async def process_new():
    # process new updates and propagate to DB
    try:
        updates = email_processor.process_new_updates(unread_only=True)
        processed_count = 0

        for update in updates:
            db.update_application(
                update.company,
                update.status,
                update.sent_time,
                summary=update.summary
            )
            processed_count += 1

        return {
            "message": f"Successfully processed {processed_count} email updates",
            "processed_count": processed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/all")
async def process_emails(unread_only: bool = False):
    # process all updates and propagate to DB
    try:
        updates = email_processor.process_new_updates(unread_only=False)
        processed_count = 0

        for update in updates:
            db.update_application(
                update.company,
                update.status,
                update.sent_time,
                summary=update.summary
            )
            processed_count += 1

        return {
            "message": f"Successfully processed {processed_count} email updates",
            "processed_count": processed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export")
async def export_applications():
    #export to excel
    try:
        excel_bytes = get_excel_file()
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            headers={"Content-Disposition": "attachment; filename=Applications.xlsx"},
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
