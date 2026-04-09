"""Central registry of callable tools (name → instance)."""

from __future__ import annotations

from app.tools.base import BaseTool
from app.tools.compliance_check import ComplianceTool
from app.tools.search_docs import SearchDocsTool
from app.tools.send_email import SendEmailTool

TOOLS: dict[str, BaseTool] = {
    SendEmailTool.name: SendEmailTool(),
    SearchDocsTool.name: SearchDocsTool(),
    ComplianceTool.name: ComplianceTool(),
}


def get_tool(name: str) -> BaseTool | None:
    return TOOLS.get(name)


def list_tool_metadata() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for t in TOOLS.values():
        model = t.input_model()
        out.append(
            {
                'name': t.name,
                'description': t.description,
                'allowed_roles': [r.value for r in sorted(t.allowed_roles, key=lambda x: x.value)],
                'input_schema': model.model_json_schema(),
            }
        )
    return sorted(out, key=lambda x: str(x['name']))
