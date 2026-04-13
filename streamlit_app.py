import streamlit as st
from pathlib import Path

from mini_dev_agent.orchestrator import MiniDevAgent
from mini_dev_agent.providers import build_provider

st.set_page_config(page_title="Mini Dev Agent", page_icon="🤖")

st.title("🤖 Mini Dev Agent")
st.markdown("An autonomous coding assistant that generates projects from natural language prompts.")

with st.form("agent_form"):
    prompt = st.text_area(
        "Project Request",
        placeholder="e.g., Build a login system with JWT auth",
        height=100
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        provider = st.selectbox(
            "Provider",
            ["auto", "mock", "openai"],
            help="auto uses OpenAI if OPENAI_API_KEY is set, otherwise mock"
        )
    with col2:
        model = st.text_input("Model", placeholder="gpt-4", help="OpenAI model name")
    with col3:
        reasoning_effort = st.selectbox(
            "Reasoning Effort",
            ["", "minimal", "low", "medium", "high"],
            help="OpenAI reasoning effort"
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