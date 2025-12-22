#!/usr/bin/env python3
"""
MM SYSTEM ORCHESTRATOR - Integra todos los módulos
Phase 1 - MVP: Pipeline completo
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import json

from mm_data_ingestion import DataIngestion
from mm_quant_engine import QuantEngine, WallData, RegimeData
from mm_ai_layer import AILayer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MMSystemOrchestrator:
    """Pipeline completo: Data → Quant → AI → Output"""
    
    def __init__(self):
        self.ingestion = DataIngestion()
        self.quant = QuantEngine()
        self.ai = AILayer()
    
    def analyze_ticker(self, ticker: str, contracts: list, price: float, 
                      iv: float, expiration: str, 
                      historical_prices: list = None,
                      ticker_profile: dict = None,
                      news: list = None) -> str:
        """
        Análisis completo de un ticker
        
        Returns: MM Brief (texto profesional + escenarios)
        """
        
        if ticker_profile is None:
            ticker_profile = self._default_profile()
        
        if news is None:
            news = []
        
        # ═════════════════════════════════════════════════════════════════
        # PASO 1: DATA INGESTION
        # ═════════════════════════════════════════════════════════════════
        logger.info(f"📥 Ingesting data for {ticker}...")
        snapshot_id = self.ingestion.save_snapshot(ticker, price, iv, contracts, expiration)
        
        if not snapshot_id:
            return f"❌ Error: Could not ingest data for {ticker}"
        
        stored_contracts = self.ingestion.get_contracts(snapshot_id)
        
        # ═════════════════════════════════════════════════════════════════
        # PASO 2: QUANT ENGINE
        # ═════════════════════════════════════════════════════════════════
        logger.info(f"⚙️ Running quant analysis...")
        
        # GEX
        gex = self.quant.calculate_gex(stored_contracts, price)
        gamma_neta = sum(gex.values())
        
        # Walls
        call_wall, put_wall = self.quant.detect_walls(stored_contracts, price, expiration)
        logger.info(f"  Call Wall: ${call_wall.strike:.2f} (OI: {call_wall.oi:,})")
        logger.info(f"  Put Wall: ${put_wall.strike:.2f} (OI: {put_wall.oi:,})")
        
        # Pinning score
        pinning_score = self.quant.calculate_pinning_score(
            call_wall, put_wall, price, gamma_neta,
            historical_pin_rate=ticker_profile.get('pin_hit_rate', 0.5)
        )
        logger.info(f"  Pinning Score: {pinning_score:.2f}")
        
        # Regime
        regime = self.quant.classify_regime(stored_contracts, price, 
                                           historical_prices, gamma_neta)
        logger.info(f"  Regime: {regime.classification} ({regime.confidence:.0%})")
        
        # Targets
        atr = self._estimate_atr(historical_prices) if historical_prices else price * 0.02
        targets = self.quant.calculate_targets(call_wall, put_wall, price, atr)
        
        # ═════════════════════════════════════════════════════════════════
        # PASO 3: AI LAYER
        # ═════════════════════════════════════════════════════════════════
        logger.info(f"🧠 Building MM Brief...")
        
        snapshot = {
            'ticker': ticker,
            'price': price,
            'iv': iv,
            'pcr': self._calc_pcr(stored_contracts)
        }
        
        walls = {
            'call_wall': {
                'strike': call_wall.strike,
                'oi': call_wall.oi,
                'distance_pct': call_wall.distance_pct,
                'strength': call_wall.strength
            },
            'put_wall': {
                'strike': put_wall.strike,
                'oi': put_wall.oi,
                'distance_pct': put_wall.distance_pct,
                'strength': put_wall.strength
            }
        }
        
        regime_dict = {
            'classification': regime.classification,
            'confidence': regime.confidence,
            'gamma_health': regime.gamma_health,
            'pin_probability': regime.pin_probability,
            'vol_risk': regime.vol_risk
        }
        
        brief = self.ai.build_brief(
            snapshot=snapshot,
            walls=walls,
            regime=regime_dict,
            targets=targets,
            ticker_profile=ticker_profile,
            news=news,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        )
        
        return brief
    
    def _calc_pcr(self, contracts: list) -> float:
        """Calcular Put/Call Ratio"""
        total_put_oi = sum(c.get('oi', 0) for c in contracts if c.get('type', '').lower() == 'put')
        total_call_oi = sum(c.get('oi', 0) for c in contracts if c.get('type', '').lower() == 'call')
        return total_put_oi / max(total_call_oi, 1)
    
    def _estimate_atr(self, prices: list) -> float:
        """Estimar ATR desde precios históricos"""
        if not prices or len(prices) < 14:
            return prices[-1] * 0.02 if prices else 100 * 0.02
        
        # ATR simple
        import numpy as np
        returns = np.diff(prices) / prices[:-1]
        atr = np.mean(np.abs(returns[-14:])) * prices[-1]
        return atr
    
    def _default_profile(self) -> Dict:
        """Perfil por defecto (sin histórico)"""
        return {
            'pin_hit_rate': 0.5,
            'wall_respect': 0.6,
            'vol_exp_freq': 0.3,
            'notes': 'Default profile - no historical data'
        }
    
    def generate_json_report(self, ticker: str, contracts: list, price: float,
                           iv: float, expiration: str) -> Dict:
        """
        Genera el JSON report completo (para API/storage)
        
        Estructura institucional lista para integración
        """
        
        gex = self.quant.calculate_gex(contracts, price)
        call_wall, put_wall = self.quant.detect_walls(contracts, price, expiration)
        
        return {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'snapshot': {
                'price': price,
                'iv': iv,
                'put_call_ratio': self._calc_pcr(contracts)
            },
            'walls': {
                'call_wall': {
                    'strike': float(call_wall.strike),
                    'oi': call_wall.oi,
                    'distance_pct': round(call_wall.distance_pct, 2),
                    'strength': call_wall.strength
                },
                'put_wall': {
                    'strike': float(put_wall.strike),
                    'oi': put_wall.oi,
                    'distance_pct': round(put_wall.distance_pct, 2),
                    'strength': put_wall.strength
                }
            },
            'gex_summary': {
                'total_gamma_neta': round(sum(gex.values()), 2),
                'max_gex_strike': float(max(gex, key=gex.get)) if gex else 0,
                'regime_implication': 'Mean reversion' if sum(gex.values()) > 0 else 'Trend risk'
            }
        }


if __name__ == "__main__":
    orch = MMSystemOrchestrator()
    logger.info("✅ MM System Orchestrator ready")
