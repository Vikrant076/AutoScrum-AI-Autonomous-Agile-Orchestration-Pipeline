from app.models import SessionLocal, StandupResponse

db = SessionLocal()
try:
    responses = db.query(StandupResponse).all()
    print(f'Found {len(responses)} standup responses:')
    print('')
    for response in responses:
        print(f'ID: {response.id}')
        print(f'Developer: {response.developer_email}')
        print(f'What I did: {response.what_did_i_do}')
        print(f'What I will do: {response.what_will_i_do}')
        print(f'Blockers: {response.blockers}')
        print(f'Created: {response.created_at}')
        print('---')
finally:
    db.close()