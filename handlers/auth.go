package handlers

import (
	"net/http"
	"github.com/Stat1c-Null/Cookly.io/models"
	"github.com/Stat1c-Null/Cookly.io/sessions"
	"github.com/Stat1c-Null/Cookly.io/templates"
)

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
		session.Save(r, w)

		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	templates.Templates.ExecuteTemplate(w, "login.html", nil)
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

	templates.Templates.ExecuteTemplate(w, "register.html", nil)
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	session := sessions.GetSession(r)
	delete(session.Values, "username")
	session.Save(r, w)

	http.Redirect(w, r, "/login", http.StatusSeeOther)
}
