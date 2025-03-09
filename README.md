# AI Agent Multi-Model Platform

## Descripción
Plataforma de agente IA que integra múltiples modelos de lenguaje con capacidades de interacción a través de Telegram y Threads, permitiendo comparación y evaluación de respuestas entre diferentes modelos.

## Características Principales
- 🤖 Integración con múltiples modelos de lenguaje (OpenAI, Anthropic, Cohere, Google)
- 📱 Conectores para Telegram y Threads
- 🔄 Modo de comparación de respuestas entre modelos
- 📊 Sistema de evaluación y selección de mejores respuestas
- 🌐 Interfaz web para gestión y monitoreo

## Arquitectura del Sistema

### Componentes Principales
1. **Core Agent System** (`src/agents/`)
   - `base_agent.py`: Agente base con funcionalidades comunes
   - `multi_model_agent.py`: Agente especializado en consultas multi-modelo
   - `response_evaluator.py`: Sistema de evaluación de respuestas

2. **Model Connectors** (`src/models/`)
   - `model_manager.py`: Gestión de diferentes modelos de LLM
   - `model_router.py`: Enrutamiento de consultas a modelos específicos
   - Adaptadores para cada proveedor de LLM

3. **Platform Connectors** (`src/connectors/`)
   - Telegram: Bot y gestión de interacciones
   - Threads: API client y gestión de publicaciones
   - Interfaces comunes para mensajería

4. **Evaluation System** (`src/evaluators/`)
   - Métricas de evaluación
   - Criterios de comparación
   - Sistema de ranking

5. **Web Interface** (`src/web/`)
   - Dashboard de administración
   - Visualización de métricas
   - Configuración del sistema

## Flujo de Trabajo
1. Recepción de consultas (Telegram/Threads/Web)
2. Procesamiento y distribución a modelos
3. Recolección de respuestas
4. Evaluación y comparación
5. Selección de mejor respuesta
6. Envío de respuesta al usuario

## Configuración del Entorno
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## Variables de Entorno Necesarias
```
# API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
COHERE_API_KEY=
GOOGLE_API_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=

# Threads
THREADS_USERNAME=
THREADS_PASSWORD=

# Configuración
DEFAULT_MODEL=gpt-4
EVALUATION_CRITERIA=accuracy,coherence,relevance
```

## Uso del Sistema

### Modo Comparación
```python
from agents.multi_model_agent import MultiModelAgent

agent = MultiModelAgent()
responses = agent.compare_responses(
    "¿Cuál es la mejor manera de implementar un sistema de caché?",
    models=["gpt-4", "claude-2", "command-nightly"]
)
```

### Bot de Telegram
El bot responderá a comandos como:
- `/ask [pregunta]` - Consulta estándar
- `/compare [pregunta]` - Modo comparación
- `/models` - Lista modelos disponibles
- `/configure` - Configura preferencias

## Evaluación de Respuestas
El sistema evalúa las respuestas basándose en:
- Precisión técnica
- Coherencia
- Relevancia
- Tiempo de respuesta
- Uso de recursos

## Próximos Pasos
- [ ] Implementación de sistema de caché
- [ ] Mejora del sistema de evaluación
- [ ] Añadir más modelos de lenguaje
- [ ] Optimización de costos
- [ ] Implementación de tests automatizados

## Contribución
Las contribuciones son bienvenidas. Por favor, revisa las guías de contribución antes de enviar un PR.

## Licencia
MIT License 