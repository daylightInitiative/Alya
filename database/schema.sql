CREATE TABLE IF NOT EXISTS user_gifs (
  id INTEGER PRIMARY KEY NOT NULL,
  user_id INTEGER NOT NULL,
  server_id INTEGER,
  gif_url, TEXT NOT NULL,
  created_at TIMESTAMP
);
-- Scheduling the timers by least to greatest has to be the play here
-- Adding it to database so it's recoverable if a crash or outage happens
-- Precision should only be down to the minute, not needing anything greater than that
-- Later we can separate the timers into time span groups, that way polling is more efficient
-- At startup we can start our tasks and since even in memory timers at least use a db state it can be recreated
-- Cleanup will be needed especially with timers that are expired and not caught, perhaps from downtime
-- Periodic database polling for timers that have not been grouped and are still pending performance cost will be negligable
-- Deltatime can be precomputed to save time, stored in the database
CREATE TABLE IF NOT EXISTS user_timers (
  id INTEGER PRIMARY KEY NOT NULL,
  -- keyed by id
  -- expired, pending
  timer_state VARCHAR(25) NOT NULL,
  expires_at TIMESTAMP,
  created_at TIMESTAMP
);