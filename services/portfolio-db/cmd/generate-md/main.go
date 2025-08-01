package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"claude-20/services/portfolio-db/pkg/config"
	"claude-20/services/portfolio-db/internal/db"
)

func main() {
	cfg := config.Load()
	database, queries, err := cfg.ConnectDB()
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer database.Close()

	// Get all holdings from database
	holdings, err := queries.GetAllHoldings(context.Background())
	if err != nil {
		log.Fatal("Failed to get holdings:", err)
	}

	if len(holdings) == 0 {
		log.Fatal("No holdings found in database")
	}

	// Generate markdown content
	markdown := generateMarkdown(holdings)

	// Write to GPT20.md in the agent directory
	outputPath := "/home/hunter/Desktop/claude-20/agent/md/indices/GPT20.md"
	
	// Ensure directory exists
	dir := filepath.Dir(outputPath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		log.Fatal("Failed to create directory:", err)
	}

	// Write the file
	if err := os.WriteFile(outputPath, []byte(markdown), 0644); err != nil {
		log.Fatal("Failed to write file:", err)
	}

	fmt.Printf("Successfully generated GPT20.md with %d holdings\n", len(holdings))
	fmt.Printf("Output: %s\n", outputPath)
}

func generateMarkdown(holdings []db.PortfolioHolding) string {
	var sb strings.Builder
	
	// Header
	sb.WriteString("# GPT20 - AI-Curated Stock Index\n\n")
	sb.WriteString("*An algorithmically-managed portfolio of 20 high-conviction stocks, maintained by GPT-4o with real-time market analysis.*\n\n")
	
	// Generation timestamp
	sb.WriteString(fmt.Sprintf("**Last Updated:** %s\n\n", time.Now().Format("January 2, 2006 at 3:04 PM MST")))
	
	// Portfolio overview
	sb.WriteString("## Portfolio Overview\n\n")
	sb.WriteString("This index represents a conviction-weighted portfolio of high-quality stocks with dynamic allocation based on opportunity size, risk assessment, and market analysis. ")
	sb.WriteString("Holdings are selected based on fundamental analysis, market performance, sector diversification, and growth potential.\n\n")
	
	// Holdings list
	sb.WriteString("## Current Holdings\n\n")
	
	for i, holding := range holdings {
		ticker := holding.Ticker
		name := holding.Name
		weight := holding.Weight
		priceStr := holding.Price
		
		// Parse price
		price, _ := strconv.ParseFloat(priceStr, 64)
		
		// Get comment
		comment := ""
		if holding.Comment.Valid {
			comment = holding.Comment.String
		}
		
		// Format entry
		sb.WriteString(fmt.Sprintf("%d. **%s (%s)** - %s%% \n", i+1, name, ticker, weight))
		if price > 0 {
			sb.WriteString(fmt.Sprintf("   *Current Price: $%.2f*\n", price))
		}
		if comment != "" {
			sb.WriteString(fmt.Sprintf("   \n   %s\n", comment))
		}
		sb.WriteString("\n")
	}
	
	// Footer
	sb.WriteString("---\n\n")
	sb.WriteString("## Methodology\n\n")
	sb.WriteString("This index is maintained through:\n")
	sb.WriteString("- **Fundamental Analysis**: Financial health, competitive advantages, and growth prospects\n")
	sb.WriteString("- **Market Intelligence**: Real-time price data and performance tracking\n")
	sb.WriteString("- **Sector Diversification**: Balanced exposure across technology, healthcare, finance, consumer goods, and energy\n")
	sb.WriteString("- **Risk Management**: Dynamic weighting with concentration limits (max 15% per position) to balance conviction with diversification\n\n")
	
	sb.WriteString(fmt.Sprintf("*Generated automatically from portfolio database on %s*\n", time.Now().Format("2006-01-02 15:04:05")))
	
	return sb.String()
}