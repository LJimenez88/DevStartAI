const mongoose = require("mongoose");

let isConnected = false;

async function connectMongo() {
  if (isConnected) return;

  const uri = process.env.MONGO_URI || "mongodb://localhost:27017";
  const dbName = process.env.MONGO_DB_NAME || "app_db";

  const fullUri = `${uri}/${dbName}`;

  console.log("[mongo] connecting to", fullUri);

  await mongoose.connect(fullUri);
  isConnected = true;

  console.log("[mongo] connected");
}

module.exports = {
  connectMongo,
};