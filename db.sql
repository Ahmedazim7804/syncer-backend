CREATE TABLE IF NOT EXISTS "RefreshTokens" (
	"role"	TEXT,
	"refresh_token"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("refresh_token")
);
