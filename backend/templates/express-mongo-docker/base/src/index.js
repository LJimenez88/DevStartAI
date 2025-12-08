require("dotenv").config();
const express = require("express");
const cors = require("cors");
const morgan = require("morgan");

const healthRouter = require("./routes/health");
const itemsRouter = require("./routes/items");

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

// Basic routes
app.use("/health", healthRouter);
app.use("/items", itemsRouter);

// Try to mount Mongo routes if the files exist.
// If the addon wasn't selected, this require will fail and we just ignore it.
try {
  const mongoItemsRouter = require("./routes/items-mongo");
  app.use("/mongo/items", mongoItemsRouter);
  console.log("Mongo routes mounted at /mongo/items");
} catch (err) {
  // No mongo addon installed – totally fine.
}

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