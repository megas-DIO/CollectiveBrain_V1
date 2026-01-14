"""Deployment utilities for CollectiveBrain.

Provides a deployment plan and optional execution via Docker Compose.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DeploymentPlan:
    """Represents a deployment plan for a given mode."""

    mode: str
    compose_file: Path
    command: List[str]
    steps: List[str]


class DeploymentManager:
    """Builds and executes deployment plans using Docker Compose."""

    def __init__(self, compose_file: str = "docker-compose.yml") -> None:
        self.compose_file = Path(compose_file)

    def build_plan(self, mode: str = "basic") -> DeploymentPlan:
        """Build a deployment plan for the requested mode."""
        normalized_mode = mode.lower().strip()
        profile = "production" if normalized_mode == "production" else None

        base_command = ["docker", "compose"]
        if profile:
            base_command.extend(["--profile", profile])
        base_command.extend(["up", "-d", "--build"])

        steps = [
            "Validate Docker Compose configuration",
            "Ensure required environment variables are set",
            "Build and start services with Docker Compose",
        ]

        if profile:
            steps.insert(1, "Enable production services (Redis, Milvus, etcd, MinIO)")

        return DeploymentPlan(
            mode=normalized_mode,
            compose_file=self.compose_file,
            command=base_command,
            steps=steps,
        )

    def validate(self, mode: str = "basic", check_tools: bool = True) -> Dict[str, List[str]]:
        """Validate prerequisites for deployment."""
        issues: List[str] = []
        warnings: List[str] = []

        if not self.compose_file.exists():
            issues.append(f"Missing compose file: {self.compose_file}")

        if mode.lower().strip() == "production":
            if not os.getenv("GITHUB_TOKEN") and not os.getenv("OPENAI_API_KEY"):
                warnings.append(
                    "No LLM API key found (GITHUB_TOKEN or OPENAI_API_KEY)."
                )

        if check_tools and not shutil.which("docker"):
            issues.append("Docker CLI not found in PATH.")

        return {"issues": issues, "warnings": warnings}

    def deploy(
        self,
        mode: str = "basic",
        execute: bool = False,
    ) -> Dict[str, Optional[str]]:
        """Deploy using Docker Compose. Returns execution summary."""
        plan = self.build_plan(mode)
        validation = self.validate(mode, check_tools=execute)

        result: Dict[str, Optional[str]] = {
            "mode": plan.mode,
            "command": " ".join(plan.command),
            "executed": "no",
            "error": None,
        }

        if validation["issues"]:
            result["error"] = "; ".join(validation["issues"])
            return result

        if execute:
            subprocess.run(plan.command, check=True)
            result["executed"] = "yes"

        return result
