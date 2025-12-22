#!/usr/bin/env python3
"""
MM SCANNER UI - Tab 8 Refactored
Integración completa del sistema institucional
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
import logging

# MM System imports
from mm_data_ingestion import DataIngestion
from mm_quant_engine import QuantEngine
from mm_ai_layer import AILayer
from mm_memory import MemorySystem
from mm_orchestrator import MMSystemOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MMScannerUI:
    """
    Refactored Tab 8 - Institutional MM Analysis
    """
    
    def __init__(self):
        self.orchestrator = MMSystemOrchestrator()
        self.memory = MemorySystem()
        self.ingestion = DataIngestion()
        self.quant = QuantEngine()
    
    def render_tab(self):
        """Renderizar Tab 8 completo"""
        
        st.markdown("# 📊 MARKET MAKER SCANNER - Institutional Edition")
        st.markdown("---")
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 1: INPUT
        # ═════════════════════════════════════════════════════════════════
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ticker = st.selectbox(
                "🎯 Select Ticker",
                ["SPY", "QQQ", "NVDA", "TSLA"],
                help="Universe of institutional interest"
            )
        
        with col2:
            expiration = st.selectbox(
                "📅 Expiration",
                ["2024-12-20", "2025-01-17", "2025-02-21"]
            )
        
        with col3:
            refresh = st.button("🔄 Analyze Now", use_container_width=True)
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 2: LIVE DATA (simulado con Tradier API)
        # ═════════════════════════════════════════════════════════════════
        if refresh:
            st.info("📡 Fetching market data...")
            
            try:
                # AQUÍ IRÍA: 
                # contracts = fetch_tradier_api(ticker, expiration)
                # prices = fetch_fmp_api(ticker)
                # news = fetch_news_api(ticker)
                
                # Por ahora simulado:
                contracts = self._mock_contracts(ticker)
                price = self._mock_price(ticker)
                iv = 0.25 + (0.05 if ticker == "TSLA" else 0)
                
                # ═════════════════════════════════════════════════════════════════
                # ANÁLISIS
                # ═════════════════════════════════════════════════════════════════
                
                # 1. INGESTION
                snapshot_id = self.ingestion.save_snapshot(
                    ticker, price, iv, contracts, expiration
                )
                stored_contracts = self.ingestion.get_contracts(snapshot_id)
                
                # 2. QUANT ENGINE
                st.markdown("### ⚙️ Quantitative Analysis")
                
                # GEX
                gex = self.quant.calculate_gex(stored_contracts, price)
                gamma_neta = sum(gex.values())
                
                col_gex1, col_gex2, col_gex3 = st.columns(3)
                with col_gex1:
                    st.metric("Gamma Net", f"{gamma_neta:.2e}", 
                             "MR" if gamma_neta > 0 else "TREND")
                with col_gex2:
                    st.metric("Price", f"${price:.2f}", "IV", f"{iv:.1%}")
                with col_gex3:
                    st.metric("Put/Call OI", f"{self._calc_pcr(stored_contracts):.2f}", "ratio")
                
                # WALLS
                st.markdown("### 🧱 Gamma Walls Detection")
                call_wall, put_wall = self.quant.detect_walls(stored_contracts, price, expiration)
                
                walls_df = pd.DataFrame({
                    'Type': ['CALL WALL', 'PUT WALL'],
                    'Strike': [f"${call_wall.strike:.2f}", f"${put_wall.strike:.2f}"],
                    'Open Interest': [f"{call_wall.oi:,}", f"{put_wall.oi:,}"],
                    'Distance': [f"{call_wall.distance_pct:.1%}", f"{put_wall.distance_pct:.1%}"],
                    'Strength': [call_wall.strength, put_wall.strength]
                })
                
                st.dataframe(walls_df, use_container_width=True)
                
                # REGIME
                st.markdown("### 📈 Market Regime")
                regime = self.quant.classify_regime(stored_contracts, price, 
                                                   historical_prices=None, 
                                                   gamma_neta=gamma_neta)
                
                col_regime1, col_regime2, col_regime3 = st.columns(3)
                with col_regime1:
                    emoji = "🔄" if regime.classification == "CHOP" else ("📊" if regime.classification == "TREND" else "⏸️")
                    st.metric(f"{emoji} Regime", regime.classification, f"{regime.confidence:.0%}")
                with col_regime2:
                    st.metric("Pinning Prob", f"{regime.pin_probability:.1%}", "likelihood")
                with col_regime3:
                    st.metric("Vol Risk", regime.vol_risk, "status")
                
                # SCENARIOS
                st.markdown("### 🎯 Target Scenarios")
                atr = price * 0.02  # simplified
                targets = self.quant.calculate_targets(call_wall, put_wall, price, atr)
                
                scenarios_data = []
                for i, (scenario, data) in enumerate(targets.items(), 1):
                    scenarios_data.append({
                        'Scenario': f"Target {scenario}",
                        'Price': f"${data.get('target', 0):.2f}",
                        'Probability': f"{data.get('probability', 0):.0%}",
                        'Type': data.get('type', 'N/A'),
                        'Invalidation': f"${data.get('invalidation', 0):.2f}"
                    })
                
                st.dataframe(pd.DataFrame(scenarios_data), use_container_width=True)
                
                # TICKER PROFILE (from Memory)
                st.markdown("### 📊 Ticker Profile (Historical)")
                profile = self.memory.get_ticker_profile(ticker)
                
                col_prof1, col_prof2, col_prof3, col_prof4 = st.columns(4)
                with col_prof1:
                    st.metric("Pinning Hit %", f"{profile['pin_hit_rate']:.1%}", 
                             f"({profile['sample_size']} samples)")
                with col_prof2:
                    st.metric("Wall Respect %", f"{profile['wall_respect_rate']:.1%}",
                             "historical")
                with col_prof3:
                    st.metric("Vol Expansion", f"{profile['vol_expansion_freq']:.1%}",
                             "frequency")
                with col_prof4:
                    st.metric("Confidence", f"{profile['confidence']:.0%}",
                             "data quality")
                
                # AI LAYER - MM BRIEF
                st.markdown("### 📝 Market Maker Brief")
                
                brief = self.orchestrator.analyze_ticker(
                    ticker=ticker,
                    contracts=contracts,
                    price=price,
                    iv=iv,
                    expiration=expiration,
                    ticker_profile=profile
                )
                
                st.markdown(brief)
                
                # BACKTESTING METRICS
                st.markdown("### 📉 Backtesting Summary")
                summary = self.memory.get_backtesting_summary(ticker, days=30)
                
                col_bt1, col_bt2, col_bt3 = st.columns(3)
                with col_bt1:
                    st.metric("Outcomes Tracked", summary['total_outcomes'])
                with col_bt2:
                    st.metric("Hit Rate", f"{summary['hit_rate']:.1f}%")
                with col_bt3:
                    st.metric("Avg Move", f"{summary['avg_price_move']:.2f}%")
                
                # LEARNING INSIGHTS
                worst = self.memory.get_worst_predictions(limit=3)
                if worst:
                    st.markdown("### ⚠️ Recent Misses (Learning)")
                    with st.expander(f"Last 3 incorrect predictions for {ticker}"):
                        for miss in worst:
                            st.warning(f"❌ {miss['ticker']} | Regime: {miss['regime']} | Move: {miss['price_move']:.1f}%")
                
                # RECOMMENDATIONS
                st.markdown("### 💡 Weight Adjustments (AI Learning)")
                recommendations = self.memory.recommend_weight_adjustment(ticker)
                
                for param, weight in recommendations['adjustments'].items():
                    st.info(f"📌 {param}: {weight}")
                
                st.success(f"✅ Analysis complete for {ticker} | {expiration}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Tab 8 error: {e}", exc_info=True)
        
        # ═════════════════════════════════════════════════════════════════
        # SECCIÓN 3: DOCUMENTATION
        # ═════════════════════════════════════════════════════════════════
        st.markdown("---")
        with st.expander("📚 System Documentation"):
            st.markdown("""
            ### How This Works:
            
            1. **Data Ingestion**: Fetches live options chains from Tradier API
            2. **Quant Engine**: Calculates GEX, detects walls, classifies regime
            3. **Pinning Score**: Probability of price pinning at walls
            4. **Scenarios**: 3 target scenarios (bullish/bearish/mean-reversion)
            5. **Memory**: Tracks accuracy by ticker and learns patterns
            
            ### Metrics Explained:
            - **GEX**: Gamma Exposure (>0 = mean reversion, <0 = trend risk)
            - **Walls**: High OI concentrations that act as support/resistance
            - **Regime**: CHOP (ranging), TREND (moving), SQUEEZE (vol compression)
            - **Pinning Score**: Probability of price sticking to wall at expiration
            - **Historical Profile**: Hit rates learned from backtesting
            """)
        
        st.markdown("---")
        st.caption("MM Scanner v1.0 | Institutional Edition | Real-time Gamma + Vol Analysis")
    
    # ═════════════════════════════════════════════════════════════════
    # HELPER FUNCTIONS
    # ═════════════════════════════════════════════════════════════════
    
    def _mock_contracts(self, ticker: str) -> List[Dict]:
        """Simular contratos para demostración"""
        import random
        
        base_price = {"SPY": 590, "QQQ": 520, "NVDA": 140, "TSLA": 280}[ticker]
        
        contracts = []
        for strike in range(int(base_price) - 20, int(base_price) + 20, 1):
            for opt_type in ['call', 'put']:
                contracts.append({
                    'strike': float(strike),
                    'type': opt_type,
                    'oi': random.randint(5000, 50000),
                    'volume': random.randint(100, 5000),
                    'bid': random.uniform(0.1, 5.0),
                    'ask': random.uniform(0.1, 5.0),
                    'delta': random.uniform(-1, 1),
                    'gamma': random.uniform(0.001, 0.1),
                    'theta': random.uniform(-0.5, 0.1),
                    'vega': random.uniform(0, 2),
                    'iv': random.uniform(0.2, 0.4)
                })
        
        return contracts
    
    def _mock_price(self, ticker: str) -> float:
        """Simular precios"""
        prices = {"SPY": 590.45, "QQQ": 520.30, "NVDA": 140.25, "TSLA": 285.15}
        return prices[ticker]
    
    def _calc_pcr(self, contracts: List[Dict]) -> float:
        """Calculate Put/Call Ratio"""
        total_put_oi = sum(c.get('oi', 0) for c in contracts if c.get('type', '').lower() == 'put')
        total_call_oi = sum(c.get('oi', 0) for c in contracts if c.get('type', '').lower() == 'call')
        return total_put_oi / max(total_call_oi, 1)


def render_mm_scanner_tab(tab):
    """Función para integrar en app.py"""
    with tab:
        ui = MMScannerUI()
        ui.render_tab()


if __name__ == "__main__":
    # Para testing local
    st.set_page_config(page_title="MM Scanner", layout="wide")
    ui = MMScannerUI()
    ui.render_tab()
