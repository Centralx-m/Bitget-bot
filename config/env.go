package config

import (
	"log"
	"os"
)

type EnvConfig struct {
	BitgetAPIKey        string
	BitgetAPISecret     string
	BitgetAPIPassphrase string
	VercelEnv           string
}

func LoadEnv() *EnvConfig {
	return &EnvConfig{
		BitgetAPIKey:        getEnv("BITGET_API_KEY", ""),
		BitgetAPISecret:     getEnv("BITGET_API_SECRET", ""),
		BitgetAPIPassphrase: getEnv("BITGET_API_PASSPHRASE", ""),
		VercelEnv:           getEnv("VERCEL_ENV", "development"),
	}
}

func getEnv(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		if defaultValue == "" {
			log.Fatalf("Missing required environment variable: %s", key)
		}
		return defaultValue
	}
	return value
}