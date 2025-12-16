const express = require("express");
const router = express.Router();

// Fake in-memory "database"
const items = [];

/**
 * GET /items
 * Returns all items from the in-memory store.
 */
router.get("/", (_req, res) => {
  res.json(items);
});

/**
 * POST /items
 * Creates a new item in the in-memory store.
 */
router.post("/", (req, res) => {
  const { name, description } = req.body || {};
  if (!name) {
    return res.status(400).json({ detail: "name is required" });
  }

  const newItem = {
    id: items.length + 1,
    name,
    description: description ?? null,
  };

  items.push(newItem);
  res.status(201).json(newItem);
});

module.exports = router;
