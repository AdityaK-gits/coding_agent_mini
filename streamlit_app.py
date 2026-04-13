import os
import streamlit as st
from pathlib import Path

from mini_dev_agent.orchestrator import MiniDevAgent
from mini_dev_agent.providers import build_provider

st.set_page_config(page_title="Mini Dev Agent", page_icon="🤖")

st.title("🤖 Mini Dev Agent")
st.markdown("An autonomous coding assistant that generates projects from natural language prompts.")

# Check for API keys
openai_key = bool(os.getenv("OPENAI_API_KEY"))
gemini_key = bool(os.getenv("GOOGLE_API_KEY"))
if not openai_key and not gemini_key:
    st.warning("⚠️ No API keys found (OPENAI_API_KEY or GOOGLE_API_KEY). Using mock provider (deterministic responses).")
elif not openai_key and gemini_key:
    st.info("ℹ️ Using Gemini provider (Google API key detected).")
elif openai_key and not gemini_key:
    st.info("ℹ️ Using OpenAI provider (OpenAI API key detected).")
else:
    st.info("ℹ️ Both API keys detected. Choose your preferred provider.")

with st.form("agent_form"):
    prompt = st.text_area(
        "Project Request",
        placeholder="e.g., Build a weather app with API integration",
        height=100
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        provider_options = ["auto", "mock"]
        if openai_key:
            provider_options.append("openai")
        if gemini_key:
            provider_options.append("gemini")
        provider = st.selectbox(
            "Provider",
            provider_options,
            help="auto uses available API keys, otherwise mock"
        )
    with col2:
        model = st.text_input("Model", placeholder="gpt-4 or gemini-1.5-flash", help="Model name for OpenAI or Gemini")
    with col3:
        reasoning_effort = st.selectbox(
            "Reasoning Effort",
            ["", "minimal", "low", "medium", "high"],
            help="OpenAI reasoning effort (not used for Gemini)"
        )

    workspace = st.text_input(
        "Workspace Path",
        value=str(Path.cwd()),
        help="Directory where generated project will be created"
    )

    submitted = st.form_submit_button("Generate Project")

if submitted and prompt.strip():
    with st.spinner("Running Mini Dev Agent..."):
        try:
            # Build provider
            provider_kwargs = {"mode": provider}
            if model:
                provider_kwargs["model"] = model
            if reasoning_effort:
                provider_kwargs["reasoning_effort"] = reasoning_effort

            llm_provider = build_provider(**provider_kwargs)

            # Create agent and run
            agent = MiniDevAgent(provider=llm_provider)
            report = agent.run(prompt=prompt, workspace=Path(workspace))

            # Display results
            st.success("Project generated successfully!")

            st.subheader("📋 Planned Steps")
            for step in report.steps:
                st.write(f"• {step.title}")

            st.subheader("📁 Generated Files")
            for file_path in report.generated_files:
                st.code(f"Created: {file_path}", language="text")

            if report.debug_actions:
                st.subheader("🔧 Debug Actions")
                for action in report.debug_actions:
                    st.write(f"• {action}")

            st.info(f"Provider used: {report.provider_name}")
            st.info(f"Output workspace: {workspace}")

        except Exception as e:
            st.error(f"Error running agent: {str(e)}")
            st.exception(e)

elif submitted:
    st.warning("Please enter a project request prompt.")

st.markdown("---")
st.markdown("Built with Mini Dev Agent - Autonomous coding assistant MVP")