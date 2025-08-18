# from agents import Runner, trace, gen_trace_id
# from search_agent import search_agent
# from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
# from writer_agent import writer_agent, ReportData
# from email_agent import email_agent
# import asyncio
# from clarification_agent import clarification_agent 

# class ResearchManager:

#     async def run(self, query: str, motivos: list[str]):
#         trace_id = gen_trace_id()
#         with trace("Investigación", trace_id=trace_id):
#             print(f"Ver traza: https://platform.openai.com/traces/trace?trace_id={trace_id}")
#             yield f"Ver traza: https://platform.openai.com/traces/trace?trace_id={trace_id}"
#             print("Iniciando investigación...")

#             # Incluye los motivos en la consulta para el planificador
#             motivos_texto = "\n".join(f"Motivo {i+1}: {m}" for i, m in enumerate(motivos) if m.strip())
#             consulta_con_motivos = f"{query}\n{motivos_texto}"

#             search_plan = await self.plan_searches(consulta_con_motivos)
#             yield "Búsquedas planificadas, iniciando búsqueda..."     
#             search_results = await self.perform_searches(search_plan)
#             yield "Búsquedas completas, escribiendo informe..."
#             report = await self.write_report(query, search_results)
#             yield "Informe escrito, enviando correo electrónico..."
#             await self.send_email(report)
#             yield "Correo electrónico enviado, investigación completa"


#     async def generate_clarification_questions(self, query: str) -> list[str]:
#             """Genera 3 preguntas de aclaración sobre la consulta"""
#             result = await Runner.run(
#                 clarification_agent,
#                 query
#             )
#             # Asegúrate de que el agente devuelve una lista de 3 preguntas (como lista o texto separada por líneas)
#             output = result.final_output
#             if isinstance(output, str):
#                 # Si devuelve un string separado por saltos de línea
#                 return [q.strip("-• ") for q in output.strip().split("\n") if q.strip()]
#             elif isinstance(output, list):
#                 return output
#             else:
#                 raise ValueError("El formato de salida del agente de aclaración no es válido")

#     async def plan_searches(self, query: str) -> WebSearchPlan:
#         """ Planifica las búsquedas a realizar para la consulta """
#         print("Planificando búsquedas...")
#         result = await Runner.run(
#             planner_agent,
#             f"Consulta: {query}",
#         )
#         print(f"Se realizarán {len(result.final_output.searches)} búsquedas")
#         return result.final_output_as(WebSearchPlan)

#     async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
#         """ Realiza las búsquedas para la consulta """
#         print("Buscando...")
#         num_completed = 0
#         tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
#         results = []
#         for task in asyncio.as_completed(tasks):
#             result = await task
#             if result is not None:
#                 results.append(result)
#             num_completed += 1
#             print(f"Buscando... {num_completed}/{len(tasks)} completadas")
#         print("Búsqueda completada")
#         return results

#     async def search(self, item: WebSearchItem) -> str | None:
#         """ Realiza una búsqueda para la consulta """
#         input = f"Término de búsqueda: {item.query}\nRazón para buscar: {item.reason}"
#         try:
#             result = await Runner.run(
#                 search_agent,
#                 input,
#             )
#             return str(result.final_output)
#         except Exception:
#             return None

#     async def write_report(self, query: str, search_results: list[str]) -> ReportData:
#         """ Escribe el informe para la consulta """
#         print("Pensando en el informe...")
#         input = f"Consulta original: {query}\nResultados de búsqueda resumidos: {search_results}"
#         result = await Runner.run(
#             writer_agent,
#             input,
#         )

#         print("Informe escrito")
#         return result.final_output_as(ReportData)
    
#     async def send_email(self, report: ReportData) -> None:
#         print("Escribiendo correo electrónico...")
#         result = await Runner.run(
#             email_agent,
#             report.markdown_report,
#         )
#         print("Correo electrónico enviado")
#         return report


# research_manager.py
from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from clarification_agent import clarification_agent
from structure import ClarificationQuestions
import asyncio
from pydantic import ValidationError

class ResearchManager:

    async def generate_clarification_questions(self, query: str) -> list[str]:
        """Genera 3 preguntas de aclaración sobre la consulta"""
        result = await Runner.run(clarification_agent, query)
        output = result.final_output

        if isinstance(output, str):
            preguntas = [q.strip("-• \n") for q in output.strip().split("\n") if q.strip()]
        elif isinstance(output, list):
            preguntas = output
        else:
            raise ValueError("El formato de salida del agente de aclaración no es válido")

        try:
            validated = ClarificationQuestions(questions=preguntas)
            return validated.questions
        except ValidationError as e:
            raise ValueError(f"Error validando las preguntas de aclaración: {e}")

    async def run(self, query: str, motivos: list[str]):
        trace_id = gen_trace_id()
        with trace("Investigación", trace_id=trace_id):
            print(f"Ver traza: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"Ver traza: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Iniciando investigación...")

            motivos_texto = "\n".join(f"Motivo {i+1}: {m}" for i, m in enumerate(motivos) if m.strip())
            consulta_con_motivos = f"{query}\n{motivos_texto}"

            search_plan = await self.plan_searches(consulta_con_motivos)
            yield "Búsquedas planificadas, iniciando búsqueda..."     
            search_results = await self.perform_searches(search_plan)
            yield "Búsquedas completas, escribiendo informe..."
            report = await self.write_report(query, search_results, motivos)
            yield "Informe escrito, enviando correo electrónico..."
            await self.send_email(report)
            yield "Correo electrónico enviado, investigación completa"
            yield {"final_report": report}

    async def plan_searches(self, query: str) -> WebSearchPlan:
        print("Planificando búsquedas...")
        result = await Runner.run(planner_agent, f"Consulta: {query}")
        print(f"Se realizarán {len(result.final_output.searches)} búsquedas")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        print("Buscando...")
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for idx, task in enumerate(asyncio.as_completed(tasks), 1):
            result = await task
            if result is not None:
                results.append(result)
            print(f"Buscando... {idx}/{len(tasks)} completadas")
        print("Búsqueda completada")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        input = f"Término de búsqueda: {item.query}\nRazón para buscar: {item.reason}"
        try:
            result = await Runner.run(search_agent, input)
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str], motivos: list[str]) -> ReportData:
        print("Pensando en el informe...")
        input = (
            f"Consulta original: {query}\n"
            f"Contexto adicional:\n"
            f"1. {motivos[0]}\n2. {motivos[1]}\n3. {motivos[2]}\n"
            f"Resultados de búsqueda resumidos: {search_results}"
        )
        result = await Runner.run(writer_agent, input)
        print("Informe escrito")
        return result.final_output_as(ReportData)

    async def send_email(self, report: ReportData) -> None:
        print("Escribiendo correo electrónico...")
        await Runner.run(email_agent, report.markdown_report)
        print("Correo electrónico enviado")
