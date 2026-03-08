# Contributing to SentinelOps 🛡️

Hey! Thanks for being interested in helping out with SentinelOps. I built this to make DevOps smarter and more proactive, and I'd love to have more devs involved.

## 🏗️ Architecture Overview

SentinelOps is built with a decoupled architecture to ensure scalability:

- **Backend (FastAPI)**: Handles the high-frequency webhook traffic and serves the API.
- **Workers (Celery)**: Process heavy AI analysis and ML training out-of-band.
- **Frontend (Next.js 14)**: provides a real-time, high-performance dashboard for decision intelligence.

## 🚀 How to Contribute

### 1. Setting Up for Development

The easiest way to get started is by using the provided `Makefile`:

```bash
make setup
```

This ensures all environment variables, virtual environments, and dependencies are correctly configured.

### 2. Development Workflow

- **Branching**: Create a new branch for every feature or bug fix: `git checkout -b feature/your-feature-name`.
- **Linting & Formatting**: We enforce strict linting. Before committing, run:
  ```bash
  make format  # Auto-formats Python (Black/Isort) and JS/TS (Prettier)
  make lint    # Checks for errors
  ```
- **Testing**: Ensure your changes don't break existing functionality:
  ```bash
  make test
  ```

### 3. Adding New AI Analysis Rules

... (rest of the sections remain same or slightly refined)

If you want to improve the `RiskAnalyzer` or `SimulationEngine`:

1. Navigate to `sentinelops-backend/app/services/risk_analyzer.py`.
2. For predictive simulations, check `app/services/simulation_service.py`.
3. If it's a new metric, ensure you update the Pydantic schemas in `app/schemas/pull_request.py`.

### 3. Training the ML Model

We use a Logistic Regression model for PR risk scoring. To enhance the model:

1. Update the feature extraction in `sentinelops-backend/app/ml/train.py`.
2. Run the training script: `docker-compose exec api python -m app.ml.train`.
3. Update `app/ml/metadata.json` with your new performance metrics.

### 4. Frontend UI Components

We use **Tailwind CSS**, **Framer Motion**, and **Lucide React**.

- Reusable UI elements live in `sentinelops-frontend/components/ui`.
- High-level visualizations like the `RiskHeatmap` live in `components/dashboard`.
- Page-specific logic should be kept in the `app/` directory (App Router).
- Use `zustand` for any global state (like the Toast system).

## 🧪 Testing Guidelines

Before submitting a PR, please ensure:

- **Backend**: All tests pass (`pytest`).
- **Frontend**: Linting passes (`npm run lint`) and the build is successful (`npm run build`).

## 📜 Code of Conduct

Please be respectful and professional in all interactions. We aim to build a welcoming environment for all engineers.

## 🗺️ Roadmap Compatibility

Check our roadmap in [README.md](./README.md#roadmap) to see where we're headed. If your feature fits the vision, we'd love to see it!
