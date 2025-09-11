from app.models import SessionLocal, StandupResponse
from datetime import datetime

db = SessionLocal()
try:
    # Create a test standup response
    test_response = StandupResponse(
        developer_email='test@example.com',
        what_did_i_do='Worked on backend API development',
        what_will_i_do='Continue with database integration',
        blockers='None',
        created_at=datetime.now()
    )
    db.add(test_response)
    db.commit()
    print('Test standup response created successfully!')
except Exception as e:
    print('Error:', e)
    db.rollback()
finally:
    db.close()