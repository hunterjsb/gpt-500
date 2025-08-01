package config

import (
	"database/sql"
	"fmt"
	"os"

	"claude-20/services/portfolio-db/internal/db"
	_ "github.com/lib/pq"
)

type Config struct {
	DBHost     string
	DBPort     string
	DBUser     string
	DBPassword string
	DBName     string
	Port       string
}

func Load() *Config {
	return &Config{
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnv("DB_PORT", "5432"),
		DBUser:     getEnv("DB_USER", "hunter"),
		DBPassword: getEnv("DB_PASSWORD", "postgres"),
		DBName:     getEnv("DB_NAME", "gpt_500"),
		Port:       getEnv("PORT", "8080"),
	}
}

func (c *Config) ConnectDB() (*sql.DB, *db.Queries, error) {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		c.DBHost, c.DBPort, c.DBUser, c.DBPassword, c.DBName)

	database, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, nil, err
	}

	if err = database.Ping(); err != nil {
		return nil, nil, err
	}

	queries := db.New(database)
	return database, queries, nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}