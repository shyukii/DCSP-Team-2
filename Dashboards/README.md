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
git clone <REPO_URL> Dashboards
cd Dashboards
npm init -y
npm install
# First install main dependencies
npm install @supabase/supabase-js@^2.52.0 chart.js@^4.5.0 daisyui@^4.6.0 vue@^3.5.17 vue-chartjs@^5.3.2
# Then instal dev dependencies
npm install --save-dev @types/node@^24.0.15 @vitejs/plugin-vue@^4.6.2 @vue/eslint-config-typescript@^14.6.0 \
autoprefixer@^10.4.21 eslint@^9.31.0 eslint-plugin-vue@^10.3.0 postcss@^8.5.6 prettier@^3.6.2 \
tailwindcss@^3.4.17 typescript@^5.8.3 vite@^5.4.19 vue-tsc@^1.8.11

npm run dev                   # to run. to check, look at local host link given