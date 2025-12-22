#!/usr/bin/env python3
"""
MM MEMORY - Backtesting & Ticker Profiles
Phase 1 - Learning system que mejora predicciones
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemorySystem:
    """
    Almacena outcomesTicker: 
    - Predicciones vs Realidad
    - Calcula hit rates por estrategia
    - Ajusta pesos por histórico
    """
    
    def __init__(self, db_path: str = "mm_system.db"):
        self.db_path = Path(db_path)
        self.init_db()
    
    def init_db(self):
        """Crear tablas de outcomesTicker"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabla 1: Predicciones almacenadas
        c.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                predicted_targets TEXT NOT NULL,  -- JSON: [target_a, target_b, target_c]
                call_wall REAL NOT NULL,
                put_wall REAL NOT NULL,
                regime TEXT NOT NULL,
                pinning_score REAL NOT NULL,
                expiration TEXT NOT NULL,
                entry_price REAL NOT NULL,
                UNIQUE(ticker, timestamp, expiration)
            )
        ''')
        
        # Tabla 2: Outcomesl (qué pasó realmente)
        c.execute('''
            CREATE TABLE IF NOT EXISTS outcomes (
                id INTEGER PRIMARY KEY,
                prediction_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                outcome_timestamp DATETIME NOT NULL,
                actual_price REAL NOT NULL,
                price_move_pct REAL NOT NULL,
                target_hit TEXT,  -- 'CALL_WALL', 'PUT_WALL', 'CENTER', 'MISS'
                time_to_target INTEGER,  -- minutos hasta target
                regime_correct BOOLEAN,  -- ¿regex predicho fue acertado?
                wall_respected BOOLEAN,  -- ¿paredes detuvieron precio?
                FOREIGN KEY(prediction_id) REFERENCES predictions(id)
            )
        ''')
        
        # Tabla 3: Ticker Profiles agregados
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticker_profiles (
                ticker TEXT PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                pinning_hit_rate REAL DEFAULT 0.5,  -- % que pinned en call/put wall
                wall_respect_rate REAL DEFAULT 0.6,  -- % que respetó walls como soporte/resistencia
                vol_expansion_freq REAL DEFAULT 0.3,  -- % ocasiones con vol jump
                regime_accuracy REAL DEFAULT 0.5,  -- % regímenes predichos correctamente
                target_reach_rate REAL DEFAULT 0.4,  -- % que alcanzó target
                best_scenario TEXT,  -- 'BULLISH', 'BEARISH', 'MEAN_REVERSION'
                worst_scenario TEXT,
                last_updated DATETIME,
                notes TEXT
            )
        ''')
        
        # Tabla 4: Daily stats (para dashboard)
        c.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_predictions INTEGER,
                successful_predictions INTEGER,
                hit_rate REAL,
                top_ticker TEXT,
                worst_ticker TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Memory tables initialized")
    
    def store_prediction(self, ticker: str, targets: Dict, 
                        call_wall: float, put_wall: float,
                        regime: str, pinning_score: float,
                        expiration: str, entry_price: float) -> int:
        """Almacenar predicción para later tracking"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            import json
            targets_json = json.dumps(targets)
            
            c.execute('''
                INSERT INTO predictions 
                (ticker, timestamp, predicted_targets, call_wall, put_wall, 
                 regime, pinning_score, expiration, entry_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                datetime.now(),
                targets_json,
                call_wall,
                put_wall,
                regime,
                pinning_score,
                expiration,
                entry_price
            ))
            
            pred_id = c.lastrowid
            conn.commit()
            logger.info(f"✅ Prediction stored (ID: {pred_id})")
            return pred_id
            
        except Exception as e:
            logger.error(f"❌ Error storing prediction: {e}")
            return None
        finally:
            conn.close()
    
    def record_outcome(self, prediction_id: int, ticker: str,
                      actual_price: float, entry_price: float,
                      target_hit: str, time_to_target: int,
                      regime_correct: bool, wall_respected: bool):
        """Registrar qué pasó realmente"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            price_move_pct = ((actual_price - entry_price) / entry_price) * 100
            
            c.execute('''
                INSERT INTO outcomes
                (prediction_id, ticker, outcome_timestamp, actual_price, 
                 price_move_pct, target_hit, time_to_target, 
                 regime_correct, wall_respected)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction_id, ticker, datetime.now(), actual_price,
                price_move_pct, target_hit, time_to_target,
                regime_correct, wall_respected
            ))
            
            conn.commit()
            self._update_ticker_profile(ticker)
            logger.info(f"✅ Outcome recorded for {ticker}")
            
        except Exception as e:
            logger.error(f"❌ Error recording outcome: {e}")
        finally:
            conn.close()
    
    def _update_ticker_profile(self, ticker: str):
        """Recalcular métricas del ticker"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Fetch outcomes para este ticker
            c.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN target_hit IN ('CALL_WALL', 'PUT_WALL') THEN 1 ELSE 0 END) as pinning_hits,
                    SUM(CASE WHEN wall_respected = 1 THEN 1 ELSE 0 END) as wall_respects,
                    SUM(CASE WHEN regime_correct = 1 THEN 1 ELSE 0 END) as regime_correct_count
                FROM outcomes
                WHERE ticker = ?
            ''', (ticker,))
            
            result = c.fetchone()
            total, pinning_hits, wall_respects, regime_correct = result if result else (0, 0, 0, 0)
            
            if total == 0:
                logger.warning(f"No outcomes yet for {ticker}")
                return
            
            pinning_rate = (pinning_hits / total) if total > 0 else 0.5
            wall_respect = (wall_respects / total) if total > 0 else 0.6
            regime_accuracy = (regime_correct / total) if total > 0 else 0.5
            
            # Insert or update
            c.execute('''
                INSERT INTO ticker_profiles 
                (ticker, total_predictions, pinning_hit_rate, wall_respect_rate, regime_accuracy, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(ticker) DO UPDATE SET
                    total_predictions = ?,
                    pinning_hit_rate = ?,
                    wall_respect_rate = ?,
                    regime_accuracy = ?,
                    last_updated = ?
            ''', (
                ticker, total, pinning_rate, wall_respect, regime_accuracy, datetime.now(),
                total, pinning_rate, wall_respect, regime_accuracy, datetime.now()
            ))
            
            conn.commit()
            logger.info(f"  📊 {ticker}: Pin={pinning_rate:.1%} Wall={wall_respect:.1%} Regime={regime_accuracy:.1%}")
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
        finally:
            conn.close()
    
    def get_ticker_profile(self, ticker: str) -> Dict:
        """Obtener perfil mejorado por histórico"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT pin_hit_rate, wall_respect_rate, vol_expansion_freq, 
                       regime_accuracy, best_scenario, total_predictions
                FROM ticker_profiles
                WHERE ticker = ?
            ''', (ticker,))
            
            result = c.fetchone()
            
            if result:
                pin_rate, wall_rate, vol_freq, regime_acc, best_scenario, total = result
                return {
                    'pin_hit_rate': pin_rate,
                    'wall_respect_rate': wall_rate,
                    'vol_expansion_freq': vol_freq,
                    'regime_accuracy': regime_acc,
                    'best_scenario': best_scenario,
                    'sample_size': total,
                    'confidence': min(total / 100, 1.0)  # Más datos = más confianza
                }
            else:
                # Default si no hay data
                return {
                    'pin_hit_rate': 0.5,
                    'wall_respect_rate': 0.6,
                    'vol_expansion_freq': 0.3,
                    'regime_accuracy': 0.5,
                    'best_scenario': 'UNKNOWN',
                    'sample_size': 0,
                    'confidence': 0.0,
                    'notes': 'No historical data'
                }
        finally:
            conn.close()
    
    def get_backtesting_summary(self, ticker: str = None, days: int = 30) -> Dict:
        """Resumen de backtesting últimos N días"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            cutoff = datetime.now() - timedelta(days=days)
            
            if ticker:
                # Por ticker específico
                c.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN target_hit IS NOT NULL THEN 1 ELSE 0 END) as hit_count,
                        AVG(ABS(price_move_pct)) as avg_move
                    FROM outcomes
                    WHERE ticker = ? AND outcome_timestamp > ?
                ''', (ticker, cutoff))
            else:
                # Global
                c.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN target_hit IS NOT NULL THEN 1 ELSE 0 END) as hit_count,
                        AVG(ABS(price_move_pct)) as avg_move
                    FROM outcomes
                    WHERE outcome_timestamp > ?
                ''', (cutoff,))
            
            result = c.fetchone()
            total, hits, avg_move = result if result else (0, 0, 0)
            
            return {
                'period': f'Last {days} days',
                'total_outcomes': total,
                'successful_targets': hits,
                'hit_rate': (hits / max(total, 1)) * 100,
                'avg_price_move': avg_move or 0
            }
        finally:
            conn.close()
    
    def get_worst_predictions(self, limit: int = 5) -> List[Dict]:
        """Identificar qué NO funcionó (para aprender)"""
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            c.execute('''
                SELECT p.ticker, p.regime, p.pinning_score, 
                       o.target_hit, o.price_move_pct, o.outcome_timestamp
                FROM outcomes o
                JOIN predictions p ON o.prediction_id = p.id
                WHERE o.target_hit = 'MISS'
                ORDER BY o.outcome_timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in c.fetchall():
                results.append({
                    'ticker': row[0],
                    'regime': row[1],
                    'pinning_score': row[2],
                    'result': row[3],
                    'price_move': row[4],
                    'timestamp': row[5]
                })
            
            return results
        finally:
            conn.close()
    
    def recommend_weight_adjustment(self, ticker: str) -> Dict:
        """
        Basado en histórico, recomendar ajustes de pesos
        para mejorar predicciones
        """
        
        profile = self.get_ticker_profile(ticker)
        
        recommendations = {
            'ticker': ticker,
            'adjustments': {}
        }
        
        # Si pinning no funciona mucho → bajar weight
        if profile['pin_hit_rate'] < 0.4:
            recommendations['adjustments']['pinning_score_weight'] = 0.3
            recommendations['reason_pinning'] = 'Historical pin rate low'
        else:
            recommendations['adjustments']['pinning_score_weight'] = 0.5
        
        # Si paredes respetan mucho → subir weight
        if profile['wall_respect_rate'] > 0.75:
            recommendations['adjustments']['wall_weight'] = 0.8
            recommendations['reason_walls'] = 'Strong historical wall respect'
        else:
            recommendations['adjustments']['wall_weight'] = 0.5
        
        return recommendations


if __name__ == "__main__":
    mem = MemorySystem()
    logger.info("✅ Memory System ready")
    
    # Test
    profile = mem.get_ticker_profile("SPY")
    logger.info(f"SPY Profile: {profile}")
