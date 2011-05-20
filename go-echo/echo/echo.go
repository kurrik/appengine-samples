package echo

import (
  "http"
  "fmt"
  "template"
  "time"
)

type PostData struct {
  Content string // post content
  Seconds int64  // timestamp
  Host string    // hostname
}

func init() {
  http.HandleFunc("/dest", posthandler)
  http.HandleFunc("/", formhandler)
}

func formhandler (w http.ResponseWriter, r *http.Request) {
  fmt.Fprint(w, `<!DOCTYPE html>
<html>
  <body>
    <form method="POST" action="/dest">
      <input type="text" name="content" placeholder="Put content here" />
      <button>Submit</button>
    </form>
  </body>
</html>`)
}

func posthandler (w http.ResponseWriter, r *http.Request) {
  data := PostData {
    Content: r.FormValue("content"),
    Seconds: time.Seconds(),
    Host: r.Host,
  }
  
  if err := postTemplate.Execute(w, data); err != nil {
    http.Error(w, err.String(), http.StatusInternalServerError)
  }
}

var postTemplate = template.MustParse(postTemplateHTML, nil)
const postTemplateHTML = `
<!DOCTYPE html>
<html>
  <body>
    <pre>{Content|html}</pre>
    <p>{Seconds}</p>
    <a href="http://{Host}/">Back</a>
  </body>
</html>`
