const express = require("express");
const router = express.Router();

const { connectMongo } = require("../db");
const Item = require("../models/item");

/**
 * GET /mongo/items
 * List all items from MongoDB.
 */
router.get("/", async (_req, res) => {
  try {
    await connectMongo();
    const items = await Item.find().lean();
    res.json(items);
  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Failed to list Mongo items" });
  }
});

/**
 * POST /mongo/items
 * Create a new item in MongoDB.
 */
router.post("/", async (req, res) => {
  const { name, description } = req.body || {};

  if (!name) {
    return res.status(400).json({ detail: "name is required" });
  }

  try {
    await connectMongo();
    const item = await Item.create({ name, description });
    res.status(201).json(item);
  } catch (err) {
    console.error(err);
    res.status(500).json({ detail: "Failed to create Mongo item" });
  }
});

module.exports = router;
