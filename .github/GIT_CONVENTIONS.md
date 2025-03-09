# 🔄 Convenciones Git

## 📝 Formato de Commits

### Estructura
```
<tipo>(<alcance>): <descripción corta>

[descripción larga opcional]

[issues relacionados opcional]
```

### Tipos de Commit
- 🎯 `feat`: Nueva característica
- 🐛 `fix`: Corrección de error
- 📚 `docs`: Cambios en documentación
- 💅 `style`: Cambios de formato (espacios, puntos, etc)
- ♻️ `refactor`: Refactorización de código
- ⚡ `perf`: Mejoras de rendimiento
- 🧪 `test`: Añadir o modificar tests
- 🛠️ `build`: Cambios en sistema de build
- 👷 `ci`: Cambios en integración continua
- 🔧 `chore`: Tareas de mantenimiento

### Ejemplos
```
feat(auth): implementar autenticación con JWT

- Añadida generación de tokens JWT
- Implementada validación de tokens
- Agregado middleware de autenticación

Closes #123
```

## 🌿 Branching Strategy

### Ramas Principales
- `main`: Código en producción
- `develop`: Desarrollo principal
- `release/*`: Preparación para release
- `hotfix/*`: Correcciones urgentes

### Ramas de Característica
```
feature/[issue-id]-breve-descripcion
```

### Ramas de Corrección
```
fix/[issue-id]-breve-descripcion
```

## 🔄 Workflow

1. **Crear Nueva Característica**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/123-nueva-caracteristica
   ```

2. **Commits Regulares**
   ```bash
   git add .
   git commit -m "feat(component): add new feature"
   ```

3. **Actualizar desde Develop**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/123-nueva-caracteristica
   git rebase develop
   ```

4. **Preparar para PR**
   ```bash
   git push origin feature/123-nueva-caracteristica
   ```

## 🎯 Pull Request Template
```markdown
## Descripción
[Descripción del cambio]

## Tipo de Cambio
- [ ] 🎯 Nueva característica
- [ ] 🐛 Corrección de error
- [ ] 📚 Documentación
- [ ] ♻️ Refactorización
- [ ] ⚡ Mejora de rendimiento

## Checklist
- [ ] Tests añadidos/actualizados
- [ ] Documentación actualizada
- [ ] PROJECT_TRACKING.md actualizado
- [ ] Revisado código propio
```

## 🔍 Code Review Guidelines

### Criterios de Revisión
1. **Funcionalidad**
   - ¿El código hace lo que debe?
   - ¿Maneja casos de error?

2. **Calidad**
   - ¿Tests adecuados?
   - ¿Código limpio y mantenible?

3. **Seguridad**
   - ¿Validación de inputs?
   - ¿Manejo seguro de datos sensibles?

### Proceso de Review
1. Revisar descripción del PR
2. Examinar cambios
3. Probar localmente si necesario
4. Aprobar o solicitar cambios

## 🤖 Git Hooks

### Pre-commit
- Linting
- Formateo de código
- Verificación de tipos
- Tests unitarios rápidos

### Pre-push
- Suite completa de tests
- Verificación de seguridad
- Validación de documentación

## 📊 Métricas de Git

### Seguimiento
- Frecuencia de commits
- Tamaño de PRs
- Tiempo de review
- Tasa de merge

### Objetivos
- PRs < 400 líneas
- Review < 24 horas
- Tests passing > 95%

## 🔄 Mantenimiento

### Limpieza Regular
```bash
# Limpiar ramas locales merged
git branch --merged | grep -v "^*" | xargs git branch -d

# Actualizar referencias remotas
git remote update origin --prune
```

### Tags y Releases
```bash
# Crear tag
git tag -a v1.0.0 -m "Version 1.0.0"

# Push tag
git push origin v1.0.0
``` 