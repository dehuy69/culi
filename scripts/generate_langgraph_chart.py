#!/usr/bin/env python3
"""Generate LangGraph visualization chart.

This script generates a visual representation of the LangGraph workflow.
It can export to Mermaid format, PNG (via graphviz), or display as ASCII.
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.graph.app_graph import get_graph


def generate_mermaid(output_path: str = None):
    """Generate Mermaid diagram format."""
    # Generate from known graph structure (based on app_graph.py)
    mermaid_diagram = _generate_mermaid_from_structure()
    
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(mermaid_diagram, encoding="utf-8")
        print(f"✅ Mermaid diagram saved to: {output_file}")
    else:
        print("Mermaid Diagram:")
        print("=" * 80)
        print(mermaid_diagram)
        print("=" * 80)
    
    return mermaid_diagram


def _generate_mermaid_from_structure():
    """Generate Mermaid diagram from known graph structure (based on app_graph.py)."""
    # Graph structure based on app/graph/app_graph.py
    mermaid_lines = [
        "graph TD",
        "    START([Start])",
        "    intent_router[intent_router]",
        "    context[context]",
        "    web_search[web_search]",
        "    app_read[app_read]",
        "    app_plan[app_plan]",
        "    present_plan[present_plan]",
        "    execute_plan[execute_plan]",
        "    answer[answer]",
        "    error[error]",
        "    END([END])",
        "",
        "    START --> intent_router",
        "    intent_router -->|general_qa| context",
        "    intent_router -->|tax_qa| web_search",
        "    intent_router -->|app_read| context",
        "    intent_router -->|app_plan| context",
        "    intent_router -->|no_app| answer",
        "",
        "    context -->|answer| answer",
        "    context -->|app_read| app_read",
        "    context -->|app_plan| app_plan",
        "",
        "    web_search --> answer",
        "    app_read --> answer",
        "    app_plan --> present_plan",
        "",
        "    present_plan -->|execute| execute_plan",
        "    present_plan -->|cancel| answer",
        "",
        "    execute_plan -->|continue| execute_plan",
        "    execute_plan -->|finish| answer",
        "",
        "    answer --> END",
        "    error --> END",
    ]
    
    return "\n".join(mermaid_lines)


def generate_ascii():
    """Generate ASCII representation."""
    ascii_diagram = _generate_ascii_from_structure()
    
    print("ASCII Diagram:")
    print("=" * 80)
    print(ascii_diagram)
    print("=" * 80)
    
    return ascii_diagram


def _generate_ascii_from_structure():
    """Generate ASCII diagram from known graph structure."""
    # Simple ASCII representation
    lines = [
        "LangGraph Workflow:",
        "",
        "START",
        "  └─> intent_router",
        "      ├─> [general_qa] → context",
        "      │       ├─> [answer] → answer",
        "      │       ├─> [app_read] → app_read → answer",
        "      │       └─> [app_plan] → app_plan → present_plan",
        "      ├─> [tax_qa] → web_search → answer",
        "      ├─> [app_read] → context → app_read → answer",
        "      ├─> [app_plan] → context → app_plan → present_plan",
        "      └─> [no_app] → answer",
        "",
        "present_plan",
        "  ├─> [execute] → execute_plan",
        "  │       ├─> [continue] → execute_plan (loop)",
        "  │       └─> [finish] → answer",
        "  └─> [cancel] → answer",
        "",
        "answer → END",
        "error → END",
    ]
    return "\n".join(lines)


def generate_png(output_path: str = "docs/langgraph_chart.png"):
    """Generate PNG image (requires mermaid-cli or pygraphviz)."""
    try:
        import subprocess
        import tempfile
        
        # First generate mermaid file
        mermaid_content = generate_mermaid()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp:
            tmp.write(mermaid_content)
            tmp_path = tmp.name
        
        # Try using mermaid-cli (mmdc) - recommended
        try:
            result = subprocess.run(
                ["mmdc", "-i", tmp_path, "-o", output_path, "-b", "white"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                print(f"✅ PNG chart saved to: {output_file}")
                Path(tmp_path).unlink()  # Clean up temp file
                return output_file
            else:
                print(f"⚠️  mermaid-cli error: {result.stderr}")
                raise FileNotFoundError("mmdc failed")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Fallback: try pygraphviz
            try:
                import pygraphviz as pgv
                from networkx import DiGraph
                
                # Create graph from structure
                G = DiGraph()
                nodes = [
                    "intent_router", "context", "web_search", "app_read",
                    "app_plan", "present_plan", "execute_plan", "answer", "error"
                ]
                for node in nodes:
                    G.add_node(node)
                
                edges = [
                    ("intent_router", "context"),
                    ("intent_router", "web_search"),
                    ("intent_router", "answer"),
                    ("context", "answer"),
                    ("context", "app_read"),
                    ("context", "app_plan"),
                    ("web_search", "answer"),
                    ("app_read", "answer"),
                    ("app_plan", "present_plan"),
                    ("present_plan", "execute_plan"),
                    ("present_plan", "answer"),
                    ("execute_plan", "answer"),
                ]
                for from_node, to_node in edges:
                    G.add_edge(from_node, to_node)
                
                # Convert to pygraphviz and render
                A = pgv.AGraph(directed=True, strict=False)
                A.add_edges_from(G.edges())
                A.layout(prog="dot")
                
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                A.draw(output_path)
                
                print(f"✅ PNG chart saved to: {output_file}")
                Path(tmp_path).unlink()
                return output_file
            except ImportError:
                print("❌ Neither mermaid-cli nor pygraphviz available.")
                print("   Install one of:")
                print("   - mermaid-cli: npm install -g @mermaid-js/mermaid-cli (recommended)")
                print("   - pygraphviz: pip install pygraphviz")
                print("     (also requires graphviz system package)")
                Path(tmp_path).unlink()
                return None
    except Exception as e:
        print(f"❌ Error generating PNG: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate LangGraph visualization")
    parser.add_argument(
        "--format",
        choices=["mermaid", "ascii", "png", "all"],
        default="mermaid",
        help="Output format (default: mermaid)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (for mermaid/png formats)"
    )
    
    args = parser.parse_args()
    
    if args.format == "mermaid" or args.format == "all":
        output_path = args.output or "docs/langgraph_chart.mmd"
        generate_mermaid(output_path)
    
    if args.format == "ascii" or args.format == "all":
        generate_ascii()
    
    if args.format == "png" or args.format == "all":
        output_path = args.output or "docs/langgraph_chart.png"
        generate_png(output_path)


if __name__ == "__main__":
    main()

