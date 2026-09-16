import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, status
from fastapi.responses import StreamingResponse
from prometheus_client import Counter, Histogram, make_asgi_app


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    labelnames=["method", "route", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "request_duration",
    "Request deration in seconds",
    labelnames=["method", "route", "status_code"],
    # Бакеты (buckets) — это "корзины" для сортировки времени в секундах.
    # Если запрос шел 0.08 сек, он попадет в корзину <= 0.1, <= 0.25 и т.д.
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

logger = logging.getLogger(__name__)


async def observability_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[StreamingResponse]]
) -> StreamingResponse:
    start_time = time.perf_counter()
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR # Дефолтное значение
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        # без логирования ошибки чтобы не дублировать в логах
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise
    finally:
        process_time = time.perf_counter() - start_time

        # - PROMETHEUS -
        # Шаблон пути роута в FastAPI ("/users/{user_id}")
        # позволяет не множить пути а привязываться к шаблону
        # Если запрос ушел на несуществующий роут (404), запишется сырой путь
        route_path = request.url.path
        if "route" in request.scope:
            route_path = request.scope["route"].path

        # словарь с тегами.
        # Ключи должны совпадать с labelnames выше
        # Prometheus принимает тегb в виде строк, поэтому str(status_code)
        metric_labels = {
            "method": request.method,
            "route": route_path,
            "status_code": str(status_code)
        }

        # Выбираем конкретную метрику с нашими тегами (.labels(**metric_labels))
        # и увеличиваем счетчик на 1 (.inc())
        HTTP_REQUESTS_TOTAL.labels(**metric_labels).inc()

        # Выбираем гистограмму времени и передаем туда замер скорости (.observe(process_time))
        # Библиотека сама разложит это время в нужную "корзину" (bucket)
        HTTP_REQUEST_DURATION_SECONDS.labels(**metric_labels).observe(process_time)


        # Один чистый лог. Для OpenObserve лучше передавать
        # параметры структурированно через extra, а не в одну строку
        logger.info(
            "HTTP request %s to %s completed with status code %s",
            request.method,
            request.url.path,
            status_code,
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "route_template": route_path, # поле для Prometheus
                "status_code": status_code,
                "duration_sec": round(process_time, 4)
            }
        )


# make_asgi_app() — это специальная функция-адаптер. Она берет все метрики,
# собранные в памяти Python, и превращает их в готовое мини-приложение,
# умеющее отдавать текст в формате Prometheus.
metrics_asgi_app = make_asgi_app()



async def add_process_time_to_requests(
    request: Request,
    call_next: Callable[[Request], Awaitable[StreamingResponse]]
) -> StreamingResponse:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.5f}"
    return response


async def log_new_request(
    request: Request,
    call_next: Callable[[Request], Awaitable[StreamingResponse]]
) -> StreamingResponse:
    logger.info(
        "Request %s to %s",
         request.method,
        # request.url,
        request.url.path
    )
    return await call_next(request)
