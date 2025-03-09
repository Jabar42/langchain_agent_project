from typing import Optional, Dict, Any
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import logging
from ...agents.multi_model_agent import MultiModelAgent
from ...utils.exceptions import TelegramError, ConfigurationError
import os

class TelegramBot:
    """Telegram bot connector for the AI agent platform."""
    
    def __init__(self, agent: MultiModelAgent):
        self.agent = agent
        self.token = self._get_token()
        self.admin_id = self._get_admin_id()
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()
        self._setup_logging()
        
    def _get_token(self) -> str:
        """Get Telegram bot token from environment."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ConfigurationError("TELEGRAM_BOT_TOKEN not found in environment")
        return token
    
    def _get_admin_id(self) -> Optional[int]:
        """Get admin user ID from environment."""
        admin_id = os.getenv("TELEGRAM_ADMIN_USER_ID")
        return int(admin_id) if admin_id else None
    
    def _setup_logging(self):
        """Configure logging for the bot."""
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_handlers(self):
        """Set up command and message handlers."""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("ask", self._ask_command))
        self.application.add_handler(CommandHandler("compare", self._compare_command))
        self.application.add_handler(CommandHandler("models", self._models_command))
        self.application.add_handler(CommandHandler("configure", self._configure_command))
        
        # Manejo de mensajes generales
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        
        # Manejo de errores
        self.application.add_error_handler(self._error_handler)
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = (
            "👋 ¡Bienvenido al Bot de AI Multi-Model!\n\n"
            "Puedes usar los siguientes comandos:\n"
            "/ask [pregunta] - Realizar una consulta\n"
            "/compare [pregunta] - Comparar respuestas de diferentes modelos\n"
            "/models - Ver modelos disponibles\n"
            "/configure - Configurar preferencias\n"
            "/help - Ver ayuda detallada"
        )
        await update.message.reply_text(welcome_message)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "📚 Ayuda Detallada\n\n"
            "Comandos disponibles:\n\n"
            "1️⃣ /ask [pregunta]\n"
            "   Realiza una consulta al mejor modelo disponible\n"
            "   Ejemplo: /ask ¿Cómo funciona la fotosíntesis?\n\n"
            "2️⃣ /compare [pregunta]\n"
            "   Compara respuestas de diferentes modelos\n"
            "   Ejemplo: /compare ¿Qué es el machine learning?\n\n"
            "3️⃣ /models\n"
            "   Muestra los modelos disponibles y su estado\n\n"
            "4️⃣ /configure\n"
            "   Configura tus preferencias de uso\n\n"
            "❓ Para cualquier duda adicional, contacta al administrador"
        )
        await update.message.reply_text(help_message)
    
    async def _ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command."""
        if not context.args:
            await update.message.reply_text("❌ Por favor, incluye una pregunta después de /ask")
            return
            
        question = " ".join(context.args)
        try:
            # Enviar mensaje de "escribiendo..."
            await update.message.reply_chat_action("typing")
            
            # Procesar la pregunta con el agente
            response = await self.agent.process_message(question)
            
            # Enviar respuesta
            await update.message.reply_text(response["best_response"])
            
        except Exception as e:
            await self._handle_error(update, str(e))
    
    async def _compare_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /compare command."""
        if not context.args:
            await update.message.reply_text("❌ Por favor, incluye una pregunta después de /compare")
            return
            
        question = " ".join(context.args)
        try:
            # Enviar mensaje de "escribiendo..."
            await update.message.reply_chat_action("typing")
            
            # Obtener respuestas de múltiples modelos
            result = await self.agent.compare_responses(
                question,
                models=self.agent.model_manager.get_default_models()
            )
            
            # Formatear respuesta comparativa
            comparison_text = self._format_comparison(result)
            await update.message.reply_text(comparison_text)
            
        except Exception as e:
            await self._handle_error(update, str(e))
    
    async def _models_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /models command."""
        try:
            models = self.agent.model_manager.list_available_models()
            models_text = "🤖 Modelos Disponibles:\n\n"
            for model in models:
                models_text += f"• {model}\n"
            await update.message.reply_text(models_text)
        except Exception as e:
            await self._handle_error(update, str(e))
    
    async def _configure_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /configure command."""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("⚠️ Solo el administrador puede usar este comando")
            return
            
        # TODO: Implementar configuración
        await update.message.reply_text("🔧 Configuración no implementada aún")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle non-command messages."""
        # Tratar mensajes normales como consultas al agente
        try:
            await update.message.reply_chat_action("typing")
            response = await self.agent.process_message(update.message.text)
            await update.message.reply_text(response["best_response"])
        except Exception as e:
            await self._handle_error(update, str(e))
    
    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot."""
        self.logger.error(f"Error: {context.error}")
        if update and isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ha ocurrido un error. Por favor, intenta de nuevo más tarde."
            )
    
    async def _handle_error(self, update: Update, error_message: str):
        """Handle and log errors."""
        self.logger.error(f"Error in update {update}: {error_message}")
        await update.message.reply_text(
            f"❌ Error: {error_message}\nPor favor, intenta de nuevo."
        )
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return self.admin_id and user_id == self.admin_id
    
    def _format_comparison(self, result: Dict[str, Any]) -> str:
        """Format comparison results for Telegram message."""
        text = "🔄 Comparación de Respuestas:\n\n"
        
        for model_id, response in result["responses"].items():
            evaluation = result["evaluations"][model_id]
            text += f"📝 Modelo: {model_id}\n"
            text += f"Respuesta: {response[:200]}...\n"
            text += f"Puntuación: {evaluation['accuracy']:.2f}\n\n"
            
        text += f"🏆 Mejor modelo: {result['best_response']}\n"
        return text
    
    async def start(self):
        """Start the bot."""
        try:
            self.logger.info("Starting bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.run_polling()
        except Exception as e:
            raise TelegramError(f"Error starting bot: {str(e)}")
    
    async def stop(self):
        """Stop the bot."""
        try:
            self.logger.info("Stopping bot...")
            await self.application.stop()
        except Exception as e:
            raise TelegramError(f"Error stopping bot: {str(e)}") 