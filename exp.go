package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

// Define the structure for the prediction request
type PredictionRequest struct {
	Smiles string `json:"smiles"` // Corrected the struct tag syntax
}

// Function to make a prediction request to the API
func makePredictionRequest(apiURL, smiles string) {
	requestPayload := PredictionRequest{Smiles: smiles}
	jsonData, err := json.Marshal(requestPayload)
	if err != nil {
		fmt.Println("Error marshalling input data:", err)
		return
	}

	resp, err := http.Post(apiURL, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Println("Error making request:", err)
		return
	}
	defer resp.Body.Close()

	// Assuming the server responds with an image file
	outputFile, err := os.Create("molecule_image.png")
	if err != nil {
		fmt.Println("Error creating file:", err)
		return
	}
	defer outputFile.Close()

	_, err = io.Copy(outputFile, resp.Body)
	if err != nil {
		fmt.Println("Error saving image:", err)
		return
	}

	fmt.Println("Molecule image saved as 'molecule_image.png'")
}

// Main function
func main() {
	flaskAPIURL := "http://localhost:5000/predict"
	scanner := bufio.NewScanner(os.Stdin)

	fmt.Println("Enter a SMILES string for lipophilicity prediction and molecule image retrieval:")
	scanner.Scan()
	smilesString := scanner.Text()

	fmt.Println("Sending prediction request to Flask API...")
	makePredictionRequest(flaskAPIURL, smilesString)
}
