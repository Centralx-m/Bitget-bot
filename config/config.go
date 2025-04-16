package config

import (
	"log"
	"os"
	"time"

	"gopkg.in/yaml.v3"
)

type Config struct {
	API struct {
		Key        string `yaml:"key"`
		Secret     string `yaml:"secret"`
		Passphrase string `yaml:"passphrase"`
	} `yaml:"api"`

	Symbol string `yaml:"symbol"`
	Market string `yaml:"market"`

	Grid struct {
		UpperPrice     float64 `yaml:"upper_price"`
		LowerPrice     float64 `yaml:"lower_price"`
		Grids          int     `yaml:"grids"`
		Investment     float64 `yaml:"investment"`
		TriggerOffset  float64 `yaml:"trigger_offset"` // 0.01 = 1%
		PricePrecision int     `yaml:"price_precision"`
		SizePrecision  int     `yaml:"size_precision"`
	} `yaml:"grid"`

	RiskManagement struct {
		Enabled         bool    `yaml:"enabled"`
		MaxDailyLossPct float64 `yaml:"max_daily_loss_pct"`
		MaxPositionSize float64 `yaml:"max_position_size"`
		StopLossPct     float64 `yaml:"stop_loss_pct"`
	} `yaml:"risk_management"`

	Monitoring struct {
		Telegram struct {
			Enabled  bool   `yaml:"enabled"`
			BotToken string `yaml:"bot_token"`
			ChatID   string `yaml:"chat_id"`
		} `yaml:"telegram"`
	} `yaml:"monitoring"`
}

func LoadConfig(path string) (*Config, error) {
	config := &Config{}
	
	file, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	
	err = yaml.Unmarshal(file, config)
	if err != nil {
		return nil, err
	}
	
	// Set defaults
	if config.Grid.TriggerOffset == 0 {
		config.Grid.TriggerOffset = 0.005 // 0.5% default offset
	}
	
	return config, nil
}