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
    st.markdown(r.get("final_answer") or "No answer produced.")
    st.subheader("Sources")
    citations=r.get("citations") or []
    if citations:
        for c in citations:
            st.markdown(f"- [{c.get('title','Source')}]({c.get('url','')})")
            snippet=(c.get("snippet") or "").strip()
            if snippet: st.caption(snippet[:300])
    else:
        # Fallback: derive sources from the raw search results.
        for s in r.get("search_results") or []:
            if isinstance(s,dict) and s.get("url"):
                st.markdown(f"- [{s.get('title','Source')}]({s['url']})")
    with st.expander("Agent trace (debug)"):
        # Show routing/agent metadata; heavy evidence blobs are summarized to keep the UI readable.
        trace={"query":r.get("query"),"session_id":r.get("session_id"),"next_agent":r.get("next_agent"),"errors":r.get("errors")}
        trace["search_results_count"]=len(r.get("search_results") or []) if isinstance(r.get("search_results"),list) else "(raw)"
        trace["citations_count"]=len(r.get("citations") or [])
        trace["analysis_chars"]=len(r.get("analysis") or "")
        trace["verification_chars"]=len(r.get("verification") or "")
        st.json(trace)

st.divider()
st.header("Configuration Advisor")
st.caption("Human approval required. Recommendations are proposals, not automatic production changes.")

# Show the currently approved configuration.
path=Path(get_settings().approved_config_path_abs)
with st.expander("Current approved configuration", expanded=False):
    try:
        st.json(json.loads(path.read_text()))
    except FileNotFoundError:
        st.warning(f"No approved config found at {path}")

# --- Manual configuration editing (no advisor approval required) ---
st.subheader("Manual configuration editor")
st.caption("Directly edit and save the approved configuration without going through the advisor.")
try:
    _cfg=json.loads(path.read_text())
except FileNotFoundError:
    _cfg=None
    st.warning(f"No approved config found at {path}; cannot edit manually.")
if _cfg is not None:
    with st.form("manual_config_form"):
        c1,c2,c3=st.columns(3)
        model=c1.text_input("Model",value=_cfg.get("model",""))
        temperature=c2.number_input("Temperature",min_value=0.0,max_value=2.0,step=0.05,value=float(_cfg.get("temperature",0.0)))
        max_tokens=c3.number_input("Max tokens",min_value=1,step=1,value=int(_cfg.get("max_tokens",1024)))
        colp,colr=st.columns(2)
        with colp:
            st.markdown("**Prompts**")
            prompts_txt=st.text_area("Prompts (JSON object)",value=json.dumps(_cfg.get("prompts",{}),indent=2),height=200)
        with colr:
            st.markdown("**Routing**")
            routing_txt=st.text_area("Routing (JSON object)",value=json.dumps(_cfg.get("routing",{}),indent=2),height=200)
        if st.form_submit_button("Save configuration",type="primary"):
            try:
                new_cfg=dict(_cfg)
                if model.strip(): new_cfg["model"]=model.strip()
                new_cfg["temperature"]=float(temperature)
                new_cfg["max_tokens"]=int(max_tokens)
                new_cfg["prompts"]=json.loads(prompts_txt)
                new_cfg["routing"]=json.loads(routing_txt)
                if not isinstance(new_cfg["prompts"],dict) or not isinstance(new_cfg["routing"],dict):
                    st.error("Prompts and Routing must be JSON objects ({}).")
                else:
                    path.write_text(json.dumps(new_cfg,indent=2))
                    st.success("Configuration saved manually. Redeploy/restart the service to apply it.")
                    st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
            except Exception as e:
                st.error(f"Failed to save configuration: {e}")

if st.button("Analyze recent Langfuse traces"):
    with st.spinner("Analyzing observability data…"):
        rec=ConfigurationAdvisor().analyze(recent_observations())
        st.session_state.recommendation=rec.model_dump()
if "recommendation" in st.session_state:
    rec=st.session_state.recommendation
    st.subheader("Advisor recommendation")
    if rec.get("model"): st.markdown(f"**Model:** `{rec['model']}`")
    if rec.get("temperature") is not None: st.markdown(f"**Temperature:** {rec['temperature']}")
    if rec.get("max_tokens") is not None: st.markdown(f"**Max tokens:** {rec['max_tokens']}")
    if rec.get("prompt_changes"): st.markdown("**Prompt changes:** " + json.dumps(rec["prompt_changes"], indent=2))
    if rec.get("routing_changes"): st.markdown("**Routing changes:** " + json.dumps(rec["routing_changes"], indent=2))
    st.markdown(f"**Rationale:** {rec.get('rationale','—')}")
    st.markdown(f"**Expected impact:** {rec.get('expected_impact','—')}")
    st.markdown(f"**Risk:** {rec.get('risk','—')}")
    if st.button("Approve recommendation"):
        cfg=json.loads(path.read_text())
        if rec.get("model"): cfg["model"]=rec["model"]
        if rec.get("temperature") is not None: cfg["temperature"]=rec["temperature"]
        if rec.get("max_tokens") is not None: cfg["max_tokens"]=rec["max_tokens"]
        cfg.setdefault("prompts",{}).update(rec.get("prompt_changes",{}))
        cfg.setdefault("routing",{}).update(rec.get("routing_changes",{}))
        path.write_text(json.dumps(cfg,indent=2))
        st.success("Approved configuration updated. Redeploy/restart the service to apply it.")
