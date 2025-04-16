package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/yourusername/bitget-grid-bot/config"
)

var tradingEngine *TradingEngine

func main() {
	// Load configuration
	cfg, err := config.LoadConfig("config/config.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Initialize trading engine
	tradingEngine = NewTradingEngine(*cfg)
	go tradingEngine.Start()

	// Set up HTTP server
	router := http.NewServeMux()
	router.HandleFunc("/start", authMiddleware(startHandler))
	router.HandleFunc("/stop", authMiddleware(stopHandler))
	router.HandleFunc("/status", authMiddleware(statusHandler))
	router.HandleFunc("/stats", authMiddleware(statsHandler))
	router.HandleFunc("/health", healthHandler)

	server := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	// Graceful shutdown
	go func() {
		sigint := make(chan os.Signal, 1)
		signal.Notify(sigint, syscall.SIGINT, syscall.SIGTERM)
		<-sigint

		log.Println("Shutting down server...")
		tradingEngine.Shutdown()

		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		
		if err := server.Shutdown(ctx); err != nil {
			log.Printf("HTTP server shutdown error: %v", err)
		}
	}()

	log.Printf("Server running on %s", server.Addr)
	if err := server.ListenAndServe(); err != http.ErrServerClosed {
		log.Fatalf("HTTP server error: %v", err)
	}
}

func startHandler(w http.ResponseWriter, r *http.Request) {
	if tradingEngine.IsRunning() {
		respondError(w, "Bot is already running", http.StatusBadRequest)
		return
	}
	
	go tradingEngine.Start()
	respondJSON(w, map[string]string{"status": "started"})
}

func stopHandler(w http.ResponseWriter, r *http.Request) {
	if !tradingEngine.IsRunning() {
		respondError(w, "Bot is not running", http.StatusBadRequest)
		return
	}
	
	tradingEngine.Shutdown()
	respondJSON(w, map[string]string{"status": "stopped"})
}

// ... additional handler functions