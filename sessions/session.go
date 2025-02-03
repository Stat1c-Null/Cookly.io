package sessions

import (
	"github.com/gorilla/sessions"
	"net/http"
)

var Store = sessions.NewCookieStore([]byte("super-secret-key"))

func GetSession(r *http.Request) *sessions.Session {
	session, _ := Store.Get(r, "session-name")
	return session
}
