#!/usr/bin/env python3
"""
QUANT ENGINE - Calcula GEX, walls, pinning score, regime
Phase 1 - MVP: Core institucional
"""

import numpy as np
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WallData:
    """Estructura de pared de opciones"""
    strike: float
    oi: int
    type: str  # 'call' o 'put'
    distance_pct: float
    strength: str  # 'WEAK', 'MEDIUM', 'STRONG'


@dataclass
class RegimeData:
    """Clasificación de régimen"""
    classification: str  # 'CHOP', 'TREND', 'SQUEEZE'
    confidence: float  # 0-1
    gamma_health: str  # 'POSITIVE', 'NEUTRAL', 'NEGATIVE'
    pin_probability: float  # 0-1
    vol_risk: str  # 'COMPRESSION', 'NEUTRAL', 'EXPANSION'


class QuantEngine:
    """Motor cuantitativo de market making"""
    
    def __init__(self):
        self.wall_strength_threshold = 1.5  # OI es 1.5x el promedio
        self.chop_atr_percentile = 30  # Volatilidad baja = chop
        self.trend_atr_percentile = 70  # Volatilidad alta = trend
    
    def calculate_gex(self, contracts: List[Dict], price: float) -> Dict[str, float]:
        """
        Calcular Gamma Exposure por strike
        
        GEX = sum(gamma * oi * price²) para cada strike
        
        Interpretación:
        - GEX positivo alto → mercado quiere mean reversion
        - GEX negativo alto → mercado frágil, riesgo de trend explosivo
        """
        gex_by_strike = {}
        
        for contract in contracts:
            strike = contract.get('strike')
            gamma = contract.get('gamma', 0)
            oi = contract.get('oi', 0)
            contract_type = contract.get('type', 'call').lower()
            
            # Gamma negativa para puts (por convención MM)
            gamma_signed = gamma if contract_type == 'call' else -gamma
            
            if strike not in gex_by_strike:
                gex_by_strike[strike] = 0
            
            # GEX = gamma * OI * price²
            gex_value = gamma_signed * oi * (price ** 2)
            gex_by_strike[strike] += gex_value
        
        return gex_by_strike
    
    def detect_walls(self, contracts: List[Dict], price: float, 
                    expiration: str) -> Tuple[WallData, WallData]:
        """
        Detectar call wall (encima) y put wall (debajo)
        
        Wall = strike con máximo OI relativo (>1.5x promedio cercano)
        """
        # Separar por tipo y expiración
        calls = [c for c in contracts 
                if c.get('type', '').lower() == 'call' and c.get('expiration') == expiration]
        puts = [c for c in contracts 
               if c.get('type', '').lower() == 'put' and c.get('expiration') == expiration]
        
        call_wall = self._find_wall(calls, price, 'call')
        put_wall = self._find_wall(puts, price, 'put')
        
        return call_wall, put_wall
    
    def _find_wall(self, contracts: List[Dict], price: float, 
                  wall_type: str) -> WallData:
        """Helper para detectar una pared"""
        if not contracts:
            return WallData(strike=price, oi=0, type=wall_type, distance_pct=0, strength='NONE')
        
        strikes = sorted(set(c.get('strike') for c in contracts))
        ois = {c.get('strike'): c.get('oi', 0) for c in contracts}
        
        # Filtrar por tipo
        if wall_type == 'call':
            relevant_strikes = [s for s in strikes if s > price]
        else:
            relevant_strikes = [s for s in strikes if s < price]
        
        if not relevant_strikes:
            return WallData(strike=price, oi=0, type=wall_type, distance_pct=0, strength='NONE')
        
        # Encontrar máximo OI
        max_strike = max(relevant_strikes, key=lambda s: ois.get(s, 0))
        max_oi = ois.get(max_strike, 0)
        
        # Comparar con promedio cercano (±2%)
        nearby = [s for s in relevant_strikes 
                 if abs(s - max_strike) / max_strike < 0.02]
        avg_oi_nearby = np.mean([ois.get(s, 0) for s in nearby]) if nearby else max_oi
        
        # Determinar fuerza
        oi_ratio = max_oi / max(avg_oi_nearby, 1)
        if oi_ratio > 2.0:
            strength = 'STRONG'
        elif oi_ratio > 1.5:
            strength = 'MEDIUM'
        else:
            strength = 'WEAK'
        
        distance = abs(max_strike - price) / price * 100
        
        return WallData(
            strike=max_strike,
            oi=max_oi,
            type=wall_type,
            distance_pct=distance if wall_type == 'call' else -distance,
            strength=strength
        )
    
    def calculate_pinning_score(self, call_wall: WallData, put_wall: WallData,
                               price: float, gamma_neta: float, 
                               historical_pin_rate: float = 0.5) -> float:
        """
        Score de probabilidad de "pinning" (precio termina en wall)
        
        Factores:
        1. Distancia a walls (más cerca = más probable)
        2. Fuerza de walls (OI mayor = más "gravedad")
        3. Salud gamma (gamma positiva = mean reversion)
        4. Hit rate histórico del ticker
        
        Resultado: 0-1 (probabilidad)
        """
        score = 0.0
        
        # Factor 1: Distancia
        closest_wall_distance = min(
            abs(call_wall.distance_pct) if call_wall.strike > price else 999,
            abs(put_wall.distance_pct) if put_wall.strike < price else 999
        )
        
        if closest_wall_distance < 1.0:
            distance_factor = 0.8
        elif closest_wall_distance < 2.0:
            distance_factor = 0.6
        else:
            distance_factor = 0.3
        
        # Factor 2: Fuerza de walls
        wall_strength = 0
        if call_wall.strength == 'STRONG':
            wall_strength += 0.4
        elif call_wall.strength == 'MEDIUM':
            wall_strength += 0.2
        
        if put_wall.strength == 'STRONG':
            wall_strength += 0.4
        elif put_wall.strength == 'MEDIUM':
            wall_strength += 0.2
        
        # Factor 3: Gamma (positiva = mean reversion = más pinning)
        if gamma_neta > 0:
            gamma_factor = 0.4
        else:
            gamma_factor = 0.1
        
        # Factor 4: Histórico
        historical_factor = historical_pin_rate * 0.3
        
        # Combinar
        score = (
            distance_factor * 0.4 +
            wall_strength * 0.3 +
            gamma_factor * 0.2 +
            historical_factor * 0.1
        )
        
        return min(max(score, 0), 1.0)
    
    def classify_regime(self, contracts: List[Dict], price: float,
                       historical_prices: List[float] = None,
                       gamma_neta: float = 0) -> RegimeData:
        """
        Clasificar régimen: CHOP, TREND o SQUEEZE
        
        CHOP:
        - ATR bajo / vol baja
        - Gamma positiva neta
        - Precio oscila entre walls
        
        TREND:
        - ATR alto / vol alta
        - Gamma negativa (fragilidad)
        - Riesgo de ruptura
        
        SQUEEZE:
        - Bollinger Bands estrechas
        - IV baja
        - Explosión probable
        """
        
        # Calcular ATR (si tenemos precios históricos)
        if historical_prices and len(historical_prices) > 14:
            atr = self._calculate_atr(historical_prices)
            atr_percentile = self._estimate_atr_percentile(atr, historical_prices)
        else:
            atr_percentile = 50
        
        # Clasificación
        if atr_percentile < self.chop_atr_percentile:
            classification = 'CHOP'
            confidence = 0.7
        elif atr_percentile > self.trend_atr_percentile:
            classification = 'TREND'
            confidence = 0.75
        else:
            classification = 'SQUEEZE'
            confidence = 0.6
        
        # Gamma health
        if gamma_neta > 0:
            gamma_health = 'POSITIVE'
        elif gamma_neta < -0.001:
            gamma_health = 'NEGATIVE'
        else:
            gamma_health = 'NEUTRAL'
        
        # Pin probability
        if classification == 'CHOP':
            pin_prob = 0.7
        elif classification == 'TREND':
            pin_prob = 0.2
        else:
            pin_prob = 0.5
        
        # Vol risk
        if classification == 'SQUEEZE':
            vol_risk = 'EXPANSION'
        elif classification == 'TREND':
            vol_risk = 'EXPANSION'
        else:
            vol_risk = 'NEUTRAL'
        
        return RegimeData(
            classification=classification,
            confidence=confidence,
            gamma_health=gamma_health,
            pin_probability=pin_prob,
            vol_risk=vol_risk
        )
    
    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calcular ATR simple"""
        if len(prices) < period:
            return np.std(prices) * 100 / np.mean(prices)
        
        returns = np.diff(prices) / prices[:-1]
        tr = np.abs(returns)
        atr = np.mean(tr[-period:]) * prices[-1]
        return atr
    
    def _estimate_atr_percentile(self, atr: float, prices: List[float]) -> float:
        """Estimar percentil de ATR histórico"""
        if len(prices) < 30:
            return 50
        
        historical_atrs = []
        for i in range(30, len(prices)):
            h_atr = self._calculate_atr(prices[i-30:i])
            historical_atrs.append(h_atr)
        
        if not historical_atrs:
            return 50
        
        percentile = np.percentileofscore(historical_atrs, atr)
        return percentile
    
    def calculate_targets(self, call_wall: WallData, put_wall: WallData,
                         price: float, atr: float = None) -> Dict[str, Dict]:
        """
        Calcular targets probabilísticos
        
        Basado en:
        1. Paredes de opciones (imanes naturales)
        2. ATR (rango típico)
        3. Estadística histórica
        """
        
        if atr is None:
            atr = price * 0.02  # Default 2%
        
        targets = {}
        
        # Target A: Call wall
        if call_wall.strength != 'NONE':
            targets['target_a'] = {
                'level': call_wall.strike,
                'probability': 0.4 if call_wall.strength == 'STRONG' else 0.3,
                'invalidation': f"breaks {call_wall.strike + atr:.2f}",
                'type': 'bullish'
            }
        
        # Target B: Put wall
        if put_wall.strength != 'NONE':
            targets['target_b'] = {
                'level': put_wall.strike,
                'probability': 0.35 if put_wall.strength == 'STRONG' else 0.25,
                'invalidation': f"breaks {put_wall.strike - atr:.2f}",
                'type': 'bearish'
            }
        
        # Target C: Mean reversion (centro)
        if len(targets) < 2:
            center = (call_wall.strike + put_wall.strike) / 2 if (call_wall.strike > 0 and put_wall.strike > 0) else price
            targets['target_c'] = {
                'level': center,
                'probability': 0.3,
                'invalidation': 'breaks a wall',
                'type': 'neutral'
            }
        
        return targets


if __name__ == "__main__":
    engine = QuantEngine()
    logger.info("✅ Quant engine initialized")
