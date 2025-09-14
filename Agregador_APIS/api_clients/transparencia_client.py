import os
import re
import time
from types import MethodType
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.portaldatransparencia.gov.br"
DATA_API_PREFIX = "/api-de-dados"
OPENAPI_URL = f"{BASE_URL}/v3/api-docs"
API_KEY = os.getenv("PORTAL_TRANSPARENCIA_KEY")

if not API_KEY:
    raise RuntimeError("Defina PORTAL_TRANSPARENCIA_KEY no .env ou ambiente")

DEFAULT_TIMEOUT: Tuple[int, int] = (15, 45)
DEFAULT_MAX_RETRIES = 6
DEFAULT_BACKOFF_BASE = 1.6


class TransparenciaAPIError(Exception):
    pass


class PortalTransparenciaClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: Tuple[int, int] = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        user_agent: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "chave-api-dados": (api_key or API_KEY),
                "User-Agent": user_agent or "legislai-portal-transparencia-client/1.0",
            }
        )
        self._openapi: Optional[Dict[str, Any]] = None
        self.operations: Dict[str, Dict[str, Any]] = {}

    def _build_url(self, path: str) -> str:
        path = path.strip()
        if not path.startswith("/"):
            path = f"/{path}"
        if not path.startswith(DATA_API_PREFIX):
            path = f"{DATA_API_PREFIX}{path}"
        return f"{self.base_url}{path}"

    def _format_path(self, template: str, path_params: Optional[Dict[str, Any]]) -> str:
        def repl(m: re.Match[str]) -> str:
            k = m.group(1)
            if path_params and k in path_params:
                return str(path_params[k])
            raise TransparenciaAPIError(f"Parâmetro de caminho '{k}' é obrigatório para {template}")

        return re.sub(r"\{([^{}]+)\}", repl, template)

    def request(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        path_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = params or {}
        url_path = self._format_path(path, path_params or {})
        url = self._build_url(url_path)

        last_err: Optional[BaseException] = None
        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and str(retry_after).isdigit():
                        time.sleep(int(retry_after))
                    else:
                        time.sleep(self.backoff_base ** attempt)
                    continue
                if resp.status_code in (500, 502, 503, 504):
                    time.sleep(self.backoff_base ** attempt)
                    last_err = TransparenciaAPIError(
                        f"HTTP {resp.status_code} em {url_path}"
                    )
                    continue
                resp.raise_for_status()
                if not resp.content:
                    return None
                ct = resp.headers.get("Content-Type", "")
                if "json" in ct:
                    return resp.json()
                return resp.text
            except requests.RequestException as e:
                last_err = e
                time.sleep(self.backoff_base ** attempt)
                continue
        raise TransparenciaAPIError(str(last_err) if last_err else "Falha na requisição")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return self.request(path, params=params)

    def get_all(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
        delay: float = 0.25,
    ) -> List[Any]:
        params = dict(params or {})
        page = int(params.get("pagina", 1))
        results: List[Any] = []
        seen_empty = 0
        while True:
            params["pagina"] = page
            data = self.get(endpoint, params)
            if isinstance(data, list):
                if not data:
                    seen_empty += 1
                    if seen_empty >= 1:
                        break
                results.extend(data)
            else:
                results.append(data)
                break
            page += 1
            if max_pages and page > max_pages:
                break
            time.sleep(delay)
        return results

    def openapi(self) -> Dict[str, Any]:
        if self._openapi is None:
            url = OPENAPI_URL
            for attempt in range(self.max_retries):
                try:
                    r = self.session.get(url, timeout=self.timeout)
                    r.raise_for_status()
                    self._openapi = r.json()
                    break
                except requests.RequestException:
                    time.sleep(self.backoff_base ** attempt)
            if self._openapi is None:
                raise TransparenciaAPIError("Não foi possível obter o OpenAPI")
        return self._openapi

    def _safe_attr(self, name: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if safe and safe[0].isdigit():
            safe = f"op_{safe}"
        return safe

    def build_operations(self) -> None:
        spec = self.openapi()
        ops: Dict[str, Dict[str, Any]] = {}
        paths: Dict[str, Any] = spec.get("paths", {})
        for raw_path, item in paths.items():
            if not raw_path.startswith(DATA_API_PREFIX):
                continue
            get_op = item.get("get")
            if not get_op:
                continue
            op_id = get_op.get("operationId") or self._op_id_from_path(raw_path)
            params = get_op.get("parameters", [])
            req_query = [p["name"] for p in params if p.get("in") == "query" and p.get("required")]
            req_path = [p["name"] for p in params if p.get("in") == "path" and p.get("required")]
            meta = {
                "operationId": op_id,
                "path": raw_path.replace(DATA_API_PREFIX, ""),
                "summary": get_op.get("summary", ""),
                "description": get_op.get("description", ""),
                "required_query": req_query,
                "required_path": req_path,
                "parameters": params,
                "tags": get_op.get("tags", []),
            }
            ops[op_id] = meta
        self.operations = ops
        for op_id in self.operations.keys():
            attr = self._safe_attr(op_id)
            if hasattr(self, attr):
                continue
            def _factory(oid: str):
                def _method(self, query: Optional[Dict[str, Any]] = None, path: Optional[Dict[str, Any]] = None):
                    return self.call(oid, query=query, path_params=path)
                return _method
            setattr(self, attr, MethodType(_factory(op_id), self))

    def _op_id_from_path(self, raw_path: str) -> str:
        clean = raw_path[len(DATA_API_PREFIX) :].strip("/")
        clean = re.sub(r"\{([^{}]+)\}", r"by_\1", clean)
        clean = clean.replace("/", "_").replace("-", "_")
        clean = re.sub(r"[^a-zA-Z0-9_]+", "_", clean)
        return clean

    def call(self, operation_id: str, query: Optional[Dict[str, Any]] = None, path_params: Optional[Dict[str, Any]] = None) -> Any:
        if not self.operations:
            self.build_operations()
        op = self.operations.get(operation_id)
        if not op:
            raise TransparenciaAPIError(f"Operação desconhecida: {operation_id}")
        return self.request(op["path"], params=query, path_params=path_params)

    def list_endpoints(self) -> List[Dict[str, Any]]:
        if not self.operations:
            self.build_operations()
        return [
            {
                "operationId": v["operationId"],
                "path": v["path"],
                "required_query": v["required_query"],
                "required_path": v["required_path"],
                "tags": v["tags"],
            }
            for v in self.operations.values()
        ]

    def endpoints_without_required_params(self) -> List[str]:
        if not self.operations:
            self.build_operations()
        ids: List[str] = []
        for op_id, op in self.operations.items():
            rq = [p for p in op["required_query"] if p != "pagina"]
            if not rq and not op["required_path"]:
                ids.append(op_id)
        return sorted(ids)

    def smoke_test(self, limit: Optional[int] = None, delay: float = 0.3) -> List[Tuple[str, bool, str]]:
        test_ids = self.endpoints_without_required_params()
        if limit:
            test_ids = test_ids[:limit]
        results: List[Tuple[str, bool, str]] = []
        for i, op_id in enumerate(test_ids, 1):
            try:
                data = self.call(op_id, query={"pagina": 1})
                if isinstance(data, list):
                    summary = f"lista {len(data)}"
                elif isinstance(data, dict):
                    summary = f"obj {len(data.keys())}"
                else:
                    summary = type(data).__name__
                results.append((op_id, True, summary))
            except Exception as e:
                results.append((op_id, False, str(e)[:200]))
            time.sleep(delay)
        return results


def _print_test_summary(rows: List[Tuple[str, bool, str]]) -> None:
    ok = [r for r in rows if r[1]]
    ko = [r for r in rows if not r[1]]
    total = len(rows)
    print("=" * 80)
    print(f"Smoke test: {len(ok)}/{total} OK")
    print("=" * 80)
    if ok:
        print("OK:")
        for op_id, _, msg in ok:
            print(f" - {op_id}: {msg}")
    if ko:
        print("Falhas:")
        for op_id, _, msg in ko:
            print(f" - {op_id}: {msg}")


if __name__ == "__main__":
    print("Portal da Transparência - Cliente real")
    client = PortalTransparenciaClient()
    client.build_operations()
    all_eps = client.list_endpoints()
    print(f"Endpoints descobertos (GET): {len(all_eps)}")
    rows = client.smoke_test(limit=None)
    _print_test_summary(rows)
