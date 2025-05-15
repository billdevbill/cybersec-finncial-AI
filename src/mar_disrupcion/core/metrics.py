"""
Métricas centralizadas para monitoreo del sistema MAR-DISRUPCION.
"""
from prometheus_client import Counter, Histogram, Gauge
import structlog

logger = structlog.get_logger(__name__)

# Métricas de API
API_REQUESTS = Counter(
    'api_requests_total',
    'Total de peticiones a APIs externas',
    ['api_name', 'endpoint', 'method']
)

API_RESPONSE_TIME = Histogram(
    'api_response_time_seconds',
    'Tiempo de respuesta de APIs en segundos',
    ['api_name', 'endpoint']
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total de errores en llamadas a APIs',
    ['api_name', 'error_type']
)

# Métricas de memoria
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Uso de memoria del sistema',
    ['component']
)

CACHE_HITS = Counter(
    'cache_hits_total',
    'Total de aciertos en caché',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total de fallos en caché',
    ['cache_type']
)

# Métricas de procesamiento
PROCESSING_TIME = Histogram(
    'processing_time_seconds',
    'Tiempo de procesamiento en segundos',
    ['operation_type']
)

BATCH_SIZE = Histogram(
    'batch_size_total',
    'Tamaño de los lotes procesados',
    ['processor_type']
)

# Métricas de seguridad
SECURITY_ALERTS = Counter(
    'security_alerts_total',
    'Total de alertas de seguridad',
    ['severity', 'type']
)

SCAN_DURATION = Histogram(
    'security_scan_duration_seconds',
    'Duración de los escaneos de seguridad',
    ['scan_type']
)

# Métricas financieras
FINANCIAL_TRANSACTIONS = Counter(
    'financial_transactions_total',
    'Total de transacciones financieras analizadas',
    ['transaction_type']
)

ANOMALY_DETECTIONS = Counter(
    'anomaly_detections_total',
    'Total de anomalías detectadas',
    ['anomaly_type', 'severity']
)

def record_api_request(api_name: str, endpoint: str, method: str = "GET"):
    """Registra una petición a API"""
    API_REQUESTS.labels(api_name=api_name, endpoint=endpoint, method=method).inc()

def record_api_error(api_name: str, error_type: str):
    """Registra un error de API"""
    API_ERRORS.labels(api_name=api_name, error_type=error_type).inc()

def start_operation_timer(operation_type: str) -> Histogram.Timer:
    """Inicia un temporizador para una operación"""
    return PROCESSING_TIME.labels(operation_type=operation_type).time()

def record_security_alert(severity: str, alert_type: str):
    """Registra una alerta de seguridad"""
    SECURITY_ALERTS.labels(severity=severity, type=alert_type).inc()

def record_financial_transaction(transaction_type: str):
    """Registra una transacción financiera"""
    FINANCIAL_TRANSACTIONS.labels(transaction_type=transaction_type).inc()

def record_anomaly_detection(anomaly_type: str, severity: str):
    """Registra una detección de anomalía"""
    ANOMALY_DETECTIONS.labels(anomaly_type=anomaly_type, severity=severity).inc()
