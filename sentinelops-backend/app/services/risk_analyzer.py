"""
PR Risk Analysis Engine - My logic for scoring pull requests.
Author: Arsh Verma
"""
from typing import Any, Dict, List
import re

class RiskAnalyzer:
    """The main engine for scoring PR risk using static analysis."""
    
    # Risk weights (sum to 1.0)
    WEIGHTS = {
        "lines_changed": 0.25,
        "file_type_risk": 0.20,
        "author_history": 0.25,
        "dependency_changes": 0.20,
        "complexity_delta": 0.10,
    }
    
    HIGH_RISK_FILE_TYPES = {".json", ".yaml", ".yml", ".toml", ".env", ".tf", ".dockerfile"}
    LOW_RISK_FILE_TYPES = {".md", ".txt", ".rst"}
    
    def analyze_pr(self, pr_data: Dict[str, Any], author_history: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scoring logic for PRs. Takes in PR data and author history to produce a 0-1 risk score.
        """
        
        # 1. Lines changed score
        total_lines = pr_data.get("lines_added", 0) + pr_data.get("lines_deleted", 0)
        lines_score = min(total_lines / 1000, 1.0)  # Normalize to 1000 lines = max risk
        
        # 2. File type risk
        file_types = set(pr_data.get("file_types", []))
        high_risk_overlap = file_types & self.HIGH_RISK_FILE_TYPES
        low_risk_overlap = file_types & self.LOW_RISK_FILE_TYPES
        file_type_score = (
            len(high_risk_overlap) * 0.3 +
            (0.2 if pr_data.get("has_config_changes") else 0) +
            (0.2 if pr_data.get("has_dependency_changes") else 0) +
            (-0.1 if pr_data.get("has_test_changes") else 0)  # Tests reduce risk
        )
        file_type_score = max(0.0, min(1.0, file_type_score))
        
        # 3. Author history score
        total = author_history.get("total_prs", 0)
        failed = author_history.get("failed_prs", 0)
        author_score = (failed / total) if total > 0 else 0.3  # Unknown author = 30% baseline
        
        # 4. Dependency changes
        dependency_score = 1.0 if pr_data.get("has_dependency_changes") else 0.0
        
        # 5. Complexity delta
        # Simulated complexity delta via radon (mapped to 0.0 - 1.0)
        complexity_delta = pr_data.get("complexity_delta", 0.0)
        # Assume 10.0 delta is max risk
        complexity_score = min(max(complexity_delta / 10.0, 0.0), 1.0)
        
        # Weighted sum matching 01_SYSTEM_ARCHITECTURE.md formula
        risk_probability = (
            self.WEIGHTS["lines_changed"] * lines_score +
            self.WEIGHTS["file_type_risk"] * file_type_score +
            self.WEIGHTS["author_history"] * author_score +
            self.WEIGHTS["dependency_changes"] * dependency_score +
            self.WEIGHTS["complexity_delta"] * complexity_score
        )
        
        risk_probability = round(min(max(risk_probability, 0.0), 1.0), 3)
        
        # Risk level classification
        if risk_probability < 0.35:
            risk_level = "safe"
        elif risk_probability < 0.65:
            risk_level = "caution"
        else:
            risk_level = "high"
        
        # Risk factors (human readable)
        risk_factors = []
        if lines_score > 0.5:
            risk_factors.append(f"Large change: {total_lines} lines modified")
        if high_risk_overlap:
            risk_factors.append(f"High-risk file types: {', '.join(high_risk_overlap)}")
        if pr_data.get("has_dependency_changes"):
            risk_factors.append("Dependency file changes detected")
        if author_score > 0.4:
            risk_factors.append(f"Author has {int(author_score * 100)}% historical failure rate")
        if complexity_score > 0.5:
            risk_factors.append(f"High code complexity delta detected (+{complexity_delta:.1f})")
        
        # Risk drivers for explainability (magnitude of contribution)
        risk_drivers = [
            {"feature": "Lines Changed (+)", "impact": round(self.WEIGHTS["lines_changed"] * lines_score, 2)},
            {"feature": "High-Risk Files (+)", "impact": round(self.WEIGHTS["file_type_risk"] * file_type_score, 2)},
            {"feature": "Author History (+)", "impact": round(self.WEIGHTS["author_history"] * author_score, 2)},
            {"feature": "Dependencies (+)", "impact": round(self.WEIGHTS["dependency_changes"] * dependency_score, 2)},
            {"feature": "Complexity (+)", "impact": round(self.WEIGHTS["complexity_delta"] * complexity_score, 2)},
        ]
        # Sort by impact
        risk_drivers.sort(key=lambda x: x["impact"], reverse=True)

        return {
            "risk_probability": risk_probability,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "risk_drivers": risk_drivers,
            "component_scores": {
                "lines": lines_score,
                "file_types": file_type_score,
                "author_history": author_score,
                "dependencies": dependency_score,
                "complexity": complexity_score,
            }
        }
