"""KiotViet adapter implementing BaseAppAdapter."""
from typing import Dict, Any
from app.domain.apps.base import (
    BaseAppAdapter,
    ConnectedAppConfig,
    AppReadIntent,
    PlanStep,
    StepResult,
    AppCategory,
)
from app.domain.apps.kiotviet.config import KiotVietConfig
from app.domain.apps.kiotviet.api_client import KiotVietApiClient
from app.domain.apps.kiotviet import mappers
from app.core.logging import get_logger

logger = get_logger(__name__)


class KiotVietAdapter:
    """
    Adapter for KiotViet POS system.
    Implements BaseAppAdapter interface.
    """
    
    def _build_client(self, config: ConnectedAppConfig) -> KiotVietApiClient:
        """
        Build KiotViet API client from ConnectedAppConfig.
        
        Args:
            config: Connected app configuration
            
        Returns:
            KiotVietApiClient instance
        """
        kv_config = KiotVietConfig.from_connected_app_config(config)
        return KiotVietApiClient(kv_config)
    
    def _run_async(self, coro):
        """
        Helper to run async code, handling both sync and async contexts.
        """
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to use a different approach
            # Create a new event loop in a thread
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        except RuntimeError:
            # No running loop, can use asyncio.run
            return asyncio.run(coro)
    
    def read(self, intent: AppReadIntent, config: ConnectedAppConfig) -> Dict[str, Any]:
        """
        Read data from KiotViet based on intent.
        
        Args:
            intent: Read intent (what to read)
            config: App configuration
            
        Returns:
            Dictionary with read data
        """
        client = self._build_client(config)
        
        try:
            # Dispatch based on intent kind
            if intent.kind == "LIST_INVOICES":
                result = self._run_async(client.get_invoices(**intent.params))
                return mappers.map_invoice_list(result)
            
            elif intent.kind == "LIST_ORDERS":
                result = self._run_async(client.get_orders(**intent.params))
                return mappers.map_order_list(result)
            
            elif intent.kind == "LIST_PRODUCTS":
                result = self._run_async(client.get_products(**intent.params))
                return mappers.map_product_list(result)
            
            elif intent.kind == "LIST_CUSTOMERS":
                result = self._run_async(client.get_customers(**intent.params))
                return mappers.map_customer_list(result)
            
            elif intent.kind == "LIST_CATEGORIES":
                result = self._run_async(client.get_categories(**intent.params))
                return mappers.map_category_list(result)
            
            elif intent.kind == "LIST_BRANCHES":
                result = self._run_async(client.get_branches())
                return mappers.map_branch_list(result)
            
            elif intent.kind == "SUMMARY_REVENUE":
                # Get invoices and calculate summary
                params = intent.params.copy()
                result = self._run_async(client.get_invoices(**params))
                return mappers.map_summary_revenue(result)
            
            elif intent.kind == "GET_PRODUCT":
                product_id = intent.params.get("product_id")
                product_code = intent.params.get("product_code")
                result = self._run_async(client.get_product(product_id, product_code))
                return {"product": result.get("data", {})}
            
            elif intent.kind == "GET_CUSTOMER":
                customer_id = intent.params.get("customer_id")
                customer_code = intent.params.get("customer_code")
                result = self._run_async(client.get_customer(customer_id, customer_code))
                return {"customer": result.get("data", {})}
            
            elif intent.kind == "GET_INVOICE":
                invoice_id = intent.params.get("invoice_id")
                invoice_code = intent.params.get("invoice_code")
                include_payment = intent.params.get("include_payment", False)
                result = self._run_async(client.get_invoice(invoice_id, invoice_code, include_payment))
                return {"invoice": result.get("data", {})}
            
            elif intent.kind == "GET_ORDER":
                order_id = intent.params.get("order_id")
                order_code = intent.params.get("order_code")
                include_payment = intent.params.get("include_payment", False)
                result = self._run_async(client.get_order(order_id, order_code, include_payment))
                return {"order": result.get("data", {})}
            
            else:
                logger.warning(f"Unsupported read intent: {intent.kind}")
                return {
                    "error": f"Unsupported read intent: {intent.kind}",
                    "data": [],
                }
        
        except Exception as e:
            logger.error(f"Error reading from KiotViet: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "data": [],
            }
    
    def execute_step(
        self,
        step: PlanStep,
        config: ConnectedAppConfig
    ) -> StepResult:
        """
        Execute a plan step on KiotViet.
        
        Args:
            step: Plan step to execute
            config: App configuration
            
        Returns:
            StepResult with execution result
        """
        client = self._build_client(config)
        
        try:
            raw_result = None
            
            # Dispatch based on action
            if step.action == "CREATE_PRODUCT":
                raw_result = self._run_async(client.create_product(step.params))
            
            elif step.action == "UPDATE_PRODUCT":
                product_id = step.params.pop("product_id")
                raw_result = self._run_async(client.update_product(product_id, step.params))
            
            elif step.action == "DELETE_PRODUCT":
                product_id = step.params.get("product_id")
                raw_result = self._run_async(client.delete_product(product_id))
            
            elif step.action == "CREATE_CATEGORY":
                category_name = step.params.get("category_name")
                parent_id = step.params.get("parent_id")
                raw_result = self._run_async(client.create_category(category_name, parent_id))
            
            elif step.action == "UPDATE_CATEGORY":
                category_id = step.params.pop("category_id")
                category_name = step.params.get("category_name")
                parent_id = step.params.get("parent_id")
                raw_result = self._run_async(client.update_category(category_id, category_name, parent_id))
            
            elif step.action == "DELETE_CATEGORY":
                category_id = step.params.get("category_id")
                raw_result = self._run_async(client.delete_category(category_id))
            
            elif step.action == "CREATE_CUSTOMER":
                raw_result = self._run_async(client.create_customer(step.params))
            
            elif step.action == "UPDATE_CUSTOMER":
                customer_id = step.params.pop("customer_id")
                raw_result = self._run_async(client.update_customer(customer_id, step.params))
            
            elif step.action == "DELETE_CUSTOMER":
                customer_id = step.params.get("customer_id")
                raw_result = self._run_async(client.delete_customer(customer_id))
            
            elif step.action == "CREATE_ORDER":
                raw_result = self._run_async(client.create_order(step.params))
            
            elif step.action == "UPDATE_ORDER":
                order_id = step.params.pop("order_id")
                raw_result = self._run_async(client.update_order(order_id, step.params))
            
            elif step.action == "DELETE_ORDER":
                order_id = step.params.get("order_id")
                raw_result = self._run_async(client.delete_order(order_id))
            
            elif step.action == "CREATE_INVOICE":
                raw_result = self._run_async(client.create_invoice(step.params))
            
            elif step.action == "UPDATE_INVOICE":
                invoice_id = step.params.pop("invoice_id")
                raw_result = self._run_async(client.update_invoice(invoice_id, step.params))
            
            elif step.action == "DELETE_INVOICE":
                invoice_id = step.params.get("invoice_id")
                raw_result = self._run_async(client.delete_invoice(invoice_id))
            
            else:
                return StepResult(
                    step_id=step.id,
                    status="failed",
                    message=f"Action {step.action} is not supported by KiotViet adapter",
                    raw={},
                )
            
            # Extract success message from result
            message = "OK"
            if isinstance(raw_result, dict):
                message = raw_result.get("message", "OK")
                # Extract data if present
                data = raw_result.get("data", raw_result)
            else:
                data = raw_result
            
            return StepResult(
                step_id=step.id,
                status="success",
                message=message,
                raw=data if isinstance(data, dict) else {"result": data},
            )
        
        except Exception as e:
            logger.error(f"Error executing step on KiotViet: {str(e)}", exc_info=True)
            return StepResult(
                step_id=step.id,
                status="failed",
                message=str(e),
                raw={},
            )
    
    def supports_action(self, action: str) -> bool:
        """
        Check if KiotViet adapter supports a specific action.
        
        Args:
            action: Action name
            
        Returns:
            True if supported, False otherwise
        """
        supported_actions = {
            "CREATE_PRODUCT",
            "UPDATE_PRODUCT",
            "DELETE_PRODUCT",
            "CREATE_CATEGORY",
            "UPDATE_CATEGORY",
            "DELETE_CATEGORY",
            "CREATE_CUSTOMER",
            "UPDATE_CUSTOMER",
            "DELETE_CUSTOMER",
            "CREATE_ORDER",
            "UPDATE_ORDER",
            "DELETE_ORDER",
            "CREATE_INVOICE",
            "UPDATE_INVOICE",
            "DELETE_INVOICE",
        }
        return action in supported_actions

