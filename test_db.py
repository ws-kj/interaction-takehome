from datetime import datetime
from db import ApplicationDatabase

def test_db():
    db = ApplicationDatabase("test.db")
    
    # Add some test applications
    db.add_application(
        company="Example Corp",
        status="Applied",
        applied_date=datetime.now()
    )
    
    # Get stats
    stats = db.get_stats()
    print(stats)
    
    # Update status
    db.update_application(
        company="Example Corp",
        new_status="Interview Scheduled",
        update_date=datetime.now()
    )
    
    # Get all applications
    applications = db.get_all_applications()
    print(applications)

if __name__ == "__main__":
    test_db() 