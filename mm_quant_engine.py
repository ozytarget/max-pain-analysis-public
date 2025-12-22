#!/usr/bin/env python3
"""
QUANT ENGINE - Calcula GEX, walls, pinning score, regime
Phase 1 - MVP: Core institucional
"""

import numpy as np
from typing import Dict, List, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WallData:
    """Estructura para datos de paredes de opciones"""
    strikes: List[float]
    volumes: List[float]
    strength: float
    density: float

@dataclass
class RegimeData:
    """Estructura para datos de régimen de mercado"""
    regime: str
    volatility: str
    call_put_ratio: float
    avg_iv: float

class QuantEngine:
    """Motor cuantitativo para análisis de mercado microestructura"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def calculate_gex(self, contracts: List[Dict], price: float, expiration: str = None) -> Dict:
        """
        Gamma Exposure Index ajustado por:
        - Liquidez (OI/Spread ratio)
        - IV (volatilidad normalizada)
        - Moneyness (distancia al strike)
        """
        try:
            if not contracts:
                return {'gex_index': 0, 'direction': 'neutral', 'by_strike': {}}
            
            gex_by_strike = {}
            total_gex = 0
            total_weight = 0
            
            for contract in contracts:
                try:
                    strike = float(contract.get('strike', 0))
                    call_gamma = float(contract.get('call_gamma', 0))
                    put_gamma = float(contract.get('put_gamma', 0))
                    call_oi = float(contract.get('call_oi', 0))
                    put_oi = float(contract.get('put_oi', 0))
                    call_iv = float(contract.get('call_iv', 1.0))
                    put_iv = float(contract.get('put_iv', 1.0))
                    bid = float(contract.get('bid', 0.01))
                    ask = float(contract.get('ask', 0.02))
                    
                    # 1. GEX base: call_gamma * call_oi - put_gamma * put_oi
                    gex_raw = (call_gamma * call_oi) - (put_gamma * put_oi)
                    
                    # 2. Factor de liquidez
                    spread = max(ask - bid, 0.01)
                    oi_total = call_oi + put_oi
                    liquidity_factor = (oi_total / max(spread, 0.01)) / 10000 if spread > 0 else 0.8
                    liquidity_factor = min(liquidity_factor, 1.5)
                    
                    # 3. Factor IV - normalizar volatilidad
                    avg_iv = (call_iv + put_iv) / 2
                    iv_factor = 1.0 if avg_iv < 0.5 else (1.5 if avg_iv > 1.0 else 1.0 + avg_iv/2)
                    
                    # 4. Factor moneyness - penalizar strikes lejanos
                    moneyness = abs(strike - price) / price if price > 0 else 0
                    moneyness_factor = 1.0 if moneyness < 0.05 else max(0.5, 1.0 - moneyness)
                    
                    # GEX ajustado
                    gex_adjusted = gex_raw * liquidity_factor * iv_factor * moneyness_factor
                    gex_by_strike[strike] = {
                        'gex_raw': gex_raw,
                        'gex_adjusted': gex_adjusted,
                        'liquidity_factor': liquidity_factor,
                        'iv_factor': iv_factor,
                        'moneyness_factor': moneyness_factor
                    }
                    
                    total_gex += gex_adjusted
                    total_weight += abs(gex_adjusted)
                    
                except (ValueError, KeyError) as e:
                    logger.debug(f"Error procesando contrato: {e}")
                    continue
            
            # Normalizar índice
            if total_weight > 0:
                gex_index = total_gex / total_weight * 100
            else:
                gex_index = 0
            
            # Interpretación
            if gex_index > 100:
                direction = 'bullish'
            elif gex_index < -100:
                direction = 'bearish'
            else:
                direction = 'neutral'
            
            return {
                'gex_index': float(gex_index),
                'direction': direction,
                'by_strike': gex_by_strike,
                'interpretation': self._interpret_gex(gex_index)
            }
        
        except Exception as e:
            logger.error(f"Error en calculate_gex: {e}")
            return {'gex_index': 0, 'direction': 'neutral', 'by_strike': {}}
    
    def _interpret_gex(self, gex_index: float) -> str:
        """Interpretar GEX en contexto de market microstructure"""
        if gex_index > 200:
            return "Mercado fuerte bullish - Demanda extrema de upside"
        elif gex_index > 100:
            return "GEX positivo - Mercado prefiere mean reversion al alza"
        elif gex_index > 0:
            return "Ligera sesgo bullish - Probabilidad de soporte dinamico"
        elif gex_index > -100:
            return "Ligera sesgo bearish - Presión en soporte"
        elif gex_index > -200:
            return "GEX negativo - Mercado frágil, riesgo de trend explosivo"
        else:
            return "GEX extremadamente negativo - Alto riesgo de capitulación"
    
    def detect_walls(self, contracts: List[Dict], price: float, expiration: str) -> Tuple[WallData, WallData]:
        """
        Detecta paredes de opciones (concentraciones de OI)
        Retorna (call_walls, put_walls)
        """
        try:
            call_walls = []
            call_vols = []
            put_walls = []
            put_vols = []
            
            for contract in contracts:
                try:
                    strike = float(contract.get('strike', 0))
                    call_oi = float(contract.get('call_oi', 0))
                    put_oi = float(contract.get('put_oi', 0))
                    
                    if call_oi > 1000:
                        call_walls.append(strike)
                        call_vols.append(call_oi)
                    
                    if put_oi > 1000:
                        put_walls.append(strike)
                        put_vols.append(put_oi)
                
                except (ValueError, KeyError):
                    continue
            
            # Analizar densidad de paredes
            call_strength = np.mean(call_vols) / 10000 if call_vols else 0
            put_strength = np.mean(put_vols) / 10000 if put_vols else 0
            
            call_density = len(call_walls) / max(abs(max(call_walls or [price]) - min(call_walls or [price])), 1)
            put_density = len(put_walls) / max(abs(max(put_walls or [price]) - min(put_walls or [price])), 1)
            
            return (
                WallData(strikes=call_walls, volumes=call_vols, strength=call_strength, density=call_density),
                WallData(strikes=put_walls, volumes=put_vols, strength=put_strength, density=put_density)
            )
        
        except Exception as e:
            logger.error(f"Error en detect_walls: {e}")
            return (
                WallData(strikes=[], volumes=[], strength=0, density=0),
                WallData(strikes=[], volumes=[], strength=0, density=0)
            )
    
    def calculate_pinning_score(self, contracts: List[Dict], price: float, expiration: str) -> Dict:
        """
        Score de pinning con 6 factores ponderados:
        1. Distancia (strikes cercanos ITM/OTM)
        2. Fuerza de pared (concentration)
        3. Gamma health (curvatura)
        4. Simetría (call/put balance)
        5. Histórico (tendencias previas)
        6. Spread (liquidez del mercado)
        """
        try:
            if not contracts:
                return {'pinning_score': 0, 'risk': 'low', 'factors': {}}
            
            # 1. FACTOR DISTANCIA - Qué tan cerca están los strikes al precio
            distances = []
            itm_calls = []
            itm_puts = []
            
            for contract in contracts:
                strike = float(contract.get('strike', 0))
                call_oi = float(contract.get('call_oi', 0))
                put_oi = float(contract.get('put_oi', 0))
                
                dist = abs(strike - price)
                distances.append(dist)
                
                if strike < price:
                    itm_calls.append(call_oi)
                if strike > price:
                    itm_puts.append(put_oi)
            
            distance_factor = 1.0 - (np.mean(distances) / price if distances and price > 0 else 0.5)
            distance_factor = max(0, min(distance_factor, 1.0)) * 15  # peso 15
            
            # 2. FACTOR PARED - Fuerza de concentración
            call_walls, put_walls = self.detect_walls(contracts, price, expiration)
            wall_strength = (call_walls.strength + put_walls.strength) / 2
            wall_factor = min(wall_strength * 20, 15)  # peso 15
            
            # 3. FACTOR GAMMA - Health de la curvatura
            gammas = [float(c.get('call_gamma', 0)) + float(c.get('put_gamma', 0)) for c in contracts]
            avg_gamma = np.mean(gammas) if gammas else 0.01
            gamma_health = min(abs(avg_gamma) * 100, 15)  # peso 15
            
            # 4. FACTOR SIMETRÍA - Balance call/put
            total_call_oi = sum(float(c.get('call_oi', 0)) for c in contracts)
            total_put_oi = sum(float(c.get('put_oi', 0)) for c in contracts)
            total_oi = total_call_oi + total_put_oi
            
            if total_oi > 0:
                balance = abs(total_call_oi - total_put_oi) / total_oi
            else:
                balance = 0.5
            
            symmetry_factor = (1.0 - balance) * 15  # peso 15
            
            # 5. FACTOR HISTÓRICO - Simular tendencia (en real: lookback)
            historical_factor = 10  # Default 10 (sin datos históricos reales)
            
            # 6. FACTOR SPREAD - Liquidez
            spreads = []
            for contract in contracts:
                try:
                    bid = float(contract.get('bid', 0.01))
                    ask = float(contract.get('ask', 0.02))
                    spreads.append(ask - bid)
                except:
                    pass
            
            avg_spread = np.mean(spreads) if spreads else 0.5
            spread_factor = max(0, 15 - avg_spread * 10)  # peso 15
            
            # SCORE TOTAL - suma ponderada (máx 100)
            total_score = (distance_factor + wall_factor + gamma_health + 
                          symmetry_factor + historical_factor + spread_factor)
            pinning_score = min(total_score, 100)
            
            # Risk level
            if pinning_score > 75:
                risk = 'critical'
            elif pinning_score > 50:
                risk = 'high'
            elif pinning_score > 25:
                risk = 'medium'
            else:
                risk = 'low'
            
            return {
                'pinning_score': float(pinning_score),
                'risk': risk,
                'factors': {
                    'distance': float(distance_factor),
                    'wall_strength': float(wall_factor),
                    'gamma_health': float(gamma_health),
                    'symmetry': float(symmetry_factor),
                    'historical': float(historical_factor),
                    'spread_liquidity': float(spread_factor)
                }
            }
        
        except Exception as e:
            logger.error(f"Error en calculate_pinning_score: {e}")
            return {'pinning_score': 0, 'risk': 'low', 'factors': {}}
    
    def calculate_targets(self, price: float, gex_index: float, pinning_score: float, 
                         contracts: List[Dict], expiration: str) -> Dict:
        """
        Calcula targets usando GEX + pinning + probabilidades dinámicas
        Retorna: {upside_target, downside_target, invalidation, probability, reasoning}
        """
        try:
            # 1. Rango ATR (simulado - en real usar ATR de 20D)
            atr = price * 0.02  # 2% como default
            
            # 2. Probabilidad dinámica basada en GEX
            if gex_index > 100:
                gex_prob = 0.65
            elif gex_index > 0:
                gex_prob = 0.55
            elif gex_index > -100:
                gex_prob = 0.45
            else:
                gex_prob = 0.35
            
            # 3. Ajuste por pinning (high pinning = menor movimiento)
            pinning_prob_adjust = 1.0 - (pinning_score / 100) * 0.3
            
            # Probabilidad final
            probability = gex_prob * pinning_prob_adjust
            
            # 4. Identificar resistencias/soportes desde paredes
            call_walls, put_walls = self.detect_walls(contracts, price, expiration)
            
            resistances = sorted([s for s in call_walls.strikes if s > price])
            supports = sorted([s for s in put_walls.strikes if s < price], reverse=True)
            
            # 5. Calcular targets
            if resistances:
                upside_target = resistances[0]
            else:
                upside_target = price + (atr * 2)
            
            if supports:
                downside_target = supports[0]
            else:
                downside_target = price - (atr * 2)
            
            # 6. Niveles de invalidación (2x ATR)
            upside_invalidation = price + (atr * 2)
            downside_invalidation = price - (atr * 2)
            
            # 7. Balance OI para dirección
            total_call_oi = sum(float(c.get('call_oi', 0)) for c in contracts)
            total_put_oi = sum(float(c.get('put_oi', 0)) for c in contracts)
            
            if total_call_oi > total_put_oi:
                bias = 'bullish'
            elif total_put_oi > total_call_oi:
                bias = 'bearish'
            else:
                bias = 'balanced'
            
            # 8. Reasoning text
            reasoning = f"GEX {gex_index:.1f} ({bias}). Pinning risk {pinning_score:.1f}/100. "
            if probability > 0.55:
                reasoning += "Alta probabilidad de movimiento alcista."
            elif probability < 0.45:
                reasoning += "Presión bajista detectada."
            else:
                reasoning += "Balance neutral."
            
            return {
                'upside_target': float(upside_target),
                'downside_target': float(downside_target),
                'upside_invalidation': float(upside_invalidation),
                'downside_invalidation': float(downside_invalidation),
                'probability': float(probability),
                'bias': bias,
                'reasoning': reasoning
            }
        
        except Exception as e:
            logger.error(f"Error en calculate_targets: {e}")
            return {
                'upside_target': price * 1.02,
                'downside_target': price * 0.98,
                'upside_invalidation': price * 1.04,
                'downside_invalidation': price * 0.96,
                'probability': 0.5,
                'bias': 'balanced',
                'reasoning': 'Error en cálculo'
            }
    
    def analyze_regime(self, contracts: List[Dict]) -> Dict:
        """
        Clasifica régimen de mercado: Bullish, Bearish, Choppy, Trapped
        """
        try:
            if not contracts:
                return {'regime': 'unknown', 'volatility': 'low'}
            
            ivs = [float(c.get('call_iv', 0.5)) for c in contracts]
            avg_iv = np.mean(ivs) if ivs else 0.5
            
            call_oi_total = sum(float(c.get('call_oi', 0)) for c in contracts)
            put_oi_total = sum(float(c.get('put_oi', 0)) for c in contracts)
            
            ratio = call_oi_total / (put_oi_total + 0.01)
            
            if avg_iv > 0.8:
                vol = 'high'
            elif avg_iv > 0.5:
                vol = 'medium'
            else:
                vol = 'low'
            
            if ratio > 1.3:
                regime = 'bullish'
            elif ratio < 0.7:
                regime = 'bearish'
            elif avg_iv > 0.7:
                regime = 'choppy'
            else:
                regime = 'trapped'
            
            return {
                'regime': regime,
                'volatility': vol,
                'call_put_ratio': float(ratio),
                'avg_iv': float(avg_iv)
            }
        
        except Exception as e:
            logger.error(f"Error en analyze_regime: {e}")
            return {'regime': 'unknown', 'volatility': 'low'}
