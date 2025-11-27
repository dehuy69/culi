"""KiotViet MCP client wrapper for direct import integration."""
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.integrations.kiotviet_oauth import get_access_token
from app.core.logging import get_logger

logger = get_logger(__name__)

# Add kiotviet-mcp to path for direct import
KIOTVIET_MCP_PATH = Path("/home/huy/Documents/kiotviet-mcp")
if str(KIOTVIET_MCP_PATH) not in sys.path:
    sys.path.insert(0, str(KIOTVIET_MCP_PATH))

try:
    # Direct import of MCP tools
    from kiotviet_mcp_server import (
        kv_list_products,
        kv_get_product,
        kv_search_customers,
        kv_get_customer,
        kv_create_customer,
        kv_list_orders,
        kv_get_order,
        kv_create_order,
        kv_list_invoices,
        kv_get_invoice,
        kv_list_categories,
        kv_list_branches,
    )
except ImportError as e:
    logger.warning(f"Failed to import kiotviet-mcp tools: {e}")
    logger.warning("MCP tools will not be available. Ensure kiotviet-mcp is in the path.")
    # Create dummy functions to prevent errors
    kv_list_products = None
    kv_get_product = None
    kv_search_customers = None
    kv_get_customer = None
    kv_create_customer = None
    kv_list_orders = None
    kv_get_order = None
    kv_create_order = None
    kv_list_invoices = None
    kv_get_invoice = None
    kv_list_categories = None
    kv_list_branches = None


