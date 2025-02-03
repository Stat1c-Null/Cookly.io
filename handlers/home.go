package handlers

import (
	"net/http"
	"github.com/Stat1c-Null/Cookly.io/sessions"
	"github.com/Stat1c-Null/Cookly.io/templates"
)

func HomeHandler(w http.ResponseWriter, r *http.Request) {
	session := sessions.GetSession(r)
	username := session.Values["username"]
	if username == nil {
		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	// Render home page
	templates.Templates.ExecuteTemplate(w, "home.html", map[string]interface{}{
		"Username": username,
	})
}
