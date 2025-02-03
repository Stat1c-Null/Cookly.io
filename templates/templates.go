package templates

import (
	"embed"
	"html/template"
	"log"
)

//go:embed *.html
var templateFiles embed.FS

var Templates *template.Template

func Init() {
	var err error
	// Parse all HTML files in the embedded templates directory
	Templates, err = template.ParseFS(templateFiles, "*.html")
	if err != nil {
		log.Fatal("Error parsing templates:", err)
	}
}
