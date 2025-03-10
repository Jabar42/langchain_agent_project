#!/bin/bash

# Colores para la salida
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Iniciando pruebas de carga...${NC}"

# Crear directorio para los resultados si no existe
mkdir -p tests/load_tests/results

# Ejecutar prueba general
echo -e "\n${GREEN}Ejecutando prueba general de la API...${NC}"
k6 run tests/load_tests/main.js --out json=tests/load_tests/results/main_results.json

# Esperar un momento para que el sistema se estabilice
sleep 30

# Ejecutar prueba específica del chat
echo -e "\n${GREEN}Ejecutando prueba específica de la API de chat...${NC}"
k6 run tests/load_tests/chat_api.js --out json=tests/load_tests/results/chat_results.json

echo -e "\n${GREEN}Pruebas completadas. Los resultados se encuentran en tests/load_tests/results/${NC}" 