package handlers

import (
	"net/http"

	"github.com/Stat1c-Null/Cookly.io/sessions"
	"github.com/Stat1c-Null/Cookly.io/templates"
)

func ChefHandler(w http.ResponseWriter, r *http.Request) {
	// Render home page
	username := sessions.User(r)
	if err := templates.Templates["chef.html"].ExecuteTemplate(w, "base.html", map[string]interface{}{
		"Username": username,
	}); err != nil {
		panic(err)
	}
}
