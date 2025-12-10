require("dotenv").config();
const express = require("express");
const cors = require("cors");
const morgan = require("morgan");

const healthRouter = require("./routes/health");
const itemsRouter = require("./routes/items");

const app = express();

// Try to load DB helper if a db-* addon was copied
let db = null;
try {
  db = require("./db"); // e.g. from addons/db-{name_of_db}/src/db/index.js
  console.log("DB helper loaded.");

  // Call initDb() on startup so tables are created
  if (typeof db.initDb === "function") {
    db.initDb()
      .then(() => console.log("Postgres tables initialized"))
      .catch((err) => console.error("DB init failed:", err));
  }
} catch (err) {
  console.log("No DB helper found – running without DB health.");
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

// Basic routes
app.use("/health", healthRouter);
app.use("/items", itemsRouter);

// Try to mount db routes if the files exist.
// If the addon wasn't selected, this require will fail and we just ignore it.
try {
  const dbItemsRouter = require("./routes/items-db");
  app.use("/db/items", dbItemsRouter);
  console.log("DB routes mounted at /db/items");
} catch (err) {
  console.log("No DB items routes found.");
}

// Optional DB health route
app.get("/health-db", async (_req, res) => {
  try {
    if (!db || typeof db.checkConnection !== "function") {
      return res.json({ status: "ok", db: "not-configured" });
    }

    await db.checkConnection();
    return res.json({ status: "ok", db: "connected" });
  } catch (err) {
    console.error("DB health error:", err);
    return res.status(500).json({ status: "error", error: err.message });
  }
});

// Root route
app.get("/", (_req, res) => {
  res.json({
    message: "Express API starter from DevStartAI",
  });
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`API listening on http://localhost:${PORT}`);
});
