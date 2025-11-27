"""Generic adapter for unknown/unclassified apps."""
from typing import Dict, Any
from app.domain.apps.base import (
    BaseAppAdapter,
    ConnectedAppConfig,
    AppReadIntent,
    PlanStep,
    StepResult,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class UnknownAppAdapter:
    """
    Generic adapter for apps that are not yet classified or supported.
    Provides limited functionality - mainly read-only operations.
    """
    
    def read(self, intent: AppReadIntent, config: ConnectedAppConfig) -> Dict[str, Any]:
        """
        Read data from unknown app.
        Limited support - returns error message.
        """
        logger.warning(
            f"Attempted to read from unknown app: {config.app_id} "
            f"with intent: {intent.kind}"
        )
        return {
            "error": f"App '{config.name}' ({config.app_id}) is not yet fully supported. "
                     "Only read operations may be available.",
            "data": [],
        }
    
    def execute_step(
        self,
        step: PlanStep,
        config: ConnectedAppConfig
    ) -> StepResult:
        """
        Execute step on unknown app.
        Returns failure result - unknown apps should not execute operations.
        """
        logger.warning(
            f"Attempted to execute step on unknown app: {config.app_id} "
            f"action: {step.action}"
        )
        return StepResult(
            step_id=step.id,
            status="failed",
            message=f"App '{config.name}' ({config.app_id}) does not support execution operations. "
                    "Please use a supported app or configure the app properly.",
            raw={},
        )
    
    def supports_action(self, action: str) -> bool:
        """
        Unknown apps do not support any actions.
        """
        return False

