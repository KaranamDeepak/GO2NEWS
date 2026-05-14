const mongoose = require("mongoose");
const bcrypt = require("bcrypt");

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  bookmarks: [
    {
      title: String,
      url: String,
      image: String,
      summary: String,
      category: String,
      state: String,
    },
  ],
});

// CORRECT pre-save hook
userSchema.pre("save", function(next) {
  const user = this;
  if (!user.isModified("password")) return next();
  
  bcrypt.genSalt(10, function(err, salt) {
    if (err) return next(err);
    bcrypt.hash(user.password, salt, function(err, hash) {
      if (err) return next(err);
      user.password = hash;
      next();
    });
  });
});

module.exports = mongoose.model("User", userSchema);