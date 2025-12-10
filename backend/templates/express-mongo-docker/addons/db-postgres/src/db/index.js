const { Pool } = require("pg");

let pool;

/**
 * Create (or reuse) a single Pool instance.
 * Reads connection info from environment variables.
 */
function getPool() {
  if (pool) return pool;

  const host = process.env.DB_HOST || "localhost";
  const port = Number(process.env.DB_PORT || "5432");
  const database = process.env.DB_NAME || "app_db";
  const user = process.env.DB_USER || "app_user";
  const password = process.env.DB_PASSWORD || "app_password";

  pool = new Pool({
    host,
    port,
    database,
    user,
    password,
  });

  return pool;
}

/**
 * Simple helper to run queries.
 */
async function query(text, params) {
  const client = await getPool().connect();
  try {
    const res = await client.query(text, params);
    return res;
  } finally {
    client.release();
  }
}

/**
 * Wait helper
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Create the items table, retrying until Postgres is ready.
 */
async function initDb(retries = 10, delayMs = 2000) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`initDb attempt ${attempt}/${retries}...`);
      await query(`
        CREATE TABLE IF NOT EXISTS items (
          id SERIAL PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT
        );
      `);
      console.log("Items table is ready");
      return;
    } catch (err) {
      console.error("initDb error:", err.code || err.message);

      // On last attempt, re-throw
      if (attempt === retries) {
        console.error("Giving up on initDb after retries");
        throw err;
      }

      console.log(`Retrying in ${delayMs} ms...`);
      await sleep(delayMs);
    }
  }
}

/**
 * Used by /health-db style endpoints.
 */
async function healthCheck() {
  await query("SELECT 1;");
}

async function checkConnection() {
  await healthCheck();
}

module.exports = {
  getPool,
  query,
  initDb,
  healthCheck,
  checkConnection,
};