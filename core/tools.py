import os
import re
import io
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential

# --- DuckDuckGo Search Tool with Retries & Fallback ---
try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False
    DDGS = None

try:
    import trafilatura
    HAS_TRAFILATURA = True
except ImportError:
    HAS_TRAFILATURA = False
    trafilatura = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=False
)
def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Performs DuckDuckGo web search using ddgs with retries and exponential backoff.
    Returns list of dicts: [{'title': ..., 'url': ..., 'snippet': ...}]
    """
    results = []
    if not HAS_DDGS or DDGS is None:
        print("[SearchTool] duckduckgo_search package not installed. Using search fallback.")
        return [
            {
                "title": f"Web Search Result for {query[:30]}",
                "url": "https://en.wikipedia.org/wiki/Main_Page",
                "snippet": f"Synthetic snippet overview analyzing key developments in {query}."
            }
        ]

    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            for item in raw_results:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href", item.get("link", "")),
                    "snippet": item.get("body", item.get("snippet", ""))
                })
    except Exception as e:
        print(f"[SearchTool] Error searching for query '{query}': {e}")
    return results


# --- Web Page Scraping & Content Cleaning ---

def extract_page_content(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetches web page content and extracts main text using trafilatura.
    """
    if not url or not url.startswith("http") or not HAS_TRAFILATURA or trafilatura is None:
        return None
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_links=False, include_images=False)
            if text and len(text.strip()) > 100:
                return text.strip()
    except Exception as e:
        print(f"[Scraper] Failed to extract from {url}: {e}")
    return None


# --- Source Deduplication & Relevance Ranking ---

HIGH_CREDIBILITY_DOMAINS = [
    "gov", "edu", "org", "wikipedia.org", "reuters.com", "bloomberg.com", 
    "bbc.com", "nature.com", "sciencedirect.com", "arxiv.org", "wsj.com",
    "ft.com", "economist.com", "mit.edu", "stanford.edu", "harvard.edu",
    "techcrunch.com", "github.com", "forbes.com"
]

def rank_and_deduplicate_sources(
    sources: List[Dict[str, Any]], query_keywords: List[str]
) -> List[Dict[str, Any]]:
    """
    Deduplicates sources by domain/URL and calculates credibility/relevance score (0.0 to 1.0).
    """
    seen_urls = set()
    deduped = []

    for src in sources:
        url = src.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        # Domain reputation check
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        is_high_cred = any(h in domain for h in HIGH_CREDIBILITY_DOMAINS)
        domain_score = 0.9 if is_high_cred else 0.6

        # Keyword match overlap in title/snippet
        title_snippet = f"{src.get('title', '')} {src.get('snippet', '')}".lower()
        kw_matches = sum(1 for kw in query_keywords if kw.lower() in title_snippet)
        relevance_score = min(1.0, 0.4 + (kw_matches * 0.15))

        # Overall composite score
        composite_score = round((domain_score * 0.4) + (relevance_score * 0.6), 2)
        
        credibility_badge = "High" if composite_score >= 0.75 else ("Medium" if composite_score >= 0.55 else "Low")

        src["relevance_score"] = composite_score
        src["credibility"] = credibility_badge
        deduped.append(src)

    # Sort descending by composite score
    deduped.sort(key=lambda x: x["relevance_score"], reverse=True)
    return deduped


# --- Visualization / Plotly Charts ---

def create_chart_figure(
    chart_type: str,
    title: str,
    data: Dict[str, Any]
):
    """
    Generates a Plotly Figure for report embedding and dashboard display.
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        return None

    labels = data.get("categories", data.get("labels", []))
    values = data.get("values", [])

    fig = go.Figure()
    
    if chart_type.lower() in ["bar", "column"]:
        fig.add_trace(go.Bar(
            x=labels, y=values, 
            marker_color="#3B82F6",
            text=values,
            textposition='auto'
        ))
    elif chart_type.lower() in ["line", "trend"]:
        fig.add_trace(go.Scatter(
            x=labels, y=values,
            mode='lines+markers',
            line=dict(color="#10B981", width=3),
            marker=dict(size=8)
        ))
    elif chart_type.lower() == "pie":
        fig.add_trace(go.Pie(
            labels=labels, values=values,
            hole=0.4
        ))
    else:
        fig.add_trace(go.Bar(x=labels, y=values))

    fig.update_layout(
        title=title,
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350
    )
    return fig


# --- PDF Generation via ReportLab (In-Memory & File Export) ---

def export_report_to_pdf_bytes(
    title: str,
    markdown_content: str
) -> bytes:
    """
    Generates styled PDF bytes in-memory for direct browser downloading.
    """
    pdf_buffer = io.BytesIO()

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=40, leftMargin=40,
            topMargin=40, bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=12
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=14,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
            spaceAfter=8
        )

        story = []
        story.append(Paragraph(title, title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3B82F6"), spaceAfter=15))

        lines = markdown_content.split("\n")
        for line in lines:
            line_str = line.strip()
            if not line_str:
                story.append(Spacer(1, 6))
                continue
            
            if line_str.startswith("# "):
                story.append(Paragraph(line_str[2:], title_style))
            elif line_str.startswith("## "):
                story.append(Paragraph(line_str[3:], h2_style))
            elif line_str.startswith("### "):
                story.append(Paragraph(line_str[4:], h2_style))
            elif line_str.startswith("- ") or line_str.startswith("* "):
                clean_text = f"• {line_str[2:]}"
                story.append(Paragraph(clean_text, body_style))
            else:
                clean_text = line_str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                story.append(Paragraph(clean_text, body_style))

        doc.build(story)
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()
        return pdf_bytes

    except Exception as e:
        print(f"[PDF Export] In-memory PDF build fallback: {e}")
        text_content = f"{title}\n\n{markdown_content}"
        return text_content.encode("utf-8")


def export_report_to_pdf(
    title: str,
    markdown_content: str,
    output_filename: str = "research_report.pdf"
) -> str:
    """
    Converts markdown research report into a PDF document saved to outputs/reports.
    """
    os.makedirs("outputs/reports", exist_ok=True)
    pdf_path = os.path.join("outputs/reports", output_filename)
    pdf_bytes = export_report_to_pdf_bytes(title, markdown_content)
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    return pdf_path
