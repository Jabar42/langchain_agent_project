import asyncio
import logging
from dotenv import load_dotenv
from ...agents.multi_model_agent import MultiModelAgent
from ...models.model_manager import ModelManager
from .telegram_bot import TelegramBot
from langchain.chat_models import ChatOpenAI

async def main():
    # Configurar logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    try:
        # Cargar variables de entorno
        load_dotenv()

        # Inicializar componentes
        logger.info("Inicializando componentes...")
        
        # Crear modelo por defecto
        default_model = ChatOpenAI(temperature=0.7)
        
        # Inicializar MultiModelAgent
        agent = MultiModelAgent(default_model)
        
        # Crear y ejecutar bot
        bot = TelegramBot(agent)
        
        logger.info("Iniciando bot...")
        await bot.start()

    except Exception as e:
        logger.error(f"Error al iniciar el bot: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 