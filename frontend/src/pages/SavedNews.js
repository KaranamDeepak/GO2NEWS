import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function SavedNews() {
  const [bookmarks, setBookmarks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    fetchBookmarks(token);
  }, [navigate]);

  async function fetchBookmarks(token) {
    try {
      const res = await axios.get("http://localhost:5000/bookmarks", {
        headers: { Authorization: token },
      });
      setBookmarks(res.data.bookmarks);
    } catch (err) {
      console.error(err);
    }
  }

  async function deleteBookmark(index) {
    const token = localStorage.getItem("token");
    try {
      await axios.delete(`http://localhost:5000/bookmarks/${index}`, {
        headers: { Authorization: token },
      });
      fetchBookmarks(token); // refresh
    } catch (err) {
      alert("Failed to delete");
    }
  }

  return (
    <div style={{ padding: "40px", color: "white" }}>
      <h1>Saved News</h1>
      {bookmarks.length === 0 && <p>No saved articles.</p>}
      <div className="news-grid">
        {bookmarks.map((item, idx) => (
          <div key={idx} className="card" style={{ position: "relative" }}>
            <button
              onClick={() => deleteBookmark(idx)}
              style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                background: "red",
                color: "white",
                border: "none",
                borderRadius: "20px",
                padding: "5px 10px",
                cursor: "pointer",
                zIndex: 10,
              }}
            >
              ✕
            </button>
            {item.image && (
              <img src={item.image} alt="news" style={{ width: "100%", height: "200px", objectFit: "cover" }} />
            )}
            <div className="content">
              <h2>{item.title}</h2>
              <p>{item.summary?.slice(0, 150)}...</p>
              <a href={item.url} target="_blank" rel="noreferrer">
                Read Full →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SavedNews;