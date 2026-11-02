"""Smoke validation: train 3 cancel examples, inspect skill/guidelines, compare critic scores."""
from __future__ import annotations

import logging
import os
import ssl
from pathlib import Path

# Local/corporate SSL interception breaks verify in this shell.
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

import httpx
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv(override=True)

from general import clean_agentic_memory, initialize_logging
from harness_agent.harness import AgentHarness

initialize_logging(logging.INFO)

_http = httpx.Client(verify=False)


def get_agent_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        http_client=_http,
    )


def get_judge_llm():
    return ChatOpenAI(
        model="gpt-5-nano",
        reasoning_effort="low",
        max_retries=3,
        timeout=60,
        http_client=_http,
    )


class ResponseEvaluatorSchema(BaseModel):
    score: int = Field(description="Integer 1-10 fidelity to the reference.")
    comment: str = Field(description="Brief explanation of match vs gaps.")


def critic_score(query: str, agent_response: str, reference_response: str) -> dict:
    system_eval_prompt = "You are an Expert Customer Service Agent Evaluator."
    eval_prompt = f"""Score the agent response from 1 to 10 against the reference answer.
Score meaning:
- 1 = very poor match to the reference (wrong or unhelpful)
- 5 = partial match (some overlap, important gaps remain)
- 10 = excellent match to the reference (same kind of help and the important information)

IMPORTANT:
- Be strict. Do not give a high score only because the answer is polite or generally helpful.
- Prefer answers that match the reference's response type and include its important information (including specific steps or placeholders when the reference has them).
- Avoid rewarding invented unsupported procedures.
- Give a short comment on what matched and what was missing.

User query:
{query}

Reference answer:
{reference_response}

Agent response:
{agent_response}"""
    model = get_judge_llm()
    result = model.with_structured_output(ResponseEvaluatorSchema).invoke(
        [SystemMessage(system_eval_prompt), HumanMessage(eval_prompt)]
    )
    return {"score": result.score, "comment": result.comment}


def run_and_score(rows: pd.DataFrame, training: bool, memory_disabled: bool):
    scores = []
    for row in rows.itertuples():
        harness = AgentHarness(
            model=get_agent_llm(),
            training_dataset=rows,
            training_mode=training,
            agentic_memory_disabled=memory_disabled,
        )
        response = harness.invoke(row.instruction)
        judged = critic_score(row.instruction, response["text"], row.response)
        scores.append(judged["score"])
        print(f"  score={judged['score']} | q={row.instruction[:70]!r}")
        print(f"    comment={judged['comment'][:160]}")
    return scores


def main():
    df = pd.read_csv("customer-dataset.csv").rename(columns={"Unnamed: 0": "id"})
    cancel = (
        df[df["intent"] == "cancel_order"]
        .drop_duplicates(subset=["instruction"])
        .sample(n=6, random_state=42)
        .reset_index(drop=True)
    )
    train_df = cancel.iloc[:3].copy()
    test_df = cancel.iloc[3:6].copy()
    print(f"train={len(train_df)} test={len(test_df)}")

    clean_agentic_memory()

    print("\n=== BASELINE (memory off, test) ===")
    baseline_scores = run_and_score(test_df, training=False, memory_disabled=True)

    clean_agentic_memory()

    print("\n=== TRAIN (memory on) ===")
    for row in train_df.itertuples():
        harness = AgentHarness(
            model=get_agent_llm(),
            training_dataset=train_df,
            training_mode=True,
            agentic_memory_disabled=False,
        )
        harness.invoke(row.instruction)
        print(f"  trained on: {row.instruction[:70]!r}")

    print("\n=== SKILLS ===")
    skills_root = Path("skills")
    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
        print(f"--- {skill_dir.name} ---")
        print(text)
        has_steps = any(token in text for token in ["1.", "2.", "- ", "{{"])
        has_placeholder = "{{" in text
        cautious_only = (
            "do not provide" in text.lower()
            and "step" in text.lower()
            and "{{" not in text
        )
        print(
            f"[check] placeholders={has_placeholder} looks_procedural={has_steps} cautious_only={cautious_only}"
        )

    print("\n=== AGENT.md ===")
    agent_md = Path("AGENT.md").read_text(encoding="utf-8")
    print(agent_md if agent_md.strip() else "(empty)")
    bans_procedures = any(
        phrase in agent_md.lower()
        for phrase in [
            "ban portal",
            "avoid unsupported procedures",
            "don't invent contact",
        ]
    )
    allows_skill = "skill" in agent_md.lower()
    print(f"[check] mentions_skill={allows_skill} likely_bans_procedures={bans_procedures}")

    print("\n=== POST-TRAIN (memory on, test) ===")
    post_scores = run_and_score(test_df, training=False, memory_disabled=False)

    print("\n=== SUMMARY ===")
    print(f"baseline avg: {sum(baseline_scores)/len(baseline_scores):.2f} scores={baseline_scores}")
    print(f"post_train avg: {sum(post_scores)/len(post_scores):.2f} scores={post_scores}")
    print(
        f"delta: {sum(post_scores)/len(post_scores) - sum(baseline_scores)/len(baseline_scores):+.2f}"
    )


if __name__ == "__main__":
    main()
