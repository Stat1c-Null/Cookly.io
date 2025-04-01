package handlers

import (
	"net/http"

	"github.com/Stat1c-Null/Cookly.io/templates"
)

func HomeHandler(w http.ResponseWriter, r *http.Request) {
	// Render home page
	if err := templates.Templates["home.html"].ExecuteTemplate(w, "base.html", map[string]interface{}{
	}); err != nil {
		panic(err)
	}
}
