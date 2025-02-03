package db

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/mattn/go-sqlite3"
)

var DB *sql.DB

func InitDB() {
	var err error
	DB, err = sql.Open("sqlite3", "./cookly.db")
	if err != nil {
		log.Fatal(err)
	}

	// Create users table
	_, err = DB.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT UNIQUE NOT NULL,
			password TEXT NOT NULL
		);
	`)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("Database initialized")
}
