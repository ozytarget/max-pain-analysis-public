#!/usr/bin/env python3
"""
DATA INGESTION MODULE - Descarga y guarda snapshots de opciones en BD
Phase 1 - MVP: Tradier API → SQLite
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
DB_PATH = Path("mm_system.db")
TRADIER_API_KEY = ""  # Se toma del .env
TICKERS = ["SPY", "QQQ", "NVDA", "TSLA"]

class DataIngestion:
    """Maneja descarga y almacenamiento de datos de opciones"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Crear tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Tabla de snapshots
        c.execute('''
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                underlying_price REAL NOT NULL,
                underlying_iv REAL,
                put_call_ratio REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, timestamp)
            )
        ''')
        
        # Tabla de contratos
        c.execute('''
            CREATE TABLE IF NOT EXISTS contracts (
                id INTEGER PRIMARY KEY,
                snapshot_id INTEGER NOT NULL,
                strike REAL NOT NULL,
                type TEXT NOT NULL,  -- 'call' o 'put'
                iv REAL,
                oi INTEGER,
                volume INTEGER,
                delta REAL,
                gamma REAL,
                theta REAL,
                vega REAL,
                bid REAL,
                ask REAL,
                expiration TEXT NOT NULL,  -- YYYY-MM-DD
                FOREIGN KEY(snapshot_id) REFERENCES snapshots(id),
                UNIQUE(snapshot_id, strike, type, expiration)
            )
        ''')
        
        # Tabla de niveles calculados
        c.execute('''
            CREATE TABLE IF NOT EXISTS computed_levels (
                id INTEGER PRIMARY KEY,
                snapshot_id INTEGER NOT NULL,
                call_wall_strike REAL,
                call_wall_oi INTEGER,
                put_wall_strike REAL,
                put_wall_oi INTEGER,
                pinning_score REAL,
                regime TEXT,  -- 'CHOP', 'TREND', 'SQUEEZE'
                gamma_flip_zone TEXT,  -- JSON: [level_low, level_high]
                computed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(snapshot_id) REFERENCES snapshots(id),
                UNIQUE(snapshot_id)
            )
        ''')
        
        # Tabla de noticias
        c.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY,
                ticker TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                title TEXT NOT NULL,
                source TEXT,
                sentiment_score REAL,  -- -1 a 1
                impact_score REAL,  -- 0 a 1
                url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, title, timestamp)
            )
        ''')
        
        # Tabla de perfiles por ticker
        c.execute('''
            CREATE TABLE IF NOT EXISTS ticker_profiles (
                ticker TEXT PRIMARY KEY,
                stat_pinning_hit_rate REAL DEFAULT 0.5,
                stat_wall_respect_rate REAL DEFAULT 0.5,
                stat_vol_expansion_freq REAL DEFAULT 0.3,
                stat_target_accuracy REAL DEFAULT 0.5,
                stat_regime_accuracy REAL DEFAULT 0.5,
                behavior_notes TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Database initialized: {self.db_path}")
    
    def save_snapshot(self, ticker: str, price: float, iv: float, 
                     contracts: List[Dict], expiration: str) -> Optional[int]:
        """
        Guardar snapshot de opciones
        
        Args:
            ticker: Símbolo (SPY, NVDA, etc)
            price: Precio subyacente
            iv: Volatilidad implícita promedio
            contracts: Lista de contratos [{'strike': X, 'type': 'call', 'iv': X, ...}]
            expiration: Fecha de expiración (YYYY-MM-DD)
        
        Returns:
            snapshot_id o None si falla
        """
        if not contracts:
            logger.warning(f"⚠️ No contracts for {ticker} on {expiration}")
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Calcular put/call ratio
            total_put_oi = sum(ct['oi'] for ct in contracts if ct.get('type') == 'put')
            total_call_oi = sum(ct['oi'] for ct in contracts if ct.get('type') == 'call')
            pcr = total_put_oi / max(total_call_oi, 1)
            
            # Insertar snapshot
            now = datetime.now().isoformat()
            c.execute('''
                INSERT INTO snapshots (ticker, timestamp, underlying_price, underlying_iv, put_call_ratio)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticker, now, price, iv, pcr))
            
            snapshot_id = c.lastrowid
            
            # Insertar contratos
            for contract in contracts:
                try:
                    c.execute('''
                        INSERT INTO contracts 
                        (snapshot_id, strike, type, iv, oi, volume, delta, gamma, theta, vega, bid, ask, expiration)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        snapshot_id,
                        contract.get('strike'),
                        contract.get('type'),
                        contract.get('iv', 0),
                        contract.get('oi', 0),
                        contract.get('volume', 0),
                        contract.get('delta', 0),
                        contract.get('gamma', 0),
                        contract.get('theta', 0),
                        contract.get('vega', 0),
                        contract.get('bid', 0),
                        contract.get('ask', 0),
                        expiration
                    ))
                except sqlite3.IntegrityError:
                    # Contract ya existe, ignorar
                    pass
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Snapshot saved: {ticker} @ ${price:.2f} ({len(contracts)} contracts)")
            return snapshot_id
            
        except Exception as e:
            logger.error(f"❌ Error saving snapshot: {e}")
            return None
    
    def get_latest_snapshot(self, ticker: str) -> Optional[Dict]:
        """Obtener el snapshot más reciente de un ticker"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, timestamp, underlying_price, underlying_iv, put_call_ratio
            FROM snapshots
            WHERE ticker = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (ticker,))
        
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'timestamp': row[1],
            'price': row[2],
            'iv': row[3],
            'pcr': row[4]
        }
    
    def get_contracts(self, snapshot_id: int) -> List[Dict]:
        """Obtener todos los contratos de un snapshot"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT strike, type, iv, oi, volume, delta, gamma, theta, vega, bid, ask, expiration
            FROM contracts
            WHERE snapshot_id = ?
            ORDER BY strike
        ''', (snapshot_id,))
        
        contracts = [
            {
                'strike': r[0],
                'type': r[1],
                'iv': r[2],
                'oi': r[3],
                'volume': r[4],
                'delta': r[5],
                'gamma': r[6],
                'theta': r[7],
                'vega': r[8],
                'bid': r[9],
                'ask': r[10],
                'expiration': r[11]
            }
            for r in c.fetchall()
        ]
        
        conn.close()
        return contracts
    
    def cleanup_old_snapshots(self, days: int = 30):
        """Eliminar snapshots más antiguos que N días"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Obtener IDs a borrar
        c.execute('SELECT id FROM snapshots WHERE timestamp < ?', (cutoff,))
        old_ids = [r[0] for r in c.fetchall()]
        
        if old_ids:
            # Borrar contratos y niveles relacionados
            for snap_id in old_ids:
                c.execute('DELETE FROM contracts WHERE snapshot_id = ?', (snap_id,))
                c.execute('DELETE FROM computed_levels WHERE snapshot_id = ?', (snap_id,))
            
            c.execute('DELETE FROM snapshots WHERE timestamp < ?', (cutoff,))
            conn.commit()
            logger.info(f"✅ Cleaned up {len(old_ids)} old snapshots")
        
        conn.close()


if __name__ == "__main__":
    # Test
    ing = DataIngestion()
    logger.info("✅ Data ingestion module ready")
