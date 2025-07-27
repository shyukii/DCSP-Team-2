# 🌱 Compost Analytics Dashboard

A Vue 3 + Vite + TailwindCSS + DaisyUI dashboard for real‑time compost sensor analytics (moisture, CO₂, etc.) powered by Supabase.

---

## ✨ Features (Current)
- Vue 3 + `<script setup>` + TypeScript
- TailwindCSS + DaisyUI component styling
- Summary metric cards (Avg Moisture, Avg CO₂, Forecast, Status)
- Moisture line chart (Chart.js + vue-chartjs)
- Naive linear forecast (to be improved)
- Status tagging via moisture thresholds
- Modular composables (`useReadings`, `useMetrics`, `useForecast`)

## 🛣 Planned / Roadmap
| Status | Feature |
|--------|---------|
| 🔜 | Realtime subscription (auto append new readings) |
| 🔜 | Time range & device filters |
| 🔜 | Improved forecast (EMA / Holt-Winters) |
| 🔜 | Additional metrics (Temperature, EC) |
| 🔜 | CSV export |
| ❔ | Auth (Supabase email / magic link) |
| ❔ | Dark / Light theme toggle |

---

## 🧱 Tech Stack
| Layer | Tools |
|-------|-------|
| UI | Vue 3, Vite, TypeScript |
| Styling | TailwindCSS, DaisyUI |
| Charts | Chart.js, vue-chartjs |
| Backend (BaaS) | Supabase (Postgres + Realtime) |
| Data Access | `@supabase/supabase-js` |
| Dev Quality | ESLint, Prettier, vue-tsc |

---
## Connection to Supabase Database
Create a tsconfig.json at the root and paste this code

{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["DOM", "ESNext"],
    "allowJs": false,
    "checkJs": false,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}


## 🚀 Quick Start

### 0. Install Node.js (LTS)

- **Required version:** Node.js **20.x LTS** (avoid Node 22 for now due to tooling issues).
- Download from: https://nodejs.org/en (choose the **LTS** installer).
- Verify after installation:

```bash
node -v
# v20.x.x expected
npm -v

```bash
cp .env.example .env # create and fill values
cd Dashboards
npm ci
npm run dev          # to run. to check, look at local host link given
ctrl c               # to stop running