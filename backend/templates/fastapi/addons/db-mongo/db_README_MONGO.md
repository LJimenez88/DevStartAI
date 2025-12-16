# MongoDB addon

- Connection handled in `app/db_mongo.py`
- Use `Depends(get_db)` to access MongoDB in your endpoints.
- Example collection: `db["items"]`
