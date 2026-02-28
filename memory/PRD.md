# Fractal Multi-Asset Platform PRD

## Original Problem Statement
Развернуть код из GitHub для работы с фракталами валютных пар. Модули: BTC Fractal, SPX, DXY Macro Engine V2. Walk-Forward Simulation, Quantile Forecast, Brain Decision Layer, Cross-Asset Classifier, Brain Compare + Simulation. Добавить P12 - Adaptive Coefficient Learning для институционального аудита.

## Architecture
- **Backend**: TypeScript (Fastify) 8002 + Python proxy 8001
- **Frontend**: React 3000 | **Database**: MongoDB (fractal_db)
- **External APIs**: FRED API (key: 2c0bf55cfd182a3a4d2e4fd017a622f7)

## Brain v2.1 Full Pipeline
```
WorldState + CrossAsset → Quantile Forecast (MoE) → Scenario Engine → Risk Engine → Directives → EngineGlobal
                                                                     ↕
                                                         Brain Compare (ON vs OFF)
                                                         Brain Simulation (Walk-Forward)
                                                         Stress Simulation + Crash-Test
                                                         Adaptive Coefficient Learning (P12)
```

## Implemented Features (2026-02-28)

| Phase | Feature | Status | Tests |
|-------|---------|--------|-------|
| P8.0-A | Feature Builder (53 features) | ✅ | — |
| P8.0-B1 | Forecast endpoint (baseline) | ✅ | 23/23 |
| P8.0-B2 | Train endpoint (MoE) | ✅ | 23/23 |
| P8.0-C | Brain Decision Rules | ✅ | 25/25 |
| P9.0 | Cross-Asset Regime Classifier | ✅ | 20/20 |
| P9.1 | Brain ON vs OFF Compare | ✅ | 22/22 |
| P9.2 | Walk-Forward Simulation | ✅ | 22/22 |
| P10 | Stress Simulation Mode | ✅ | — |
| P10.1 | Regime Memory State | ✅ | — |
| P10.2 | MetaRisk Scale | ✅ | — |
| P10.3 | Brain/Engine Integration | ✅ | — |
| P11 | Capital Allocation Optimizer | ✅ | — |
| P12 | **Adaptive Coefficient Learning** | ✅ NEW | PRODUCTION Grade |

## P12 — Adaptive Coefficient Learning (IMPLEMENTED 2026-02-28)

### Philosophy
- NOT ML blackbox — rolling recalibration of weights
- Grid search with smoothing (alpha=0.35)
- Strict acceptance gates
- Never touch: guard dominance, shrink logic, TAIL risk-down

### Parameter Groups
| Group | Description | Tunable |
|-------|-------------|---------|
| brain_rules | Brain Quantile thresholds | No (too sensitive) |
| optimizer | Optimizer coefficients (K, wReturn, wTail, wCorr, wGuard) | Yes |
| metarisk | MetaRisk mapping (durationScale, stabilityScale, flipPenalty, crossAdj) | Yes |

### Acceptance Gates
- avgDeltaHitRatePp >= 2
- minDeltaPp >= -1
- flipRatePerYear <= 6
- maxOverrideIntensity <= cap (0.35 BASE, 0.60 TAIL)
- determinism = true
- noLookahead = true

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/brain/v2/adaptive/params | GET | Current params |
| /api/brain/v2/adaptive/schema | GET | Schema docs |
| /api/brain/v2/adaptive/run | POST | Start tuning run |
| /api/brain/v2/adaptive/status | GET | Get run status/report |
| /api/brain/v2/adaptive/history | GET | Params history |
| /api/brain/v2/adaptive/promote | POST | Promote params to active |

### P12 Fix: Override Intensity Breakdown
Engine Global response now includes:
```json
{
  "brain": {
    "overrideIntensity": {
      "brain": 0.0,
      "optimizer": 0.08,
      "total": 0.08,
      "cap": 0.6,
      "withinCap": true
    },
    "adaptive": {
      "mode": "off|shadow|on",
      "versionId": "default_dxy_v1",
      "asset": "dxy",
      "source": "default|tuned|promoted",
      "deltasApplied": { "brain":..., "optimizer":..., "metarisk":... }
    }
  }
}
```

### P12 Fix: Compare Endpoint
Brain Compare now includes:
- `optimizerDelta` - deltas from optimizer
- `optimizerDeltaAbs` - max absolute delta
- `overrideIntensity` - breakdown brain/optimizer/total

## All API Endpoints

### Engine Global
| Endpoint | Method | Status |
|----------|--------|--------|
| /api/engine/global | GET | Working |
| /api/engine/global?brain=1&optimizer=1 | GET | Working (with P12 adaptive section) |

### Brain Core
| Endpoint | Method | Status |
|----------|--------|--------|
| /api/brain/v2/decision | GET | Working |
| /api/brain/v2/compare | GET | Working (with optimizerDeltaAbs) |
| /api/brain/v2/adaptive/* | GET/POST | Working (P12) |

## Frontend Routes
| Route | Terminal | Status |
|-------|----------|--------|
| / | BTC Fractal | ✅ |
| /spx | SPX Terminal | ✅ |
| /dxy | DXY Fractal | ✅ |
| /admin | Admin Panel | ✅ |
| /engine/compare | Compare Dashboard | ✅ |

## Test Results (2026-02-28)
- Backend: 100% - All P12 Adaptive APIs working perfectly
- Frontend: 95% - All routes accessible, minor icon import warnings

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] P12 Adaptive Coefficient Learning
- [x] Override intensity breakdown (brain/optimizer/total)
- [x] Adaptive section in Engine Global response

### P1 (High) - NEXT
- [ ] P13: Portfolio Return Backtest (реальные SPX/BTC returns + transaction costs)
- [ ] UI for adaptive tuning controls

### P2 (Medium)
- [ ] Telegram/Slack alerts for production
- [ ] Daily cron for divergence checks

---
Last Updated: 2026-02-28
