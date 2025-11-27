"""Direct KiotViet Public API client with automatic token management."""
import httpx
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from app.integrations.kiotviet_oauth import get_access_token
from app.core.logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://public.kiotapi.com"
TOKEN_URL = "https://id.kiotviet.vn/connect/token"


class KiotVietDirectClient:
    """
    Direct client for KiotViet Public API.
    Handles OAuth2 token management and all API operations.
    """
    
    def __init__(self, client_id: str, client_secret: str, retailer: str):
        """
        Initialize KiotViet Direct API client.
        
        Args:
            client_id: KiotViet OAuth2 client ID
            client_secret: KiotViet OAuth2 client secret
            retailer: Retailer name (tên gian hàng)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.retailer = retailer
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _ensure_token(self) -> str:
        """Ensure access token is valid and refresh if needed."""
        if not self._access_token or (
            self._token_expires_at and datetime.now() >= self._token_expires_at - timedelta(minutes=5)
        ):
            # Get new token (get_access_token is async and returns str directly)
            self._access_token = await get_access_token(self.client_id, self.client_secret)
            # Token expires in 24h by default (based on KiotViet API)
            expires_in = 86400  # 24 hours
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            logger.debug(f"Refreshed KiotViet access token, expires at {self._token_expires_at}")
        
        return self._access_token
    
    def _headers(self, access_token: str) -> Dict[str, str]:
        """Get headers with authentication for API requests."""
        return {
            "Retailer": self.retailer,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # ========== Categories API ==========
    
    async def get_categories(
        self,
        hierarchical_data: bool = True,
        last_modified_from: Optional[datetime] = None,
        page_size: int = 100,
        current_item: int = 0,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get list of categories."""
        params = {
            "hierarchicalData": hierarchical_data,
            "pageSize": page_size,
            "currentItem": current_item,
        }
        if last_modified_from:
            params["lastModifiedFrom"] = last_modified_from.isoformat()
        if order_by:
            params["orderBy"] = order_by
        if order_direction:
            params["orderDirection"] = order_direction
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/categories",
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_category(self, category_id: int) -> Dict[str, Any]:
        """Get category details by ID."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/categories/{category_id}",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json()
    
    async def create_category(
        self,
        category_name: str,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new category."""
        body = {"categoryName": category_name}
        if parent_id:
            body["parentId"] = parent_id
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.post(
            f"{BASE_URL}/categories",
            headers=self._headers(access_token),
            json=body
        )
        response.raise_for_status()
        return response.json()
    
    async def update_category(
        self,
        category_id: int,
        category_name: Optional[str] = None,
        parent_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update a category."""
        body = {}
        if category_name:
            body["categoryName"] = category_name
        if parent_id is not None:
            body["parentId"] = parent_id
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.put(
            f"{BASE_URL}/categories/{category_id}",
            headers=self._headers(access_token),
            json=body
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_category(self, category_id: int) -> Dict[str, Any]:
        """Delete a category."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.delete(
            f"{BASE_URL}/categories/{category_id}",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json() if response.text else {"message": "success"}
    
    # ========== Products API ==========
    
    async def get_products(
        self,
        name: Optional[str] = None,
        category_id: Optional[int] = None,
        page_size: int = 100,
        current_item: int = 0,
        include_inventory: bool = False,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Get list of products."""
        params = {
            "pageSize": page_size,
            "currentItem": current_item,
            "includeInventory": include_inventory,
        }
        if name:
            params["name"] = name
        if category_id:
            params["categoryId"] = category_id
        if order_by:
            params["orderBy"] = order_by
        if order_direction:
            params["orderDirection"] = order_direction
        # Add any additional params from kwargs
        params.update(kwargs)
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/products",
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_product(self, product_id: Optional[int] = None, product_code: Optional[str] = None) -> Dict[str, Any]:
        """Get product details by ID or code."""
        if product_id:
            path = f"{BASE_URL}/products/{product_id}"
        elif product_code:
            path = f"{BASE_URL}/products/code/{product_code}"
        else:
            raise ValueError("Either product_id or product_code must be provided")
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            path,
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json()
    
    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.post(
            f"{BASE_URL}/products",
            headers=self._headers(access_token),
            json=product_data
        )
        response.raise_for_status()
        return response.json()
    
    async def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.put(
            f"{BASE_URL}/products/{product_id}",
            headers=self._headers(access_token),
            json=product_data
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_product(self, product_id: int) -> Dict[str, Any]:
        """Delete a product."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.delete(
            f"{BASE_URL}/products/{product_id}",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json() if response.text else {"message": "success"}
    
    # ========== Customers API ==========
    
    async def get_customers(
        self,
        name: Optional[str] = None,
        contact_number: Optional[str] = None,
        code: Optional[str] = None,
        page_size: int = 100,
        current_item: int = 0,
        include_total: bool = False,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Search/get customers."""
        params = {
            "pageSize": page_size,
            "currentItem": current_item,
            "includeTotal": include_total,
        }
        if name:
            params["name"] = name
        if contact_number:
            params["contactNumber"] = contact_number
        if code:
            params["code"] = code
        if order_by:
            params["orderBy"] = order_by
        if order_direction:
            params["orderDirection"] = order_direction
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/customers",
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_customer(self, customer_id: Optional[int] = None, customer_code: Optional[str] = None) -> Dict[str, Any]:
        """Get customer details by ID or code."""
        if customer_id:
            path = f"{BASE_URL}/customers/{customer_id}"
        elif customer_code:
            path = f"{BASE_URL}/customers/code/{customer_code}"
        else:
            raise ValueError("Either customer_id or customer_code must be provided")
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            path,
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json()
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.post(
            f"{BASE_URL}/customers",
            headers=self._headers(access_token),
            json=customer_data
        )
        response.raise_for_status()
        return response.json()
    
    async def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a customer."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.put(
            f"{BASE_URL}/customers/{customer_id}",
            headers=self._headers(access_token),
            json=customer_data
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_customer(self, customer_id: int) -> Dict[str, Any]:
        """Delete a customer."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.delete(
            f"{BASE_URL}/customers/{customer_id}",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json() if response.text else {"message": "success"}
    
    # ========== Orders API ==========
    
    async def get_orders(
        self,
        branch_ids: Optional[List[int]] = None,
        customer_ids: Optional[List[int]] = None,
        status: Optional[List[int]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page_size: int = 100,
        current_item: int = 0,
        include_payment: bool = False,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get list of orders."""
        params = {
            "pageSize": page_size,
            "currentItem": current_item,
            "includePayment": include_payment,
        }
        if branch_ids:
            params["branchIds"] = branch_ids
        if customer_ids:
            params["customerIds"] = customer_ids
        if status:
            params["status"] = status
        if from_date:
            params["fromDate"] = from_date.isoformat()
        if to_date:
            params["toDate"] = to_date.isoformat()
        if order_by:
            params["orderBy"] = order_by
        if order_direction:
            params["orderDirection"] = order_direction
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/orders",
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_order(self, order_id: Optional[int] = None, order_code: Optional[str] = None, include_payment: bool = False) -> Dict[str, Any]:
        """Get order details by ID or code."""
        if order_id:
            path = f"{BASE_URL}/orders/{order_id}"
        elif order_code:
            path = f"{BASE_URL}/orders/code/{order_code}"
        else:
            raise ValueError("Either order_id or order_code must be provided")
        
        params = {"includePayment": include_payment} if include_payment else {}
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            path,
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.post(
            f"{BASE_URL}/orders",
            headers=self._headers(access_token),
            json=order_data
        )
        response.raise_for_status()
        return response.json()
    
    async def update_order(self, order_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an order."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.put(
            f"{BASE_URL}/orders/{order_id}",
            headers=self._headers(access_token),
            json=order_data
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_order(self, order_id: int) -> Dict[str, Any]:
        """Delete an order."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.delete(
            f"{BASE_URL}/orders/{order_id}",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json() if response.text else {"message": "success"}
    
    # ========== Invoices API ==========
    
    async def get_invoices(
        self,
        branch_ids: Optional[List[int]] = None,
        customer_ids: Optional[List[int]] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        from_purchase_date: Optional[datetime] = None,
        to_purchase_date: Optional[datetime] = None,
        page_size: int = 100,
        current_item: int = 0,
        include_payment: bool = False,
    ) -> Dict[str, Any]:
        """Get list of invoices."""
        params = {
            "pageSize": page_size,
            "currentItem": current_item,
            "includePayment": include_payment,
        }
        if branch_ids:
            params["branchIds"] = branch_ids
        if customer_ids:
            params["customerIds"] = customer_ids
        if from_date:
            params["fromDate"] = from_date.isoformat()
        if to_date:
            params["toDate"] = to_date.isoformat()
        if from_purchase_date:
            params["fromPurchaseDate"] = from_purchase_date.isoformat()
        if to_purchase_date:
            params["toPurchaseDate"] = to_purchase_date.isoformat()
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/invoices",
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def get_invoice(self, invoice_id: Optional[int] = None, invoice_code: Optional[str] = None, include_payment: bool = False) -> Dict[str, Any]:
        """Get invoice details by ID or code."""
        if invoice_id:
            path = f"{BASE_URL}/invoices/{invoice_id}"
        elif invoice_code:
            path = f"{BASE_URL}/invoices/code/{invoice_code}"
        else:
            raise ValueError("Either invoice_id or invoice_code must be provided")
        
        params = {"includePayment": include_payment} if include_payment else {}
        
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            path,
            headers=self._headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    async def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new invoice."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.post(
            f"{BASE_URL}/invoices",
            headers=self._headers(access_token),
            json=invoice_data
        )
        response.raise_for_status()
        return response.json()
    
    async def update_invoice(self, invoice_id: int, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an invoice."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.put(
            f"{BASE_URL}/invoices/{invoice_id}",
            headers=self._headers(access_token),
            json=invoice_data
        )
        response.raise_for_status()
        return response.json()
    
    async def delete_invoice(self, invoice_id: int) -> Dict[str, Any]:
        """Delete an invoice."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.delete(
            f"{BASE_URL}/invoices/{invoice_id}",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json() if response.text else {"message": "success"}
    
    # ========== Branches API ==========
    
    async def get_branches(self) -> Dict[str, Any]:
        """Get list of branches."""
        access_token = await self._ensure_token()
        client = await self._get_client()
        response = await client.get(
            f"{BASE_URL}/branches",
            headers=self._headers(access_token)
        )
        response.raise_for_status()
        return response.json()

