# 💰 MoneyTracker Sara - Analizador de Finanzas Personal

De PDFs desordenados a decisiones inteligentes. Este proyecto es un ecosistema completo de automatización que transforma estados de cuenta bancarios en un dashboard interactivo, con validación de datos profesional y alertas en tiempo real.

### 🚀 Funcionalidades
- **Análisis de PDF**: Extracción automática de datos financieros.
- **Categorización Inteligente**: Clasifica gastos en Súper, Transporte, etc.
- **Alertas de Telegram**: Envía notificaciones automáticas al detectar gastos duplicados.
- **ETL Financiero (Extracción y Carga): Automatización de la lectura de PDFs bancarios complejos, convirtiendo datos no estructurados en dataframes limpios y listos para el análisis.
- **Validación con Pydantic: Implementación de una capa de seguridad de datos que garantiza la integridad de cada transacción antes de su procesamiento.
- **Motor de Categorización Inteligente: Algoritmo personalizado que clasifica el historial de gastos en categorías clave para un control de presupuesto.
- **Detección de Anomalías & Duplicados: Sistema de monitoreo que identifica transacciones repetidas, asegurando la precisión de tus balances,alertas instantáneas vía Telegram Bot API
- **Exportación de Datos: Capacidad de exportar la data procesada a formatos Excel (.xlsx) para auditorías externas o reportes externos.
- **Diseño de Interfaz & Dashboard (UX/UI) He diseñado una interfaz intuitiva enfocada en la experiencia del usuario (UX):
- **Visualización Dinámica: Gráficos interactivos que permiten segmentar gastos por periodo y categoría.
- **Métricas en Tiempo Real: Resúmenes visuales rápidos de ahorros, gastos totales y alertas pendientes.

### 🛠️ Stack Tecnológico Profesional
- **Core: Python 3.12+ (Pandas, NumPy).
- **Web Framework: Streamlit (Dashboard,UI).
- **Data Validation: Pydantic (Modelado de datos robusto).
- **Análisis de PDF: Pdfplumber
- **Integraciones: Telegram Bot API (vía Requests con soporte de Proxies).
- **Visualización: Plotly Express.
- **Almacenamiento: SQLite para la gestión eficiente del historial de transacciones.

### Seguridad y Buenas Prácticas
Gestión de Secretos: Uso de variables de entorno (.env) para proteger credenciales sensibles.

Clean Code: Estructura de código modularizada en main.py y utils.py para facilitar el mantenimiento y escalabilidad.
