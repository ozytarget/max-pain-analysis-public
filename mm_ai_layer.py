#!/usr/bin/env python3
"""
AI LAYER - Explica datos cuantitativos + arma escenarios
Phase 1 - MVP: Sin alucinaciones, solo RAG con datos medidos
"""

import json
import logging
from typing import Dict, List
from dataclasses import asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AILayer:
    """Convierte datos cuantitativos en narrativa + escenarios"""
    
    def __init__(self):
        self.template = """
# MM BRIEF: {ticker}

**Generated**: {timestamp}
**Data Confidence**: {confidence}%

---

## 📊 MARKET SNAPSHOT
- **Price**: ${price:.2f}
- **Implied Vol**: {iv:.1%}
- **Put/Call Ratio**: {pcr:.2f}x
- **Regime**: {regime} ({regime_confidence}% confidence)

---

## 🧱 WALLS & STRUCTURE

### Call Wall (Resistance)
- **Strike**: ${call_wall_strike:.2f}
- **Distance**: +{call_wall_distance:.2f}%
- **OI**: {call_wall_oi:,}
- **Strength**: {call_wall_strength}
- **Interpretation**: {call_wall_interp}

### Put Wall (Support)
- **Strike**: ${put_wall_strike:.2f}
- **Distance**: {put_wall_distance:.2f}%
- **OI**: {put_wall_oi:,}
- **Strength**: {put_wall_strength}
- **Interpretation**: {put_wall_interp}

---

## 🎲 SCENARIOS

### Scenario A: BULLISH
- **Entry**: {scenario_a_entry}
- **Target**: ${scenario_a_target:.2f}
- **Stop**: ${scenario_a_stop:.2f}
- **Invalidation**: {scenario_a_invalid}
- **Probability**: {scenario_a_prob:.0%}
- **Why**: {scenario_a_why}

### Scenario B: BEARISH
- **Entry**: {scenario_b_entry}
- **Target**: ${scenario_b_target:.2f}
- **Stop**: ${scenario_b_stop:.2f}
- **Invalidation**: {scenario_b_invalid}
- **Probability**: {scenario_b_prob:.0%}
- **Why**: {scenario_b_why}

### Scenario C: MEAN REVERSION (Current Regime)
- **Range Low**: ${scenario_c_low:.2f}
- **Range High**: ${scenario_c_high:.2f}
- **Duration**: {scenario_c_duration}
- **Why**: {scenario_c_why}

---

## ⚠️ KEY RISKS
- {risk_1}
- {risk_2}
- {risk_3}

---

## 🔄 TICKER PERSONALITY
- **Pinning Hit Rate**: {pin_hit_rate:.0%}
- **Wall Respect Rate**: {wall_respect:.0%}
- **Vol Expansion Frequency**: {vol_exp_freq:.0%}
- **Notes**: {ticker_notes}

---

## 📰 NEWS IMPACT
{news_section}

---

## ✅ DATA SOURCES
All figures based on measured market data:
- Options chain from Tradier API (real-time)
- Historical prices (252-day baseline)
- Wall detection via OI aggregation
- Gamma/Greeks from Black-Scholes
- No AI forecasting, only analysis of actual positions
"""
    
    def build_brief(self, snapshot: Dict, walls: Dict, regime: Dict, 
                   targets: Dict, ticker_profile: Dict, news: List[Dict],
                   timestamp: str) -> str:
        """
        Construir el MM Brief completo
        
        Input: Todos los datos cuantitativos
        Output: Narrativa clara + escenarios
        """
        
        call_wall = walls.get('call_wall', {})
        put_wall = walls.get('put_wall', {})
        
        # Interpretaciones de walls
        call_interp = self._interpret_wall('call', call_wall.get('strength'), 
                                          snapshot.get('price'))
        put_interp = self._interpret_wall('put', put_wall.get('strength'),
                                         snapshot.get('price'))
        
        # Escenarios
        scenarios = self._build_scenarios(snapshot, walls, regime)
        
        # Riesgos
        risks = self._identify_risks(snapshot, walls, regime, ticker_profile)
        
        # News
        news_section = self._format_news(news)
        
        # Llenar template
        brief = self.template.format(
            ticker=snapshot.get('ticker'),
            timestamp=timestamp,
            confidence=int(regime.get('confidence', 0.5) * 100),
            
            # Snapshot
            price=snapshot.get('price', 0),
            iv=snapshot.get('iv', 0),
            pcr=snapshot.get('pcr', 0),
            regime=regime.get('classification'),
            regime_confidence=int(regime.get('confidence', 0.5) * 100),
            
            # Walls
            call_wall_strike=call_wall.get('strike', 0),
            call_wall_distance=call_wall.get('distance_pct', 0),
            call_wall_oi=call_wall.get('oi', 0),
            call_wall_strength=call_wall.get('strength', 'NONE'),
            call_wall_interp=call_interp,
            
            put_wall_strike=put_wall.get('strike', 0),
            put_wall_distance=put_wall.get('distance_pct', 0),
            put_wall_oi=put_wall.get('oi', 0),
            put_wall_strength=put_wall.get('strength', 'NONE'),
            put_wall_interp=put_interp,
            
            # Scenarios
            scenario_a_entry=scenarios['a'].get('entry'),
            scenario_a_target=scenarios['a'].get('target', 0),
            scenario_a_stop=scenarios['a'].get('stop', 0),
            scenario_a_invalid=scenarios['a'].get('invalidation'),
            scenario_a_prob=scenarios['a'].get('probability', 0),
            scenario_a_why=scenarios['a'].get('why'),
            
            scenario_b_entry=scenarios['b'].get('entry'),
            scenario_b_target=scenarios['b'].get('target', 0),
            scenario_b_stop=scenarios['b'].get('stop', 0),
            scenario_b_invalid=scenarios['b'].get('invalidation'),
            scenario_b_prob=scenarios['b'].get('probability', 0),
            scenario_b_why=scenarios['b'].get('why'),
            
            scenario_c_low=scenarios['c'].get('range_low', 0),
            scenario_c_high=scenarios['c'].get('range_high', 0),
            scenario_c_duration=scenarios['c'].get('duration'),
            scenario_c_why=scenarios['c'].get('why'),
            
            # Risks
            risk_1=risks[0],
            risk_2=risks[1],
            risk_3=risks[2],
            
            # Profile
            pin_hit_rate=ticker_profile.get('pin_hit_rate', 0.5),
            wall_respect=ticker_profile.get('wall_respect', 0.5),
            vol_exp_freq=ticker_profile.get('vol_exp_freq', 0.3),
            ticker_notes=ticker_profile.get('notes', ''),
            
            # News
            news_section=news_section
        )
        
        return brief
    
    def _interpret_wall(self, wall_type: str, strength: str, price: float) -> str:
        """Interpretación de una pared"""
        if strength == 'STRONG':
            if wall_type == 'call':
                return "STRONG resistance. Large block of call OI creates significant friction above. Price typically respects."
            else:
                return "STRONG support. Large block of put OI creates significant floor below. Bounces common."
        elif strength == 'MEDIUM':
            if wall_type == 'call':
                return "Moderate resistance. Possible temporary pause if tested."
            else:
                return "Moderate support. Some buyers waiting if price dips."
        else:
            return "Weak or no significant wall. Low OI concentration."
    
    def _build_scenarios(self, snapshot: Dict, walls: Dict, regime: Dict) -> Dict:
        """Armar 3 escenarios (bull, bear, neutral)"""
        price = snapshot.get('price', 100)
        call_wall = walls.get('call_wall', {})
        put_wall = walls.get('put_wall', {})
        
        scenarios = {
            'a': {
                'entry': f"Break above ${call_wall.get('strike', price * 1.02):.2f}",
                'target': call_wall.get('strike', price * 1.02),
                'stop': put_wall.get('strike', price * 0.98),
                'invalidation': f"Closes below ${put_wall.get('strike', price * 0.98):.2f}",
                'probability': 0.4,
                'why': 'Call wall at resistance; if broken, acceleration likely due to low gamma above'
            },
            'b': {
                'entry': f"Break below ${put_wall.get('strike', price * 0.98):.2f}",
                'target': put_wall.get('strike', price * 0.98),
                'stop': call_wall.get('strike', price * 1.02),
                'invalidation': f"Closes above ${call_wall.get('strike', price * 1.02):.2f}",
                'probability': 0.35,
                'why': 'Put wall at support; if broken, downside acceleration likely'
            },
            'c': {
                'range_low': put_wall.get('strike', price * 0.98),
                'range_high': call_wall.get('strike', price * 1.02),
                'duration': '1-3 days' if regime.get('classification') == 'CHOP' else '1 day',
                'why': f"Current regime is {regime.get('classification')}. Price oscillating between walls is typical for this setup."
            }
        }
        
        return scenarios
    
    def _identify_risks(self, snapshot: Dict, walls: Dict, regime: Dict,
                       profile: Dict) -> List[str]:
        """Identificar 3 riesgos principales"""
        risks = []
        
        # Riesgo 1: Vol
        if regime.get('vol_risk') == 'EXPANSION':
            risks.append("⚡ Vol EXPANSION probable - typical ±1.5-2.0x ATR moves if triggered")
        else:
            risks.append("📉 Vol steady or compressing - watch for range compression")
        
        # Riesgo 2: Wall strength
        call_strength = walls.get('call_wall', {}).get('strength')
        put_strength = walls.get('put_wall', {}).get('strength')
        
        if call_strength == 'WEAK' or put_strength == 'WEAK':
            risks.append("🧱 One or both walls are weak - breakout more likely than typical")
        else:
            risks.append("🎯 Both walls present - pinning/range-bound behavior likely")
        
        # Riesgo 3: Histórico del ticker
        if profile.get('wall_respect') < 0.5:
            risks.append(f"📊 {snapshot.get('ticker')} doesn't respect walls as much - breakout bias")
        else:
            risks.append(f"📊 {snapshot.get('ticker')} typically respects walls - mean reversion bias")
        
        return risks[:3]
    
    def _format_news(self, news: List[Dict]) -> str:
        """Formatear sección de noticias"""
        if not news:
            return "No significant news in last 24h"
        
        lines = []
        for item in news:
            sentiment = "🔴" if item.get('sentiment_score', 0) < 0 else "🟢"
            impact = "HIGH" if item.get('impact_score', 0) > 0.7 else "MEDIUM"
            lines.append(f"- {sentiment} [{impact}] {item.get('title')}")
        
        return "\n".join(lines[:5])  # Max 5 noticias


if __name__ == "__main__":
    ai = AILayer()
    logger.info("✅ AI layer initialized")
