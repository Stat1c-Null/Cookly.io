package gem

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

var client *genai.Client

func init() {
	ctx := context.Background()
	var err error
	key := os.Getenv("GEMINI_API_KEY")
	if key == "" {
		panic("GEMINI_API_KEY not set")
	}
	client, err = genai.NewClient(ctx, option.WithAPIKey(key))
	if err != nil {
		log.Fatal(err)
	}
}

func GetRecipe(ingredients []string) (string, error) {
	ctx := context.Background()
	tmpl := `please suggest a recipe that a user can make using the following ingredients: %s`
	ing_str := strings.Join(ingredients,",")
	prompt := fmt.Sprintf(tmpl, ing_str)
	fmt.Println("My prompt is:\n%s\n",prompt)

	model := client.GenerativeModel("gemini-1.5-flash-002")
	resp, err := model.GenerateContent(ctx, genai.Text(prompt))
	if err != nil {
		return "",err
	}

	response := ""
	for _, part := range resp.Candidates[0].Content.Parts {
		response += fmt.Sprintf("%v",part)
	}
	return response, nil
}

func dummy() {
	fmt.Println("duh")
}

/*
func main() {





}
*/
