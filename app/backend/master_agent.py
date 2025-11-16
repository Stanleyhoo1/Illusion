import os
import json
import time
import threading
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from strands import Agent
from strands.models.gemini import GeminiModel
from string import Template

import re
from .agents.search_agent import search_agent
from .agents.extract_agent import extract_agent
from .agents.summary_agent import summary_agent

import mlflow
import mlflow.strands

# Enable tracing + token usage logging for Strands Agents
mlflow.strands.autolog()


# -------------------------------------------------------------------
# Env / LLM
# -------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)


def run_master_pipeline(
    company_or_url: str,
    user_query: Optional[str] = None,
    task_prompt: str = "privacy policies, terms of service, and data practices",
) -> Dict[str, Any]:
    """
    Deterministic master orchestrator:
      1) call search_agent
      2) call extract_agent
      3) call summary_agent
      4) assemble the final JSON object described in your MASTER_SYSTEM_PROMPT
    """

    if user_query is None:
        user_query = (
            f"Summarize {company_or_url}'s privacy policies, terms of service, "
            f"and data practices (data collection, usage, sharing, retention, "
            f"user rights, cookies, API usage, etc.)."
        )

    t0 = time.time()
    trace_steps = []
    tools_used = []

    # ---------------------------------------------------------------
    # Step 1 – search_agent
    # ---------------------------------------------------------------
    search_step_index = len(trace_steps)
    try:
        search_result = search_agent(company_or_url=company_or_url)
    except Exception as e:
        total_ms = int((time.time() - t0) * 1000)
        return {
            "status": "error",
            "query": user_query,
            "search_result": None,
            "extraction_result": None,
            "final_summary": None,
            "timing": {"estimated_total_ms": total_ms},
            "trace": {
                "tools_used": ["search_agent"],
                "steps": [
                    {
                        "step_index": search_step_index,
                        "action": "Call search_agent to resolve company and find policy URLs",
                        "tool": "search_agent",
                        "tool_input": f"company_or_url={company_or_url}",
                        "tool_output_used": "exception",
                        "reasoning": "Failed during search_agent call, so we cannot proceed.",
                    }
                ],
            },
            "error_message": f"search_agent raised an exception: {e}",
        }

    tools_used.append("search_agent")
    trace_steps.append(
        {
            "step_index": search_step_index,
            "action": "Call search_agent to resolve company and find policy URLs",
            "tool": "search_agent",
            "tool_input": f"company_or_url={company_or_url}",
            "tool_output_used": "full search_agent JSON",
            "reasoning": "We need a list of relevant policy URLs and metadata before extraction.",
        }
    )

    if not isinstance(search_result, dict) or search_result.get("status") != "success":
        total_ms = int((time.time() - t0) * 1000)
        return {
            "status": "error",
            "query": user_query,
            "search_result": search_result,
            "extraction_result": None,
            "final_summary": None,
            "timing": {"estimated_total_ms": total_ms},
            "trace": {
                "tools_used": tools_used,
                "steps": trace_steps,
            },
            "error_message": "search_agent did not return a successful JSON payload.",
        }

    sources = search_result.get("sources") or []
    if not sources:
        total_ms = int((time.time() - t0) * 1000)
        return {
            "status": "error",
            "query": user_query,
            "search_result": search_result,
            "extraction_result": None,
            "final_summary": None,
            "timing": {"estimated_total_ms": total_ms},
            "trace": {
                "tools_used": tools_used,
                "steps": trace_steps,
            },
            "error_message": "search_agent returned no sources; nothing to extract from.",
        }

    # ---------------------------------------------------------------
    # Step 2 – extract_agent
    # ---------------------------------------------------------------
    extract_step_index = len(trace_steps)
    try:
        extraction_result = extract_agent(sources=sources, task_prompt=task_prompt)
    except Exception as e:
        total_ms = int((time.time() - t0) * 1000)
        return {
            "status": "error",
            "query": user_query,
            "search_result": search_result,
            "extraction_result": None,
            "final_summary": None,
            "timing": {"estimated_total_ms": total_ms},
            "trace": {
                "tools_used": tools_used + ["extract_agent"],
                "steps": trace_steps
                + [
                    {
                        "step_index": extract_step_index,
                        "action": "Call extract_agent on sources with task_prompt",
                        "tool": "extract_agent",
                        "tool_input": f"sources=[{len(sources)} items], task_prompt={task_prompt!r}",
                        "tool_output_used": "exception",
                        "reasoning": "extract_agent failed; cannot continue to summary.",
                    }
                ],
            },
            "error_message": f"extract_agent raised an exception: {e}",
        }

    tools_used.append("extract_agent")
    trace_steps.append(
        {
            "step_index": extract_step_index,
            "action": "Call extract_agent on sources with task_prompt",
            "tool": "extract_agent",
            "tool_input": f"sources=[{len(sources)} items], task_prompt={task_prompt!r}",
            "tool_output_used": "full extract_agent JSON",
            "reasoning": "We need the structured extraction of only the relevant data practices before summarizing.",
        }
    )

    # ---------------------------------------------------------------
    # Step 3 – summary_agent
    # ---------------------------------------------------------------
    summary_step_index = len(trace_steps)
    try:
        final_summary = summary_agent(
            search_result=search_result,
            extraction_result=extraction_result,
            user_query=user_query,
        )
    except Exception as e:
        total_ms = int((time.time() - t0) * 1000)
        return {
            "status": "error",
            "query": user_query,
            "search_result": search_result,
            "extraction_result": extraction_result,
            "final_summary": None,
            "timing": {"estimated_total_ms": total_ms},
            "trace": {
                "tools_used": tools_used + ["summary_agent"],
                "steps": trace_steps
                + [
                    {
                        "step_index": summary_step_index,
                        "action": "Call summary_agent to synthesize final report",
                        "tool": "summary_agent",
                        "tool_input": "search_result + extraction_result + user_query",
                        "tool_output_used": "exception",
                        "reasoning": "summary_agent failed while synthesizing the final JSON summary.",
                    }
                ],
            },
            "error_message": f"summary_agent raised an exception: {e}",
        }

    tools_used.append("summary_agent")
    trace_steps.append(
        {
            "step_index": summary_step_index,
            "action": "Call summary_agent to synthesize final report",
            "tool": "summary_agent",
            "tool_input": "search_result + extraction_result + user_query",
            "tool_output_used": "full summary_agent JSON",
            "reasoning": "This step produces the final structured report with ratings, risks, and advice.",
        }
    )

    total_ms = int((time.time() - t0) * 1000)

    # ---------------------------------------------------------------
    # Final master JSON (exact structure you specified)
    # ---------------------------------------------------------------
    master = {
        "status": "success",
        "query": user_query,
        "search_result": search_result,
        "extraction_result": extraction_result,
        "final_summary": final_summary,
        "timing": {"estimated_total_ms": total_ms},
        "trace": {
            "tools_used": tools_used,
            "steps": trace_steps,
        },
        "error_message": None,
    }

    # Get the most recent trace from MLflow
    try:
        last_trace_id = mlflow.get_last_active_trace_id()
        trace = mlflow.get_trace(trace_id=last_trace_id)
        usage = (
            trace.info.token_usage
        )  # dict: {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...}

        # Optionally also get per-span usage if you want super detailed breakdown
        detailed_usage = []
        for span in trace.data.spans:
            span_usage = span.get_attribute("mlflow.chat.tokenUsage")
            if span_usage:
                cost_in = 0.3 / 1000000
                cost_out = 2.5 / 1000000

                input_cost = span_usage["input_tokens"] * cost_in
                output_cost = span_usage["output_tokens"] * cost_out
                detailed_usage.append(
                    {
                        "span_name": span.name,
                        "input_tokens": span_usage["input_tokens"],
                        "output_tokens": span_usage["output_tokens"],
                        "total_tokens": span_usage["total_tokens"],
                        "total_cost_usd": input_cost + output_cost,
                    }
                )
    except Exception:
        usage = None
        detailed_usage = []

    # Attach token usage into your final JSON
    # (you can put this under `timing` or a new top-level field)
    if isinstance(master, dict):
        master.setdefault("timing", {})
        master["timing"]["token_usage"] = usage
        master["timing"]["token_usage_detailed"] = detailed_usage

    return master


if __name__ == "__main__":
    res = run_master_pipeline("Anthropic")
    print()
    print("=" * 100)
    print(json.dumps(res))
