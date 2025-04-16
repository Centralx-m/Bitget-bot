package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"sync"
	"time"
)

var (
	activeSessions = make(map[string]*TradingSession)
	sessionMutex   sync.Mutex
)

func startBotHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var config BotConfig
	if err := json.NewDecoder(r.Body).Decode(&config); err != nil {
		respondWithError(w, "Invalid request body")
		return
	}

	if err := validateConfig(config); err != nil {
		respondWithError(w, err.Error())
		return
	}

	sessionMutex.Lock()
	defer sessionMutex.Unlock()

	if _, exists := activeSessions[config.Symbol]; exists {
		respondWithError(w, fmt.Sprintf("Bot already running for %s", config.Symbol))
		return
	}

	session := NewTradingSession(config)
	activeSessions[config.Symbol] = session

	// Start the trading session in a goroutine
	ctx, cancel := context.WithCancel(context.Background())
	go func() {
		session.Run(ctx)
		cancel()
		sessionMutex.Lock()
		delete(activeSessions, config.Symbol)
		sessionMutex.Unlock()
	}()

	// Store the cancel function
	session.CancelFunc = cancel

	respondWithSuccess(w, fmt.Sprintf("Grid bot started for %s", config.Symbol))
}

func validateConfig(config BotConfig) error {
	// Validate all configuration parameters
	// Implementation omitted for brevity
	return nil
}

// Other handlers remain similar but updated to use TradingSession
