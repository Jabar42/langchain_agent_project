#!/bin/bash

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Instalando Git hooks...${NC}"

# Crear directorio de hooks si no existe
mkdir -p .git/hooks

# Copiar hooks
cp .github/hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

# Instalar dependencias de desarrollo necesarias
echo -e "${YELLOW}📥 Instalando dependencias de desarrollo...${NC}"
pip install black flake8 mypy pytest

echo -e "${GREEN}✅ Hooks instalados exitosamente${NC}"
echo -e "${YELLOW}ℹ️  Los siguientes hooks están activos:${NC}"
echo "  - pre-commit: Verifica formato, estilo, tipos y tests"

echo -e "\n${YELLOW}📝 Recuerda seguir las convenciones de commit:${NC}"
echo "  <tipo>(<alcance>): <descripción>"
echo "  Ejemplo: feat(auth): implementar autenticación JWT" 