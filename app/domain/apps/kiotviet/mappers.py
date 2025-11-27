"""Data mappers for KiotViet API responses to internal schema."""
from typing import Dict, Any, List


def map_invoice_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map KiotViet invoice list response to internal format.
    
    Args:
        raw: Raw response from KiotViet API
        
    Returns:
        Normalized invoice list data
    """
    return {
        "invoices": raw.get("data", []),
        "total": raw.get("total", 0),
        "page_size": raw.get("pageSize", 0),
        "removed_ids": raw.get("removedIds", []),
        "timestamp": raw.get("timestamp"),
    }


def map_order_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map KiotViet order list response to internal format.
    
    Args:
        raw: Raw response from KiotViet API
        
    Returns:
        Normalized order list data
    """
    return {
        "orders": raw.get("data", []),
        "total": raw.get("total", 0),
        "page_size": raw.get("pageSize", 0),
    }


def map_product_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map KiotViet product list response to internal format.
    
    Args:
        raw: Raw response from KiotViet API
        
    Returns:
        Normalized product list data
    """
    return {
        "products": raw.get("data", []),
        "total": raw.get("total", 0),
        "page_size": raw.get("pageSize", 0),
        "removed_ids": raw.get("removeId", []),
    }


def map_customer_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map KiotViet customer list response to internal format.
    
    Args:
        raw: Raw response from KiotViet API
        
    Returns:
        Normalized customer list data
    """
    return {
        "customers": raw.get("data", []),
        "total": raw.get("total", 0),
        "page_size": raw.get("pageSize", 0),
    }


def map_category_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map KiotViet category list response to internal format.
    
    Args:
        raw: Raw response from KiotViet API
        
    Returns:
        Normalized category list data
    """
    return {
        "categories": raw.get("data", []),
        "total": raw.get("total", 0),
        "page_size": raw.get("pageSize", 0),
        "removed_ids": raw.get("removedIds", []),
        "timestamp": raw.get("timestamp"),
    }


def map_branch_list(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map KiotViet branch list response to internal format.
    
    Args:
        raw: Raw response from KiotViet API
        
    Returns:
        Normalized branch list data
    """
    return {
        "branches": raw.get("data", []),
    }


def map_summary_revenue(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map revenue summary data from invoices.
    
    Args:
        raw: Raw invoice data
        
    Returns:
        Summary with total revenue, count, etc.
    """
    invoices = raw.get("data", [])
    total_revenue = sum(float(inv.get("total", 0)) for inv in invoices)
    total_paid = sum(float(inv.get("totalPayment", 0)) for inv in invoices)
    
    return {
        "revenue": total_revenue,
        "paid": total_paid,
        "outstanding": total_revenue - total_paid,
        "count": len(invoices),
        "invoices": invoices,
    }

