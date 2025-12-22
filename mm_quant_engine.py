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
        Calcular Gamma Exposure por strike - MEJORADO
        
        GEX = sum(gamma * oi * price²) para cada strike
        Ponderado por: vol, bid-ask spread, moneyness
        
        Interpretación:
        - GEX > 0: Mercado quiere mean reversion (long gamma)
        - GEX < 0: Mercado frágil (short gamma) = riesgo trend
        """
        gex_by_strike = {}
        
        for contract in contracts:
            try:
                strike = float(contract.get('strike', 0))
                gamma = float(contract.get('gamma', 0))
                oi = int(contract.get('open_interest', 0))
                bid = float(contract.get('bid', 0))
                ask = float(contract.get('ask', 0))
                iv = float(contract.get('iv', 0.25))
                
                if strike <= 0 or gamma == 0:
                    continue
                
                # Base GEX
                gex = gamma * oi * (price ** 2)
                
                # Ajuste por liquidez (penalizar spreads amplios)
                spread = ask - bid if ask > bid else 0.01
                spread_pct = spread / ((bid + ask) / 2) if (bid + ask) > 0 else 0.1
                liquidity_factor = max(0.5, 1.0 - spread_pct * 10)
                
                # Ajuste por IV (higher IV = more gamma meaningful)
                iv_factor = max(0.8, min(1.2, iv / 0.20))  # Normalized to 20% IV
                
                # Ajuste por moneyness (ATM gamma > importante)
                moneyness = abs(strike - price) / price
                moneyness_factor = max(0.3, 1.0 - moneyness)
                
                # GEX ajustado
                gex_adjusted = gex * liquidity_factor * iv_factor * moneyness_factor
                
                if strike not in gex_by_strike:
                    gex_by_strike[strike] = 0
                gex_by_strike[strike] += gex_adjusted
                
            except (ValueError, TypeError):
                continue
        
        return gex_by_strike
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
        Score MEJORADO de probabilidad de pinning
        
        Factores:
        1. Distancia a walls (exponencial - muy sensible)
        2. Fuerza de walls (OI poder magnético)
        3. Salud gamma (positiva = presión a mean-revert)
        4. Simetría de walls (balanced = más probable pinning)
        5. Hit rate histórico (aprendizaje)
        6. Spread de opciones (liquidez)
        
        Resultado: 0-1 (probabilidad con máxima precision)
        """
        score = 0.0
        weights = {
            'distance': 0.25,
            'wall_strength': 0.25,
            'gamma_health': 0.20,
            'symmetry': 0.15,
            'historical': 0.10,
            'spread': 0.05
        }
        
        # Factor 1: Distancia (exponencial - más sensible)
        call_dist = abs(call_wall.distance_pct) if call_wall.strike > price else 999
        put_dist = abs(put_wall.distance_pct) if put_wall.strike < price else 999
        closest_dist = min(call_dist, put_dist)
        
        # Exponencial: 0% dist = 1.0, 5% dist = 0.0
        distance_factor = max(0.0, 1.0 - (closest_dist / 5.0) ** 1.5) if closest_dist < 5 else 0.1
        
        # Factor 2: Fuerza de walls (OI absoluto + relativo)
        total_oi = max(call_wall.oi + put_wall.oi, 1)
        call_strength_value = (call_wall.oi / max(total_oi, 1)) * {
            'STRONG': 1.0, 'MEDIUM': 0.6, 'WEAK': 0.2
        }.get(call_wall.strength, 0.1)
        put_strength_value = (put_wall.oi / max(total_oi, 1)) * {
            'STRONG': 1.0, 'MEDIUM': 0.6, 'WEAK': 0.2
        }.get(put_wall.strength, 0.1)
        wall_strength = (call_strength_value + put_strength_value) / 2
        
        # Factor 3: Salud gamma (positiva = buena para pinning)
        if gamma_neta > 0:
            gamma_factor = min(1.0, 0.5 + (gamma_neta / 1e6))  # Normalized
        elif gamma_neta > -1e6:
            gamma_factor = max(0.2, 0.5 - (abs(gamma_neta) / 1e6))
        else:
            gamma_factor = 0.1
        
        # Factor 4: Simetría de walls (balanced = más probable pinning)
        oi_imbalance = abs(call_wall.oi - put_wall.oi) / max(call_wall.oi + put_wall.oi, 1)
        symmetry_factor = max(0.3, 1.0 - oi_imbalance)
        
        # Factor 5: Hit rate histórico (suavizado para evitar overfit)
        historical_factor = 0.3 + (historical_pin_rate * 0.7)
        
        # Spread factor (penalizar opciones ilíquidas) - placeholder
        spread_factor = 0.9  # Podría mejorar con datos de bid-ask
        
        # Calcular score ponderado
        score = (
            distance_factor * weights['distance'] +
            wall_strength * weights['wall_strength'] +
            gamma_factor * weights['gamma_health'] +
            symmetry_factor * weights['symmetry'] +
            historical_factor * weights['historical'] +
            spread_factor * weights['spread']
        )
        
        return min(1.0, max(0.0, score))
        
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
        Calcular targets MEJORADOS con máxima precisión
        
        Basado en:
        1. Paredes de opciones (magnéticos principales)
        2. ATR + volatilidad (rango probable)
        3. Simetría/asimetría de paredes
        4. Estadística histórica de ruptura
        5. Distancia y fuerza relativa
        """
        
        if atr is None:
            atr = price * 0.02
        
        targets = {}
        
        # Calcular probabilidades dinámicas basado en wall strength + distance
        call_distance_pct = call_wall.distance_pct / 100.0 if call_wall.distance_pct else 0.05
        put_distance_pct = abs(put_wall.distance_pct / 100.0) if put_wall.distance_pct else 0.05
        
        # Strength multiplier
        call_strength_mult = {
            'STRONG': 1.5,
            'MEDIUM': 1.0,
            'WEAK': 0.5,
            'NONE': 0.1
        }.get(call_wall.strength, 0.1)
        
        put_strength_mult = {
            'STRONG': 1.5,
            'MEDIUM': 1.0,
            'WEAK': 0.5,
            'NONE': 0.1
        }.get(put_wall.strength, 0.1)
        
        # Distance multiplier (más cerca = más probable)
        call_distance_mult = max(0.5, 1.0 - call_distance_pct * 5)
        put_distance_mult = max(0.5, 1.0 - put_distance_pct * 5)
        
        # Target A: Call wall
        if call_wall.strength != 'NONE':
            call_prob = 0.35 * call_strength_mult * call_distance_mult
            call_prob = min(0.60, max(0.15, call_prob))  # Clamp 15-60%
            
            targets['target_a'] = {
                'target': call_wall.strike,
                'probability': round(call_prob, 2),
                'invalidation': round(call_wall.strike + atr * 2, 2),
                'type': 'bullish',
                'reasoning': f"Call wall OI concentration at ${call_wall.strike:.2f}"
            }
        
        # Target B: Put wall
        if put_wall.strength != 'NONE':
            put_prob = 0.35 * put_strength_mult * put_distance_mult
            put_prob = min(0.60, max(0.15, put_prob))  # Clamp 15-60%
            
            targets['target_b'] = {
                'target': put_wall.strike,
                'probability': round(put_prob, 2),
                'invalidation': round(put_wall.strike - atr * 2, 2),
                'type': 'bearish',
                'reasoning': f"Put wall OI concentration at ${put_wall.strike:.2f}"
            }
        
        # Target C: Mean reversion o equilibrio
        if call_wall.strike > 0 and put_wall.strike > 0:
            center = (call_wall.strike + put_wall.strike) / 2
            
            # Probability based on wall symmetry
            oi_ratio = min(call_wall.oi, put_wall.oi) / max(call_wall.oi, put_wall.oi) if max(call_wall.oi, put_wall.oi) > 0 else 0.5
            center_prob = 0.25 * (0.5 + oi_ratio * 0.5)  # 12.5-25%
            
            targets['target_c'] = {
                'target': round(center, 2),
                'probability': round(center_prob, 2),
                'invalidation': 'sustains outside wall range',
                'type': 'mean_reversion',
                'reasoning': f"Equilibrium between walls (OI balance: {oi_ratio:.1%})"
            }
        
        # Normalizar probabilidades a suma = 1.0
        total_prob = sum(t.get('probability', 0) for t in targets.values())
        if total_prob > 0:
            for target_key in targets:
                targets[target_key]['probability'] = round(
                    targets[target_key]['probability'] / total_prob, 2
                )
        
        return targets


if __name__ == "__main__":
    engine = QuantEngine()
    logger.info("✅ Quant engine initialized")
