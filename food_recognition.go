package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"image"
	"image/png"
	"io"
	"os"

	aiplatform "cloud.google.com/go/aiplatform/apiv1"
	aiplatformpb "cloud.google.com/go/aiplatform/apiv1/aiplatformpb"
	"google.golang.org/api/option"
	structpb "google.golang.org/protobuf/types/known/structpb"
)

const projectID = "useful-flame-441821-h0"
const location = "us-east1"
const modelName = "gemini-1.5-flash-002"
const imagePath = "images/uploadedImage.png"

var textsi_food = `We only want to find out what ingredients this person has by analyzing what is inside their fridge, 
pantry, or etc. Make it comma separated like: banana, apple, syrup... etc. Listing all the ingredients in their fridge`

func mustOpen(imageFile string) *os.File {
	file, err := os.Open(imageFile)
	if err != nil {
		panic(err)
	}
	return file
}

func analyzeImg(imageFile string, reader io.Reader) (map[string]string, error) {
	//load google cloud  creds
	ctx := context.Background()
	client, err := aiplatform.NewPredictionClient(ctx, option.WithCredentialsFile("useful-flame-441821-h0-5e6960a95210.json"))
	if err != nil { //if there is an error
		return nil, fmt.Errorf("failed to create AI platform client: %v", err)
	}
	defer client.Close()

	// decode and save img to storage

	img, _, err := image.Decode(reader)
	if err != nil {
		return nil, fmt.Errorf("failed to decode image: %v", err)
	}

	outFile, err := os.Create(imagePath)
	if err != nil {
		return nil, fmt.Errorf("failed to create image file: %v", err)
	}
	defer outFile.Close()

	//then we encode the image as a png and we save it
	if err := png.Encode(outFile, img); err != nil {
		return nil, fmt.Errorf("failed to read image file: %v", err)
	}

	//next we read out the saved file
	imgData, err := os.ReadFile(imagePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read image file: %v", err)
	}

	//convert image to base64 encoding
	encodedImage := base64.StdEncoding.EncodeToString(imgData)

	// begin shenanigans
	// creates a request for vertex ai model
	params, err := structpb.NewStruct(map[string]interface{}{
		"temperature":       1.0,
		"max_output_tokens": 8192,
		"top_p":             0.95,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create parameters struct: %v", err)
	}

	// now we create an instance struct
	instanceStruct, err := structpb.NewStruct(map[string]interface{}{
		"mime_type": "image.png",
		"data":      encodedImage,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create instance struct: %v", err)
	}
	//this converts instancestruct to *structPB.value
	instanceValue, err := structpb.NewValue(instanceStruct)
	if err != nil {
		return nil, fmt.Errorf("failed to convert instance struct to value: %v", err)
	}
	//this converts params to *structpb.value
	paramsValue, err := structpb.NewValue(params)
	if err != nil {
		return nil, fmt.Errorf("failed to convert parameters struct to value: %v", err)
	}

	req := &aiplatformpb.PredictRequest{
		Endpoint: fmt.Sprintf("projects/%s/locations/%s/publishers/google/models/%s", projectID, location, modelName),
		Instances: []*structpb.Value{
			instanceValue,
		},
		Parameters: paramsValue,
	}

	// then we actually send the prediction request to Vertex AI
	resp, err := client.Predict(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("failed to predict: %v", err)
	}

	//collect the model's response
	fullResponse := ""
	for _, prediction := range resp.Predictions {
		fullResponse += prediction.String() + " "
	}

	//remove the saved image file to free up space
	if err := os.Remove(imagePath); err != nil {
		fmt.Println("Unable to remove image:", err)
	}

	//Return AI model's response as a json
	return map[string]string{"data": fullResponse}, nil
}

var generationConfig = map[string]interface{}{
	"max_output_tokens": 8192,
	"temperature":       1,
	"top_p":             0.95,
}

// Safety settings placeholder
var safetySettings = []string{
	"HARM_CATEGORY_HATE_SPEECH: OFF",
	"HARM_CATEGORY_DANGEROUS_CONTENT: OFF",
	"HARM_CATEGORY_SEXUALLY_EXPLICIT: OFF",
	"HARM_CATEGORY_HARASSMENT: OFF",
}
