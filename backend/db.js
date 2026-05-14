const fs = require("fs");
const path = require("path");
const bcrypt = require("bcrypt");

const DB_PATH = path.join(__dirname, "database.json");

// Initialize database file if it doesn't exist
function initDB() {
  if (!fs.existsSync(DB_PATH)) {
    const initialData = {
      users: [],
      nextId: 1
    };
    fs.writeFileSync(DB_PATH, JSON.stringify(initialData, null, 2));
  }
}

// Read entire database
function readDB() {
  initDB();
  const data = fs.readFileSync(DB_PATH, "utf8");
  return JSON.parse(data);
}

// Write entire database
function writeDB(data) {
  fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2));
}

// Find user by email
function findUserByEmail(email) {
  const db = readDB();
  return db.users.find(user => user.email === email);
}

// Find user by id
function findUserById(id) {
  const db = readDB();
  return db.users.find(user => user.id === id);
}

// Create new user
async function createUser({ name, email, password }) {
  const db = readDB();
  const existing = db.users.find(u => u.email === email);
  if (existing) throw new Error("Email already exists");
  
  const hashedPassword = await bcrypt.hash(password, 10);
  const newUser = {
    id: db.nextId,
    name,
    email,
    password: hashedPassword,
    bookmarks: []
  };
  db.users.push(newUser);
  db.nextId++;
  writeDB(db);
  return newUser;
}

// Add bookmark to user
function addBookmark(userId, bookmark) {
  const db = readDB();
  const user = db.users.find(u => u.id === userId);
  if (!user) throw new Error("User not found");
  user.bookmarks.push(bookmark);
  writeDB(db);
  return user.bookmarks;
}

// Get user bookmarks
function getUserBookmarks(userId) {
  const user = findUserById(userId);
  return user ? user.bookmarks : [];
}

// Remove bookmark by index
function removeBookmark(userId, index) {
  const db = readDB();
  const user = db.users.find(u => u.id === userId);
  if (!user) throw new Error("User not found");
  if (index < 0 || index >= user.bookmarks.length) throw new Error("Invalid index");
  user.bookmarks.splice(index, 1);
  writeDB(db);
  return user.bookmarks;
}

module.exports = {
  findUserByEmail,
  findUserById,
  createUser,
  addBookmark,
  getUserBookmarks,
  removeBookmark
};