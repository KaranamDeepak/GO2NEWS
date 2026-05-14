const express = require("express");
const jwt = require("jsonwebtoken");
const db = require("../db");

const router = express.Router();

function auth(req, res, next) {
  try {
    const token = req.headers.authorization;
    if (!token) return res.status(401).json({ message: "No token" });
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ message: "Invalid token" });
  }
}

// GET all bookmarks
router.get("/", auth, (req, res) => {
  try {
    const bookmarks = db.getUserBookmarks(req.user.id);
    res.json({ bookmarks });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST add bookmark
router.post("/", auth, (req, res) => {
  try {
    const { title, url, image, summary, category, state } = req.body;
    const bookmark = { title, url, image, summary, category, state };
    const bookmarks = db.addBookmark(req.user.id, bookmark);
    res.json({ bookmarks });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE bookmark by index
router.delete("/:index", auth, (req, res) => {
  try {
    const index = parseInt(req.params.index);
    const bookmarks = db.removeBookmark(req.user.id, index);
    res.json({ bookmarks });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;