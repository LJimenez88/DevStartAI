# MongoDB integration (Express)

This folder adds MongoDB support using **Mongoose**.

Generated routes:

- `GET /mongo/items`
- `POST /mongo/items`

Make sure your `.env` contains:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=app_db
