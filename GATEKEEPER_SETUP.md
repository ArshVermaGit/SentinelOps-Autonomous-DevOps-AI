# 🛡️ GitHub Gatekeeper Setup Guide

SentinelOps can act as a hard "Pass/Fail" gate for your repository. By following these steps, you can ensure that only PRs verified by the AI can be merged.

## 1. Configure Webhooks

Ensure your repository has a webhook pointing to your SentinelOps instance:

- **Payload URL**: `https://your-sentinel-ops.com/api/v1/webhooks/github`
- **Content type**: `application/json`
- **Events**: `Pull requests`, `Workflow runs`

## 2. Enable Branch Protection

To make the AI-gate mandatory:

1. Go to your repo **Settings** > **Branches**.
2. Click **Add branch protection rule** (or Edit an existing one).
3. Check **Require status checks to pass before merging**.
4. Search for and select `sentinel-ops/risk-gate`.
5. Click **Create** or **Save changes**.

## 3. How it Works

1. **Developer opens a PR**: SentinelOps immediately posts a `pending` status.
2. **AI Analysis**: Our worker analyzes the diff, complexity, and author history.
3. **Status Update**:
   - 🟢 **Safe/Caution**: Status becomes `success`. Merge is allowed.
   - 🔴 **High Risk**: Status becomes `failure`. Merge is **blocked**.
4. **Resolution**: If blocked, click **Details** to see the Risk Explainer on the dashboard and resolve the issues.

---

_Built by Arsh Verma — Secure Your Delivery Pipeline_
