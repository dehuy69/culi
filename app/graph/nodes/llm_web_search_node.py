"""LLM Web search node using GPT-4o-mini Search Preview."""
from typing import Dict, Any
from app.core.llm_config import get_llm
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def llm_web_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search the web using GPT-4o-mini Search Preview model.
    This model has built-in web search capabilities and will automatically
    search and synthesize information from the web.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with web_results and kb_context
    """
    user_input = state.get("user_input", "")
    chat_context = state.get("chat_context", "")
    
    # Build search query/prompt
    search_prompt = f"""Bạn là trợ lý tìm kiếm thông tin chuyên nghiệp. Hãy tìm kiếm và tổng hợp thông tin về câu hỏi sau:

Câu hỏi: {user_input}

Ngữ cảnh từ cuộc trò chuyện trước: {chat_context if chat_context else "Không có"}

Hãy:
1. Tìm kiếm thông tin liên quan trên web
2. Tổng hợp và phân tích thông tin tìm được
3. Trả lời câu hỏi một cách chi tiết, chính xác và có nguồn tham khảo

Trả lời bằng tiếng Việt."""
    
    try:
        # Use GPT-4o-mini Search Preview model
        # This model has built-in web search capability and will automatically
        # search the web and synthesize information
        llm = get_llm(
            temperature=0.3,  # Lower temperature for more factual search results
            model=settings.llm_model_web_search,
            max_tokens=settings.llm_max_tokens_web_search
        )
        
        # Invoke LLM with search prompt
        # The model will automatically search the web and synthesize results
        response = llm.invoke([
            {
                "role": "system",
                "content": "Bạn là trợ lý tìm kiếm thông tin chuyên nghiệp. Sử dụng khả năng tìm kiếm web của bạn để tìm và tổng hợp thông tin chính xác, đáng tin cậy. Trả lời bằng tiếng Việt."
            },
            {
                "role": "user",
                "content": search_prompt
            }
        ])
        
        # Extract search results and summary
        search_result_text = response.content.strip()
        
        # Store the synthesized search result
        state["web_results"] = [
            {
                "title": "Kết quả tìm kiếm tổng hợp",
                "snippet": search_result_text,
                "source": "GPT-4o-mini Search Preview"
            }
        ]
        
        # Use the full result as kb_context
        state["kb_context"] = search_result_text
        
        logger.info(f"LLM web search completed: {len(search_result_text)} characters")
        
    except Exception as e:
        logger.error(f"LLM web search error: {str(e)}", exc_info=True)
        state["web_results"] = []
        state["kb_context"] = f"Lỗi khi tìm kiếm thông tin: {str(e)}"
    
    return state

