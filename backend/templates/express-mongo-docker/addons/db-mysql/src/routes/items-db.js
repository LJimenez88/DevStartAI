const express = require("express");
const db = require("../db"); // uses src/db/index.js

const router = express.Router();

// GET /db/items
router.get("/", async (_req, res) => {
  const rows = await db.query(
    "SELECT id, name, description FROM items ORDER BY id ASC"
  );
  res.json(rows);
});

// POST /db/items
router.post("/", async (req, res) => {
  const { name, description } = req.body;
  if (!name) return res.status(400).json({ error: "name required" });

  const result = await db.query(
    "INSERT INTO items (name, description) VALUES (?, ?)",
    [name, description ?? null]
  );

  const inserted = await db.query(
    "SELECT id, name, description FROM items WHERE id = ?",
    [result.insertId]
  );

  res.status(201).json(inserted[0]);
});

// GET /db/items/:id
router.get("/:id", async (req, res) => {
  const rows = await db.query(
    "SELECT id, name, description FROM items WHERE id = ?",
    [req.params.id]
  );

  if (!rows.length) return res.status(404).json({ error: "Not found" });
  res.json(rows[0]);
});

// DELETE /db/items/:id
router.delete("/:id", async (req, res) => {
  const result = await db.query("DELETE FROM items WHERE id = ?", [
    req.params.id,
  ]);

  if (!result.affectedRows) return res.status(404).json({ error: "Not found" });
  res.status(204).end();
});

module.exports = router;
