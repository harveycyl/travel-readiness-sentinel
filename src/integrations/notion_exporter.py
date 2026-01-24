"""
Notion integration for Travel Readiness Sentinel.
Exports validation results to Notion pages.
"""
import logging
from datetime import datetime
from typing import Dict, Any
from notion_client import Client
from notion_client.errors import APIResponseError

from ..core.schemas import ValidationResponse

logger = logging.getLogger(__name__)


class NotionExporter:
    """Export validation results to Notion pages."""
    
    def __init__(self, api_token: str):
        """Initialize Notion client with API token."""
        self.client = Client(auth=api_token)
    
    async def export_validation_results(
        self,
        validation_response: ValidationResponse,
        parent_page_id: str
    ) -> Dict[str, Any]:
        """
        Export validation results to a Notion page.
        
        Args:
            validation_response: The validation results to export
            parent_page_id: The ID of the parent Notion page
            
        Returns:
            Dict containing the created page URL and ID
            
        Raises:
            APIResponseError: If the Notion API request fails
        """
        try:
            # Create page title with timestamp
            page_title = self._create_page_title(validation_response)
            
            # Build page content blocks
            page_blocks = self._build_page_blocks(validation_response)
            
            # Create the Notion page
            logger.info(f"Creating Notion page for {validation_response.destination}")
            page = self.client.pages.create(
                parent={"page_id": parent_page_id},
                properties={
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": page_title
                                }
                            }
                        ]
                    }
                },
                children=page_blocks
            )
            
            page_url = page.get("url", "")
            page_id = page.get("id", "")
            
            logger.info(f"Successfully created Notion page: {page_url}")
            
            return {
                "notion_url": page_url,
                "notion_page_id": page_id,
                "exported_at": datetime.utcnow().isoformat()
            }
            
        except APIResponseError as e:
            logger.error(f"Notion API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Notion export: {e}")
            raise
    
    def _create_page_title(self, validation_response: ValidationResponse) -> str:
        """Create a descriptive page title."""
        status_emoji = "✅" if validation_response.status == "success" else "❌"
        date_str = validation_response.timestamp.strftime("%b %d, %Y")
        return f"{status_emoji} {validation_response.destination} - {date_str}"
    
    def _build_page_blocks(self, validation_response: ValidationResponse) -> list:
        """Build Notion blocks for the page content."""
        blocks = []
        
        # Summary section
        blocks.append(self._heading_block("📊 Validation Summary", level=1))
        
        # Status overview
        status_icon = "✅" if validation_response.status == "success" else "⚠️"
        blocks.append(self._paragraph_block(
            f"{status_icon} **Status:** {validation_response.status.upper()}"
        ))
        blocks.append(self._paragraph_block(
            f"📍 **Destination:** {validation_response.destination}"
        ))
        blocks.append(self._paragraph_block(
            f"🔍 **Total Checks:** {validation_response.total_checks}"
        ))
        blocks.append(self._paragraph_block(
            f"✅ **Passed:** {validation_response.passed_checks}"
        ))
        blocks.append(self._paragraph_block(
            f"❌ **Failed:** {validation_response.failed_checks}"
        ))
        
        # Divider
        blocks.append({"object": "block", "type": "divider", "divider": {}})
        
        # Detailed checks section
        blocks.append(self._heading_block("📋 Detailed Check Results", level=2))
        
        # Create a table for check results
        for check in validation_response.checks:
            icon = "✅" if check.passed else "❌"
            blocks.append(self._callout_block(
                icon=icon,
                text=f"**{check.check_name}**\n{check.message}",
                color="green_background" if check.passed else "red_background"
            ))
        
        # Footer with timestamp
        blocks.append({"object": "block", "type": "divider", "divider": {}})
        blocks.append(self._paragraph_block(
            f"🕐 Generated: {validation_response.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        ))
        
        return blocks
    
    def _heading_block(self, text: str, level: int = 1) -> Dict[str, Any]:
        """Create a heading block."""
        heading_type = f"heading_{level}"
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": text}
                    }
                ]
            }
        }
    
    def _paragraph_block(self, text: str) -> Dict[str, Any]:
        """Create a paragraph block with support for bold markdown."""
        rich_text = self._parse_rich_text(text)
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_text
            }
        }
    
    def _callout_block(self, icon: str, text: str, color: str = "gray_background") -> Dict[str, Any]:
        """Create a callout block."""
        rich_text = self._parse_rich_text(text)
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": rich_text,
                "icon": {
                    "type": "emoji",
                    "emoji": icon
                },
                "color": color
            }
        }
    
    def _parse_rich_text(self, text: str) -> list:
        """Parse text with simple markdown (bold) into Notion rich text format."""
        parts = []
        segments = text.split("**")
        
        for i, segment in enumerate(segments):
            if segment:
                is_bold = i % 2 == 1
                parts.append({
                    "type": "text",
                    "text": {"content": segment},
                    "annotations": {"bold": is_bold}
                })
        
        return parts if parts else [{"type": "text", "text": {"content": text}}]


async def export_to_notion(
    validation_response: ValidationResponse,
    notion_token: str,
    parent_page_id: str
) -> Dict[str, Any]:
    """
    Convenience function to export validation results to Notion.
    
    Args:
        validation_response: The validation results to export
        notion_token: Notion API integration token
        parent_page_id: The ID of the parent Notion page
        
    Returns:
        Dict containing export details (URL, page ID, timestamp)
    """
    exporter = NotionExporter(api_token=notion_token)
    return await exporter.export_validation_results(validation_response, parent_page_id)
