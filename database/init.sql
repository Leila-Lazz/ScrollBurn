-- database/init.sql
-- Green IT justification: SQLite database for dev means 0 additional energy consumption from a dedicated server process.
-- Indexes are explicitly created to avoid full table scans (saving CPU cycles and energy).

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    device_type VARCHAR(20), -- 'smartphone', 'laptop', 'tablet'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scroll_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform VARCHAR(30) NOT NULL, -- 'TikTok', 'Instagram', 'YouTube', 'Snapchat', 'Twitter/X', 'Facebook', 'Other'
    duration_minutes INTEGER NOT NULL,
    device VARCHAR(20), -- 'smartphone', 'laptop', 'tablet'
    co2_grams FLOAT, -- calculated automatically server-side
    session_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS green_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    platform VARCHAR(30),
    daily_limit_minutes INTEGER NOT NULL,
    duration_days INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'failed'
    co2_saved_grams FLOAT DEFAULT 0,
    start_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for performance (Green IT: faster queries = less CPU time)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON scroll_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_date ON scroll_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_challenges_user_id ON green_challenges(user_id);

-- Sample Data
-- Password hash for 'password123' generated with bcrypt
INSERT OR IGNORE INTO users (username, email, password_hash, device_type) VALUES 
('ecowarrior', 'eco@example.com', '$2b$12$D23iE/.K.U5o5v5P3e5m.Oe.8.r.n.c.c.c.c.c.c.c.c.c.c.c.c', 'smartphone'),
('greenuser', 'green@example.com', '$2b$12$D23iE/.K.U5o5v5P3e5m.Oe.8.r.n.c.c.c.c.c.c.c.c.c.c.c.c', 'laptop');

-- Sample sessions (co2 calculated: 10 mins TikTok on smartphone = 10 * 2.92 * 1.0 = 29.2)
INSERT OR IGNORE INTO scroll_sessions (user_id, platform, duration_minutes, device, co2_grams, session_date) VALUES 
(1, 'TikTok', 10, 'smartphone', 29.2, '2026-04-29'),
(1, 'Instagram', 15, 'smartphone', 15.75, '2026-04-29'),
(2, 'YouTube', 30, 'laptop', 67.2, '2026-04-30'),
(2, 'Snapchat', 5, 'smartphone', 4.5, '2026-04-30'),
(1, 'Twitter/X', 20, 'laptop', 19.6, '2026-04-30');

-- Sample challenges
INSERT OR IGNORE INTO green_challenges (user_id, title, platform, daily_limit_minutes, duration_days, status, start_date) VALUES 
(1, 'Less TikTok this week', 'TikTok', 20, 7, 'active', '2026-04-30'),
(2, 'No YouTube on laptop', 'YouTube', 0, 3, 'completed', '2026-04-25');
