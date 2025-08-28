# backend/app/monitoring.py
"""
Мониторинг и метрики приложения.
"""

import time
import psutil
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from .logging_config import app_logger


@dataclass
class SystemMetrics:
    """Метрики системы."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    timestamp: datetime


@dataclass
class ApplicationMetrics:
    """Метрики приложения."""
    active_users: int
    total_requests: int
    requests_per_minute: float
    average_response_time: float
    error_rate: float
    database_connections: int
    redis_connections: int
    timestamp: datetime


class MetricsCollector:
    """
    Сборщик метрик приложения.
    """
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)  # Последние 1000 запросов
        self.request_counts = defaultdict(int)  # Счетчики запросов по минутам
        self.error_counts = defaultdict(int)    # Счетчики ошибок по минутам
        self.active_users = set()               # Активные пользователи
        self.user_last_seen = {}               # Последняя активность пользователей
        
        # Метрики производительности
        self.slow_queries = deque(maxlen=100)   # Медленные запросы к БД
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Системные метрики
        self.system_metrics_history = deque(maxlen=60)  # Последние 60 измерений
        
        self._start_time = datetime.utcnow()
    
    def record_request(self, duration: float, status_code: int, 
                      user_id: Optional[int] = None, endpoint: str = ""):
        """
        Записывает метрики запроса.
        
        Args:
            duration: Время выполнения запроса в секундах
            status_code: HTTP статус код
            user_id: ID пользователя (если авторизован)
            endpoint: Эндпоинт API
        """
        current_time = datetime.utcnow()
        minute_key = current_time.replace(second=0, microsecond=0)
        
        # Записываем время ответа
        self.request_times.append(duration)
        
        # Увеличиваем счетчик запросов
        self.request_counts[minute_key] += 1
        
        # Записываем ошибки
        if status_code >= 400:
            self.error_counts[minute_key] += 1
        
        # Обновляем активных пользователей
        if user_id:
            self.active_users.add(user_id)
            self.user_last_seen[user_id] = current_time
        
        # Логируем медленные запросы
        if duration > 1.0:  # Запросы дольше 1 секунды
            app_logger.log_performance(
                f"Slow request to {endpoint}",
                duration,
                {"status_code": status_code, "user_id": user_id}
            )
    
    def record_database_query(self, query_type: str, duration: float, 
                             query: str = ""):
        """
        Записывает метрики запроса к базе данных.
        
        Args:
            query_type: Тип запроса (SELECT, INSERT, UPDATE, DELETE)
            duration: Время выполнения в секундах
            query: SQL запрос (опционально)
        """
        if duration > 0.5:  # Медленные запросы (больше 500ms)
            self.slow_queries.append({
                "type": query_type,
                "duration": duration,
                "query": query[:200] if query else "",  # Первые 200 символов
                "timestamp": datetime.utcnow()
            })
            
            app_logger.log_performance(
                f"Slow database query ({query_type})",
                duration,
                {"query_preview": query[:100] if query else ""}
            )
    
    def record_cache_operation(self, operation: str, hit: bool):
        """
        Записывает операцию с кэшем.
        
        Args:
            operation: Тип операции (get, set, delete)
            hit: True если попадание в кэш, False если промах
        """
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def cleanup_old_users(self, inactive_minutes: int = 30):
        """
        Удаляет неактивных пользователей из списка активных.
        
        Args:
            inactive_minutes: Количество минут неактивности
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=inactive_minutes)
        
        inactive_users = [
            user_id for user_id, last_seen in self.user_last_seen.items()
            if last_seen < cutoff_time
        ]
        
        for user_id in inactive_users:
            self.active_users.discard(user_id)
            del self.user_last_seen[user_id]
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        Получает текущие системные метрики.
        
        Returns:
            SystemMetrics: Метрики системы
        """
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_usage_percent=disk.percent,
            timestamp=datetime.utcnow()
        )
        
        # Сохраняем в историю
        self.system_metrics_history.append(metrics)
        
        return metrics
    
    def get_application_metrics(self) -> ApplicationMetrics:
        """
        Получает текущие метрики приложения.
        
        Returns:
            ApplicationMetrics: Метрики приложения
        """
        current_time = datetime.utcnow()
        
        # Очищаем неактивных пользователей
        self.cleanup_old_users()
        
        # Вычисляем запросы в минуту (за последние 5 минут)
        five_minutes_ago = current_time - timedelta(minutes=5)
        recent_requests = sum(
            count for minute, count in self.request_counts.items()
            if minute >= five_minutes_ago
        )
        requests_per_minute = recent_requests / 5.0
        
        # Вычисляем среднее время ответа
        avg_response_time = (
            sum(self.request_times) / len(self.request_times)
            if self.request_times else 0.0
        )
        
        # Вычисляем процент ошибок
        recent_errors = sum(
            count for minute, count in self.error_counts.items()
            if minute >= five_minutes_ago
        )
        error_rate = (
            (recent_errors / recent_requests * 100) 
            if recent_requests > 0 else 0.0
        )
        
        return ApplicationMetrics(
            active_users=len(self.active_users),
            total_requests=sum(self.request_counts.values()),
            requests_per_minute=requests_per_minute,
            average_response_time=avg_response_time,
            error_rate=error_rate,
            database_connections=0,  # TODO: Получать из пула соединений
            redis_connections=0,     # TODO: Получать из Redis клиента
            timestamp=current_time
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Получает статус здоровья приложения.
        
        Returns:
            Dict: Статус здоровья
        """
        system_metrics = self.get_system_metrics()
        app_metrics = self.get_application_metrics()
        
        # Определяем статус здоровья
        health_issues = []
        
        if system_metrics.cpu_percent > 80:
            health_issues.append("High CPU usage")
        
        if system_metrics.memory_percent > 85:
            health_issues.append("High memory usage")
        
        if system_metrics.disk_usage_percent > 90:
            health_issues.append("High disk usage")
        
        if app_metrics.error_rate > 5.0:
            health_issues.append("High error rate")
        
        if app_metrics.average_response_time > 2.0:
            health_issues.append("Slow response times")
        
        status = "healthy" if not health_issues else "warning"
        if len(health_issues) > 2:
            status = "critical"
        
        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "issues": health_issues,
            "system": asdict(system_metrics),
            "application": asdict(app_metrics),
            "cache": {
                "hit_rate": (
                    self.cache_hits / (self.cache_hits + self.cache_misses) * 100
                    if (self.cache_hits + self.cache_misses) > 0 else 0
                ),
                "total_operations": self.cache_hits + self.cache_misses
            },
            "slow_queries_count": len(self.slow_queries)
        }


class PerformanceMonitor:
    """
    Контекстный менеджер для мониторинга производительности.
    """
    
    def __init__(self, operation_name: str, metrics_collector: MetricsCollector):
        self.operation_name = operation_name
        self.metrics_collector = metrics_collector
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.record_database_query(
                self.operation_name, 
                duration
            )


@asynccontextmanager
async def async_performance_monitor(operation_name: str, 
                                   metrics_collector: MetricsCollector):
    """
    Асинхронный контекстный менеджер для мониторинга производительности.
    
    Args:
        operation_name: Название операции
        metrics_collector: Сборщик метрик
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        metrics_collector.record_database_query(operation_name, duration)


# Глобальный экземпляр сборщика метрик
metrics_collector = MetricsCollector()


def get_metrics_summary() -> Dict[str, Any]:
    """
    Получает сводку всех метрик для отображения в админке.
    
    Returns:
        Dict: Сводка метрик
    """
    return metrics_collector.get_health_status()