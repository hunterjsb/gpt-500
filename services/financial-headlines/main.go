package main

import (
	"log"
	"net/http"

	"claude-20/services/financial-headlines/pkg/headlines"
	"claude-20/services/financial-headlines/pkg/mcp"
	"os"
)

func main() {
	// Initialize services
	headlinesService := headlines.NewService()
	mcpHandler := mcp.NewHandler(headlinesService)

	// Setup HTTP routes
	http.Handle("/mcp", mcpHandler)
	http.HandleFunc("/health", healthHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8081" // Default port
	}

	// Start server
	log.Printf("Starting MCP server on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}
