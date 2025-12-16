const mysql = require("mysql2/promise");

let pool;

/**
 * Create (or reuse) a single Pool instance.
 * Reads connection info from environment variables.
 */
function getPool() {
  if (pool) return pool;

  // Fallbacks for testing (env should override)
  /*
  Variables are meant for Local use only
  Real Projects should have these variables should be provided via .env
  */
  const host = process.env.DB_HOST || "mysql"; // docker-compose service name
  const port = Number(process.env.DB_PORT || "3306");
  const database = process.env.DB_NAME || "app_db";
  const user = process.env.DB_USER || "app_user";
  const password = process.env.DB_PASSWORD || "app_password";

  pool = mysql.createPool({
    host,
    port,
    database,
    user,
    password,
    waitForConnections: true,
    connectionLimit: 10,
  });

  return pool;
}

/**
 * Simple helper to run queries.
 * mysql2 returns [rows, fields]
 */
async function query(sql, params = []) {
  const [rows] = await getPool().query(sql, params);
  return rows;
}

/**
 * Wait helper
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Create the items table, retrying until MySQL is ready.
 */
async function initDb(retries = 10, delayMs = 2000) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      console.log(`initDb attempt ${attempt}/${retries}...`);

      await query("SELECT 1");

      await query(`
        CREATE TABLE IF NOT EXISTS items (
          id INT AUTO_INCREMENT PRIMARY KEY,
          name VARCHAR(200) NOT NULL,
          description TEXT NULL
        )
      `);

      console.log("Items table is ready");
      return;
    } catch (err) {
      console.error("initDb error:", err.code || err.message);

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
  await query("SELECT 1");
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
