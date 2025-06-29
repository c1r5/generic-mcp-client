import logging


from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent


logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self, agent: Agent) -> None:
        self.runner = InMemoryRunner(app_name=agent.name, agent=agent)
        self.agent = agent
        
        pass
    
    async def create_session(self):
        self.session = await self.runner.session_service.create_session(app_name=self.agent.name, user_id='c1r5dev')

    async def ask(self, content: str):
        try:
            async for response in self.runner.run_async(user_id=self.session.user_id,session_id=self.session.id,new_message=UserContent(content)):
                if not response.is_final_response():
                    continue
                
                if response.content is None:
                    logger.warning("Não foi possivel gerar a resposta")
                    yield "Não foi possivel gerar a resposta"
                
                if response.content.parts is None or []: # type: ignore
                    logger.warning("Não foi possivel obter o conteudo da resposta")
                    yield "Não foi possivel obter o conteudo da resposta"

                yield '\n'.join([part.text for part in response.content.parts])   # type: ignore
            
        except Exception as e:
            logger.error("Um erro ocorreu ao tentar gerar resposta", exc_info=e)
            
            
    async def close(self):
        await self.runner.close()