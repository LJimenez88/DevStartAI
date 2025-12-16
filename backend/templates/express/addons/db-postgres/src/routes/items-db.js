const express = require("express");
const router = express.Router();
const db = require("../db");

// GET /items  -> list all items
router.get("/", async (_req, res, next) => {
  try {
    const result = await db.query(
      "SELECT id, name, description FROM items ORDER BY id ASC"
    );
    res.json(result.rows);
  } catch (err) {
    next(err);
  }
});

// POST /items -> create item
router.post("/", async (req, res, next) => {
  const { name, description } = req.body || {};

  if (!name) {
    return res.status(400).json({ detail: "name is required" });
  }

  try {
    const result = await db.query(
      "INSERT INTO items (name, description) VALUES ($1, $2) RETURNING id, name, description",
      [name, description || null]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    next(err);
  }
});

module.exports = router;