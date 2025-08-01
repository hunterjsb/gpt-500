package main

import (
	"database/sql"
	"log"
	"net/http"

	"claude-20/services/portfolio-db/pkg/config"
	"claude-20/services/portfolio-db/pkg/mcp"
	"claude-20/services/portfolio-db/pkg/portfolio"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Connect to database
	database, queries, err := cfg.ConnectDB()
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer database.Close()

	// Initialize services
	portfolioService := portfolio.NewService(database, queries)
	mcpHandler := mcp.NewHandler(portfolioService)

	// Setup HTTP routes
	http.Handle("/mcp", mcpHandler)
	http.HandleFunc("/health", healthHandler(database))

	// Start server
	log.Printf("Starting MCP server on port %s", cfg.Port)
	log.Fatal(http.ListenAndServe(":"+cfg.Port, nil))
}

func healthHandler(database *sql.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if err := database.Ping(); err != nil {
			http.Error(w, "Database connection failed", http.StatusServiceUnavailable)
			return
		}
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	}
}