import json, uuid
from pathlib import Path
import streamlit as st
from mars.graph.workflow import run_research
from mars.agents.advisor import ConfigurationAdvisor
from mars.observability.advisor_data import recent_observations
from mars.config.settings import get_settings

st.set_page_config(page_title="MARS Research Assistant",page_icon="🔎",layout="wide")
st.title("🔎 Multi-Agent Research System")
st.caption("MCP = tool access · LangGraph = orchestration · Langfuse = observability · Advisor = continuous improvement")

if "session_id" not in st.session_state: st.session_state.session_id=str(uuid.uuid4())

with st.sidebar:
    st.subheader("Research session")
    st.code(st.session_state.session_id, language="text")
    st.info("Agents: Research → Analysis → Verification → Memory")

query=st.text_area("Research question",placeholder="Compare the latest approaches to deploying LLM agents with MCP and explain the trade-offs.",height=120)
if st.button("Run research",type="primary",disabled=not query.strip()):
    with st.spinner("Agents are researching, analyzing, verifying, and saving memory…"):
        try:
            result=run_research(query.strip(),st.session_state.session_id)
            st.session_state.last_result=result
        except Exception as e:
            import traceback

            st.error(f"Research failed: {e}")
            st.code(traceback.format_exc())

if "last_result" in st.session_state:
    r=st.session_state.last_result
    st.subheader("Final answer")
    st.write(r.get("final_answer", "No answer produced."))
    st.subheader("Sources")
    for c in r.get("citations",[]): st.markdown(f"- [{c['title']}]({c['url']})")
    with st.expander("Agent state"):
        st.json({k:v for k,v in r.items() if k not in {"final_answer","citations"}})

st.divider()
st.header("Configuration Advisor")
st.caption("Human approval required. Recommendations are proposals, not automatic production changes.")
if st.button("Analyze recent Langfuse traces"):
    with st.spinner("Analyzing observability data…"):
        rec=ConfigurationAdvisor().analyze(recent_observations())
        st.session_state.recommendation=rec.model_dump()
if "recommendation" in st.session_state:
    rec=st.session_state.recommendation
    st.json(rec)
    if st.button("Approve recommendation"):
        path=Path(get_settings().approved_config_path)
        cfg=json.loads(path.read_text())
        if rec.get("model"): cfg["model"]=rec["model"]
        if rec.get("temperature") is not None: cfg["temperature"]=rec["temperature"]
        if rec.get("max_tokens") is not None: cfg["max_tokens"]=rec["max_tokens"]
        cfg.setdefault("prompts",{}).update(rec.get("prompt_changes",{}))
        cfg.setdefault("routing",{}).update(rec.get("routing_changes",{}))
        path.write_text(json.dumps(cfg,indent=2))
        st.success("Approved configuration updated. Redeploy/restart the service to apply it.")