class KiotVietMCPClient:
    """Wrapper for KiotViet MCP tools with automatic token management."""
    
    def __init__(self, client_id: str, client_secret: str, retailer: str):
        """
        Initialize KiotViet MCP client.
        
        Args:
            client_id: KiotViet client ID
            client_secret: KiotViet client secret
            retailer: KiotViet retailer name
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.retailer = retailer
        self._access_token: Optional[str] = None
    
    async def _ensure_token(self) -> str:
        """Ensure access token is available."""
        if not self._access_token:
            import asyncio
            self._access_token = await get_access_token(self.client_id, self.client_secret)
        return self._access_token
    
    async def list_products(
        self,
        page_size: int = 50,
        current_item: int = 0,
        name: Optional[str] = None,
        category_id: Optional[int] = None,
        include_inventory: bool = True,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List products."""
        if kv_list_products is None:
            raise RuntimeError("kv_list_products is not available")
        
        access_token = await self._ensure_token()
        return kv_list_products(
            access_token=access_token,
            retailer=self.retailer,
            page_size=page_size,
            current_item=current_item,
            name=name,
            category_id=category_id,
            include_inventory=include_inventory,
            order_by=order_by,
            order_direction=order_direction,
        )
    
    async def get_product(
        self,
        product_id: Optional[int] = None,
        product_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get product by ID or code."""
        if kv_get_product is None:
            raise RuntimeError("kv_get_product is not available")
        
        access_token = await self._ensure_token()
        return kv_get_product(
            access_token=access_token,
            retailer=self.retailer,
            product_id=product_id,
            product_code=product_code,
        )
    
    async def search_customers(
        self,
        name: Optional[str] = None,
        contact_number: Optional[str] = None,
        code: Optional[str] = None,
        page_size: int = 20,
        current_item: int = 0,
        include_total: bool = False,
    ) -> Dict[str, Any]:
        """Search customers."""
        if kv_search_customers is None:
            raise RuntimeError("kv_search_customers is not available")
        
        access_token = await self._ensure_token()
        return kv_search_customers(
            access_token=access_token,
            retailer=self.retailer,
            name=name,
            contact_number=contact_number,
            code=code,
            page_size=page_size,
            current_item=current_item,
            include_total=include_total,
        )
    
    async def get_customer(
        self,
        customer_id: Optional[int] = None,
        customer_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get customer by ID or code."""
        if kv_get_customer is None:
            raise RuntimeError("kv_get_customer is not available")
        
        access_token = await self._ensure_token()
        return kv_get_customer(
            access_token=access_token,
            retailer=self.retailer,
            customer_id=customer_id,
            customer_code=customer_code,
        )
    
    async def create_customer(
        self,
        name: str,
        code: Optional[str] = None,
        contact_number: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        gender: Optional[bool] = None,
        birth_date: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new customer."""
        if kv_create_customer is None:
            raise RuntimeError("kv_create_customer is not available")
        
        access_token = await self._ensure_token()
        return kv_create_customer(
            access_token=access_token,
            retailer=self.retailer,
            name=name,
            code=code,
            contact_number=contact_number,
            email=email,
            address=address,
            gender=gender,
            birth_date=birth_date,
            comments=comments,
        )
    
    async def list_orders(
        self,
        branch_ids: Optional[List[int]] = None,
        status: Optional[List[int]] = None,
        customer_ids: Optional[List[int]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page_size: int = 50,
        current_item: int = 0,
        include_payment: bool = False,
    ) -> Dict[str, Any]:
        """List orders."""
        if kv_list_orders is None:
            raise RuntimeError("kv_list_orders is not available")
        
        access_token = await self._ensure_token()
        return kv_list_orders(
            access_token=access_token,
            retailer=self.retailer,
            branch_ids=branch_ids,
            status=status,
            customer_ids=customer_ids,
            from_date=from_date,
            to_date=to_date,
            page_size=page_size,
            current_item=current_item,
            include_payment=include_payment,
        )
    
    async def get_order(
        self,
        order_id: Optional[int] = None,
        order_code: Optional[str] = None,
        include_payment: bool = False,
    ) -> Dict[str, Any]:
        """Get order by ID or code."""
        if kv_get_order is None:
            raise RuntimeError("kv_get_order is not available")
        
        access_token = await self._ensure_token()
        return kv_get_order(
            access_token=access_token,
            retailer=self.retailer,
            order_id=order_id,
            order_code=order_code,
            include_payment=include_payment,
        )
    
    async def create_order(
        self,
        branch_id: int,
        purchase_date: str,
        order_details: List[Dict[str, Any]],
        customer_id: Optional[int] = None,
        description: Optional[str] = None,
        total_payment: Optional[float] = None,
        discount: Optional[float] = None,
        method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new order."""
        if kv_create_order is None:
            raise RuntimeError("kv_create_order is not available")
        
        access_token = await self._ensure_token()
        return kv_create_order(
            access_token=access_token,
            retailer=self.retailer,
            branch_id=branch_id,
            purchase_date=purchase_date,
            order_details=order_details,
            customer_id=customer_id,
            description=description,
            total_payment=total_payment,
            discount=discount,
            method=method,
        )
    
    async def list_invoices(
        self,
        branch_ids: Optional[List[int]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        from_purchase_date: Optional[str] = None,
        to_purchase_date: Optional[str] = None,
        customer_ids: Optional[List[int]] = None,
        page_size: int = 50,
        current_item: int = 0,
        include_payment: bool = False,
    ) -> Dict[str, Any]:
        """List invoices."""
        if kv_list_invoices is None:
            raise RuntimeError("kv_list_invoices is not available")
        
        access_token = await self._ensure_token()
        return kv_list_invoices(
            access_token=access_token,
            retailer=self.retailer,
            branch_ids=branch_ids,
            from_date=from_date,
            to_date=to_date,
            from_purchase_date=from_purchase_date,
            to_purchase_date=to_purchase_date,
            customer_ids=customer_ids,
            page_size=page_size,
            current_item=current_item,
            include_payment=include_payment,
        )
    
    async def get_invoice(
        self,
        invoice_id: Optional[int] = None,
        invoice_code: Optional[str] = None,
        include_payment: bool = False,
    ) -> Dict[str, Any]:
        """Get invoice by ID or code."""
        if kv_get_invoice is None:
            raise RuntimeError("kv_get_invoice is not available")
        
        access_token = await self._ensure_token()
        return kv_get_invoice(
            access_token=access_token,
            retailer=self.retailer,
            invoice_id=invoice_id,
            invoice_code=invoice_code,
            include_payment=include_payment,
        )
    
    async def list_categories(
        self,
        hierarchical_data: bool = True,
        page_size: int = 100,
        current_item: int = 0,
    ) -> Dict[str, Any]:
        """List categories."""
        if kv_list_categories is None:
            raise RuntimeError("kv_list_categories is not available")
        
        access_token = await self._ensure_token()
        return kv_list_categories(
            access_token=access_token,
            retailer=self.retailer,
            hierarchical_data=hierarchical_data,
            page_size=page_size,
            current_item=current_item,
        )
    
    async def list_branches(self) -> Dict[str, Any]:
        """List branches."""
        if kv_list_branches is None:
            raise RuntimeError("kv_list_branches is not available")
        
        access_token = await self._ensure_token()
        return kv_list_branches(
            access_token=access_token,
            retailer=self.retailer,
        )

