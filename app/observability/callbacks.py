from typing import Any, List
from langchain_core.callbacks.base import BaseCallbackHandler
from ..logging import logger


class ResearchLoggingHandler(BaseCallbackHandler):
    def __init__(self, trace: str | None = None) -> None:
        self.trace = trace or "research"
        self.step = 0

    def on_chain_start(self, serialized: dict[str, Any] | None, inputs: dict[str, Any] | None, **kwargs: Any) -> None:
        name = None
        if isinstance(serialized, dict):
            name = serialized.get("name") or serialized.get("id")
        if not name:
            name = "chain"
        keys = list(inputs.keys()) if isinstance(inputs, dict) else []
        logger.info(f"[{self.trace}] chain:start name={name} inputs_keys={keys}")

    def on_chain_end(self, outputs: dict[str, Any] | None, **kwargs: Any) -> None:
        keys = list(outputs.keys()) if isinstance(outputs, dict) else []
        logger.info(f"[{self.trace}] chain:end outputs_keys={keys}")

    def on_llm_start(self, serialized: dict[str, Any] | None, prompts: List[str] | None, **kwargs: Any) -> None:
        n = len(prompts[0]) if prompts and len(prompts) > 0 else 0
        logger.info(f"[{self.trace}] llm:start prompt_len={n}")

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        logger.info(f"[{self.trace}] llm:end")

    def on_tool_start(self, serialized: dict[str, Any] | None, input_str: Any, **kwargs: Any) -> None:
        self.step += 1
        name = None
        if isinstance(serialized, dict):
            name = serialized.get("name") or serialized.get("id")
        if not name:
            name = "tool"
        try:
            snippet_raw = input_str if isinstance(input_str, str) else str(input_str)
        except Exception:
            snippet_raw = "<unserializable input>"
        snippet = snippet_raw if len(snippet_raw) <= 300 else snippet_raw[:297] + "..."
        logger.info(f"[{self.trace}] step={self.step} tool:start name={name} input={snippet}")

    def on_tool_end(self, output: Any, **kwargs: Any) -> None:
        try:
            out_raw = output if isinstance(output, str) else str(output)
        except Exception:
            out_raw = "<unserializable output>"
        snippet = out_raw if len(out_raw) <= 300 else out_raw[:297] + "..."
        logger.info(f"[{self.trace}] step={self.step} tool:end output={snippet}")

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        logger.error(f"[{self.trace}] step={self.step} tool:error {error}")


__all__ = ["ResearchLoggingHandler"]
