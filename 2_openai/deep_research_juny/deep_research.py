import streamlit as st
import asyncio
from dotenv import load_dotenv
from research_manager import ResearchManager

load_dotenv(override=True)

manager = ResearchManager()

# Estado inicial de la app
if "step" not in st.session_state:
    st.session_state.step = "query"
if "query" not in st.session_state:
    st.session_state.query = ""
if "clarification_questions" not in st.session_state:
    st.session_state.clarification_questions = []
if "clarification_answers" not in st.session_state:
    st.session_state.clarification_answers = []
if "motivos" not in st.session_state:
    st.session_state.motivos = []


async def generate_questions(query: str):
    return await manager.generate_clarification_questions(query)


async def run_research(query: str, motivos: list[str]):
    async for chunk in manager.run(query, motivos):
        yield chunk


st.title("🔎 Búsqueda Profunda con Clarificación")

if st.session_state.step == "query":
    st.subheader("1. Indica el tema de investigación")
    query = st.text_input("¿Sobre qué tema te gustaría investigar?")
    # motivo1 = st.text_input("Motivo/Contexto 1")
    # motivo2 = st.text_input("Motivo/Contexto 2")
    # motivo3 = st.text_input("Motivo/Contexto 3")

    if st.button("Generar preguntas de clarificación"):
        if query.strip():
            st.session_state.query = query
            # st.session_state.motivos = [motivo1, motivo2, motivo3]
            # Ejecutamos agente para generar preguntas
            # Mostrar mensaje mientras se generan las preguntas
            placeholder = st.empty()
            placeholder.info("⏳ Generando preguntas de aclaración...")

            st.session_state.clarification_questions = asyncio.run(
                generate_questions(query)
            )
            st.session_state.step = "clarification"
            st.rerun()


elif st.session_state.step == "clarification":
    st.subheader("2. Responde estas preguntas para afinar la investigación")
    answers = []
    for i, q in enumerate(st.session_state.clarification_questions):
        answers.append(st.text_area(f"Pregunta {i+1}: {q}"))

    if st.button("Confirmar respuestas y comenzar investigación"):
        st.session_state.clarification_answers = answers
        st.session_state.step = "research"
        st.rerun()


elif st.session_state.step == "research":
    st.subheader("3. Progreso de la investigación")

    motivos_ext = st.session_state.motivos + [
        f"Respuesta aclaratoria {i+1}: {a}"
        for i, a in enumerate(st.session_state.clarification_answers)
        if a.strip()
    ]

    placeholder = st.empty()
    st.session_state.final_report = None

    async def stream_and_capture():
        async for chunk in manager.run(st.session_state.query, motivos_ext):
            if isinstance(chunk, str):
                # 🔑 mostrar solo el último mensaje (sin acumular)
                placeholder.markdown(chunk)
            elif isinstance(chunk, dict) and "final_report" in chunk:
                st.session_state.final_report = chunk["final_report"]

    asyncio.run(stream_and_capture())

    if st.session_state.final_report:
        st.subheader("📑 Informe final")
        st.markdown(st.session_state.final_report.markdown_report)

