package handlers

import (
	"fmt"
	"net/http"

	"github.com/Stat1c-Null/Cookly.io/models"
	"github.com/Stat1c-Null/Cookly.io/sessions"
	"github.com/Stat1c-Null/Cookly.io/templates"
)

func AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Check if user is authenticated
		if sessions.User(r) == "" {
			http.Redirect(w, r, "/login", http.StatusSeeOther)
			return
		}
		// Call the next middleware function or final handler
		next.ServeHTTP(w, r)
	})
}

func LoginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		username := r.FormValue("username")
		password := r.FormValue("password")

		user, err := models.GetUserByUsername(username)
		if err != nil || user.Password != password {
			http.Error(w, "Invalid credentials", http.StatusUnauthorized)
			return
		}

		session := sessions.GetSession(r)
		session.Values["username"] = username
		fmt.Printf("username %s logged in\n",username)
		session.Save(r, w)

		http.Redirect(w, r, "/chef", http.StatusSeeOther)
		return
	}

	if err := templates.Templates["login.html"].ExecuteTemplate(w, "base.html", map[string]interface{}{}); err != nil {
		panic(err)
	}

}

func RegisterHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		username := r.FormValue("username")
		password := r.FormValue("password")

		err := models.CreateUser(username, password)
		if err != nil {
			http.Error(w, "Registration failed", http.StatusInternalServerError)
			return
		}

		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	if err := templates.Templates["register.html"].ExecuteTemplate(w, "base.html", map[string]interface{}{}); err != nil {
		panic(err)
	}
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	session := sessions.GetSession(r)
	delete(session.Values, "username")
	session.Save(r, w)

	http.Redirect(w, r, "/", http.StatusSeeOther)
}
