package sessions

import (
	"fmt"
	"net/http"
	"os"

	"github.com/gorilla/sessions"
)

var store *sessions.CookieStore

func init() {
	session_key := os.Getenv("SECRET_SESSION_KEY")
	if len(session_key) < 8 {
		panic("SECRET_SESSION_KEY not set, or too short")
	}
	store = sessions.NewCookieStore([]byte(session_key))
}

func GetSession(r *http.Request) *sessions.Session {
	session, err := store.Get(r, "session-name")
	if err != nil {
		fmt.Println(err)
	}
	return session
}

func User(r *http.Request) string {
	s := GetSession(r)
	username, found := s.Values["username"]

	fmt.Println(username, found)
	if !found {
		return ""
	}

	if name, ok := username.(string); ok {
		return name
	}
	return ""
}
