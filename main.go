package main

import (
	"embed"
	"fmt"
	"log"
	"net/http"
	"github.com/Stat1c-Null/Cookly.io/db"
	"github.com/Stat1c-Null/Cookly.io/handlers"
	"github.com/Stat1c-Null/Cookly.io/templates"
)

//go:embed static/*
var staticFiles embed.FS

func main() {
	// Initialize database
	db.InitDB()

	// Initialize templates
	templates.Init()

	// Serve static files
	http.Handle("/static/", http.FileServer(http.FS(staticFiles)))

	// Routes
	http.HandleFunc("/", handlers.HomeHandler)
	http.HandleFunc("/login", handlers.LoginHandler)
	http.HandleFunc("/register", handlers.RegisterHandler)
	http.HandleFunc("/logout", handlers.LogoutHandler)

	fmt.Println("Server running on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
