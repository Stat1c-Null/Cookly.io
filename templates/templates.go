package templates

import (
	"embed"
	"html/template"
)

//go:embed *.html
var templateFiles embed.FS

var Templates map[string]*template.Template

func Init() {
	Templates = make(map[string]*template.Template)
	// Parse all HTML files in the embedded templates directory
	Templates["home.html"] = template.Must(template.ParseFS(templateFiles, "home.html", "base.html"))
	Templates["login.html"] = template.Must(template.ParseFS(templateFiles, "login.html", "base.html"))
	Templates["register.html"] = template.Must(template.ParseFS(templateFiles, "register.html", "base.html"))
	Templates["chef.html"] = template.Must(template.ParseFS(templateFiles, "chef.html", "base.html"))
}
