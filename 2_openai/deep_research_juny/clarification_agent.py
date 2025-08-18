
# clarification_agent.py
from agents import Agent

clarification_agent = Agent(
    name="Agente de aclaración",
    instructions=(
        "Eres un asistente experto en clarificar consultas de investigación. "
        "Dada una consulta, responde con exactamente 3 preguntas de aclaración en texto plano, cada una en una nueva línea. "
        "Ejemplo:\n"
        "- ¿Qué aspecto específico del tema te interesa?\n"
        "- ¿Cuál es el propósito de esta investigación?\n"
        "- ¿Hay algún contexto o experiencia previa relacionada?"
    ),
    model="gpt-4o-mini"
)
