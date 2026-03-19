# src/core/detectors/opportunity.py - Main opportunity detector
import logging
from typing import Dict, List
from datetime import datetime
from core.strategies import (
    TriangularArbitrage, FundingArbitrage, GridTrading,
    DCAStrategy, LiquidationSniping, FlashLoanArbitrage,
    CrossExchangeArbitrage, YieldOptimizer, OptionsStrategy,
    MempoolScanner
)

class OpportunityDetector:
    def __init__(self, config: Dict):
        self.logger = logging.getLogger(__name__)
        self.strategies = []
        
        # Initialize all strategies
        if 'triangular' in config.get('enabled', []):
            self.strategies.append(TriangularArbitrage(config))
        if 'funding' in config.get('enabled', []):
            self.strategies.append(FundingArbitrage(config))
        if 'grid' in config.get('enabled', []):
            self.strategies.append(GridTrading(config))
        if 'dca' in config.get('enabled', []):
            self.strategies.append(DCAStrategy(config))
        if 'liquidation' in config.get('enabled', []):
            self.strategies.append(LiquidationSniping(config))
        if 'flash_loan' in config.get('enabled', []):
            self.strategies.append(FlashLoanArbitrage(config))
        if 'cross_exchange' in config.get('enabled', []):
            self.strategies.append(CrossExchangeArbitrage(config))
        if 'yield' in config.get('enabled', []):
            self.strategies.append(YieldOptimizer(config))
        if 'options' in config.get('enabled', []):
            self.strategies.append(OptionsStrategy(config))
        if 'mempool' in config.get('enabled', []):
            self.strategies.append(MempoolScanner(config))
            
    async def scan_all(self, market_data: Dict) -> List[Dict]:
        """Scan all strategies for opportunities"""
        all_opportunities = []
        
        for strategy in self.strategies:
            try:
                opportunities = await strategy.scan(market_data)
                all_opportunities.extend(opportunities)
            except Exception as e:
                self.logger.error(f"Error in {strategy.name}: {e}")
                
        # Sort by expected ROI
        all_opportunities.sort(key=lambda x: x.get('expected_roi', 0), reverse=True)
        
        return all_opportunities