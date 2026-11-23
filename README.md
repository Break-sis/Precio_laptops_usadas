# Laboratorio: Pruebas de Aceptación de Usuario (UAT) con Python, NiceGUI y SQLModel

## Estructura del proyecto
- `modelos_y_reglas.py`: Modelo `Pedido` (SQLModel) y lógica de negocio aislada de la UI.
- `app_nicegui.py`: Aplicación web interactiva construida con NiceGUI.
- `test_aceptacion.py`: Pruebas de aceptación automatizadas con `pytest` sobre SQLite en memoria.
- `requirements.txt`: Dependencias necesarias.

## Instalación y ejecución rápida
1. Crear y activar entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / macOS:
   source .venv/bin/activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar pruebas de aceptación automatizadas:
   ```bash
   pytest -v
   ```
4. Ejecutar la aplicación web en NiceGUI:
   ```bash
   python app_nicegui.py
   ```
   Abrir en el navegador: `http://localhost:8080`
