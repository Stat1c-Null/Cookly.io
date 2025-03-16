package main

import (
	"context"
	"fmt"
	"os"
	"strings"
	"sync"

	//"cloud.google.com/go/vertexai"
	"cloud.google.com/go/vertexai/genai"
	"google.golang.org/api/option"
)

var recipeStore = struct {
	sync.Mutex
	data string
}{data: ""}

var textsi_text = `You will be helping users to create recipes with the stuff they tell you that they have in 
their kitchen or at their disposal, add serving size, calories, fats amount, and protein. When writing the recipe have it like **Meal Name** Name and not on a new line keep it right next to it.
Format it like **Meal Name:** (Actual Meal Name Here), **Ingredients:** (Actual Ingredient list), **Instructions:** (Actual Instruction list), **Notes:** (Actual notes)`

// MultiTurnGenerateContent generates a recipe based on ingredients and user constraints
func MultiTurnGenerateContent(ingredients, calories, protein, carbs, fat, people string, allergens []string) string {
	os.Setenv("GOOGLE_APPLICATION_CREDENTIALS", "useful-flame-441821-h0-5e6960a95210.json")

	ctx := context.Background()
	projectID := "useful-flame-441821-h0"
	location := "us-central1"
	client, err := genai.NewClient(ctx, projectID, location, option.WithCredentialsFile("useful-flame-441821-h0-5e6960a95210.json"))
	if err != nil {
		fmt.Println("Error initializing Vertex AI:", err)
		return ""
	}
	defer client.Close()

	model := client.GenerativeModel("gemini-1.0-pro")
	model.SetTemperature(0.95)
	model.SetTopP(0.95)
	model.SetMaxOutputTokens(1024)
	model.SystemInstruction = genai.NewUserContent(genai.Text(textsi_text))

	//set the value of those jawns
	*model.MaxOutputTokens = 1024
	*model.Temperature = 1.0
	*model.TopP = 0.95

	// Default assumed ingredients
	assumedIngredients := "salt, pepper, oil"
	formattedAllergens := formatAllergens(allergens)

	fullPrompt := fmt.Sprintf("What can I cook with: %s, %s%s? Break your response into the following parts: Meal Name, Ingredients, Instructions, Notes.",
		ingredients, assumedIngredients, formattedAllergens)

	fmt.Println("Debug: Sending to model ->", fullPrompt)

	response, err := model.GenerateContent(ctx, genai.Text(fullPrompt))

	if err != nil {
		fmt.Println("Error generating response:", err)
		return ""
	}

	text := string("\nGemini says you should try:\n" + response.Candidates[0].Content.Parts[0].(genai.Text))
	fmt.Println(text)

	// Store recipe safely
	recipeStore.Lock()
	recipeStore.data = text
	recipeStore.Unlock()

	return text
}

// GetRecipe retrieves the last generated recipe
func GetRecipe() string {
	recipeStore.Lock()
	defer recipeStore.Unlock()
	return recipeStore.data
}

// formatNutrients constructs a formatted string for nutritional constraints
func formatNutrients(calories, protein, carbs, fat, people string) string {
	var formattedNutrients []string

	if calories != "" {
		formattedNutrients = append(formattedNutrients, "under "+calories+" calories")
	}
	if protein != "" {
		formattedNutrients = append(formattedNutrients, protein+" protein")
	}
	if carbs != "" {
		formattedNutrients = append(formattedNutrients, carbs+" carbs")
	}
	if fat != "" {
		formattedNutrients = append(formattedNutrients, fat+" fat")
	}
	if people != "" {
		if people == "1" {
			formattedNutrients = append(formattedNutrients, "for 1 person")
		} else {
			formattedNutrients = append(formattedNutrients, "for "+people+" people")
		}
	}

	return strings.Join(formattedNutrients, ", ")
}

// formatAllergens constructs a formatted string for allergens
func formatAllergens(allergens []string) string {
	if len(allergens) == 0 {
		return ""
	}
	return ", my allergies are " + strings.Join(allergens, ", ")
}
