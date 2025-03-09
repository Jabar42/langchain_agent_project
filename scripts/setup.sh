#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Configurando el proyecto LangChain Agent...${NC}"

# Verificar Python
echo -e "\n${YELLOW}Verificando versión de Python...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    exit 1
fi

# Crear entorno virtual
echo -e "\n${YELLOW}Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo -e "\n${YELLOW}Instalando dependencias...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: No se pudieron instalar las dependencias${NC}"
    exit 1
fi

# Crear directorios necesarios
echo -e "\n${YELLOW}Creando estructura de directorios...${NC}"
mkdir -p logs data/cache

# Configurar variables de entorno
echo -e "\n${YELLOW}Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}Archivo .env creado. Por favor, configura tus claves API${NC}"
fi

# Verificar configuración de Git
echo -e "\n${YELLOW}Verificando configuración de Git...${NC}"
if [ ! -d .git ]; then
    git init
    git add .
    git commit -m "Initial commit"
fi

# Configurar pre-commit hooks
echo -e "\n${YELLOW}Configurando pre-commit hooks...${NC}"
pip install pre-commit
pre-commit install

echo -e "\n${GREEN}¡Configuración completada!${NC}"
echo -e "\n${YELLOW}Próximos pasos:${NC}"
echo "1. Edita el archivo .env con tus claves API"
echo "2. Ejecuta 'make test' para verificar la instalación"
echo "3. Ejecuta 'make run-web' para iniciar la interfaz web" 