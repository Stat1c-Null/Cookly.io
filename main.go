package main

import (
	"embed"
	"fmt"
	"log"
	"net/http"

	"github.com/Stat1c-Null/Cookly.io/db"
	//"github.com/Stat1c-Null/Cookly.io/gem"
	"github.com/Stat1c-Null/Cookly.io/handlers"
	"github.com/Stat1c-Null/Cookly.io/templates"

	"github.com/gorilla/mux"
)

//go:embed static
var staticFiles embed.FS

func main() {
	// Initialize database
	db.InitDB()

	// Initialize templates
	templates.Init()

	/*
		recipe, err := gem.GetRecipe([]string{"bread","peanut butter","grape jelly"})
		if err != nil {
			panic(err)
		}
		fmt.Println(recipe)
	*/

	// Create a new router.
	r := mux.NewRouter()

	// Public routes.
	r.HandleFunc("/", handlers.HomeHandler)
	r.HandleFunc("/login", handlers.LoginHandler)
	r.HandleFunc("/register", handlers.RegisterHandler)

	// Serve static files from the embedded "static" folder.
	// Requests to "/static/..." will be served from the embedded files.
	r.PathPrefix("/static/").Handler(http.FileServer(http.FS(staticFiles)))

	// Protected routes: create a subrouter and attach the AuthMiddleware.
	authRouter := r.NewRoute().Subrouter()
	authRouter.Use(handlers.AuthMiddleware)
	authRouter.HandleFunc("/logout", handlers.LogoutHandler)
	authRouter.HandleFunc("/chef", handlers.ChefHandler)

	fmt.Println("Server running on :8080")
	log.Fatal(http.ListenAndServe(":8080", r))
}
