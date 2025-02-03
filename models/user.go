package models

import "github.com/Stat1c-Null/Cookly.io/db"

type User struct {
	ID       int
	Username string
	Password string
}

func CreateUser(username, password string) error {
	_, err := db.DB.Exec("INSERT INTO users (username, password) VALUES (?, ?)", username, password)
	return err
}

func GetUserByUsername(username string) (*User, error) {
	var user User
	err := db.DB.QueryRow("SELECT id, username, password FROM users WHERE username = ?", username).Scan(&user.ID, &user.Username, &user.Password)
	if err != nil {
		return nil, err
	}
	return &user, nil
}
