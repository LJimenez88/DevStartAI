const mongoose = require("mongoose");

let isConnected = false;

async function connectMongo() {
  if (isConnected) return;

  // Full URI already includes DB name and options
  /*URI and DBname information has to be in env file.
  This was left here as a fall back so you will need to update this on your end*/
  const uri = process.env.MONGO_URI || "mongodb://localhost:27017/app_db";

  console.log("[mongo] connecting to", uri);

  try {
    await mongoose.connect(uri);
    isConnected = true;
    console.log("[mongo] connected");
  } catch (err) {
    console.error("[mongo] connection error:", err);
    throw err; // route will send 500
  }
}

// used by /health-db or any health check
async function checkConnection() {
  await connectMongo();
}

module.exports = {
  connectMongo,
  checkConnection,
};
