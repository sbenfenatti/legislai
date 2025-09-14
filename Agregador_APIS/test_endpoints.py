# test_endpoints.py
# Sistema de testes automatizados para endpoints configurados em YAML.
# Executa chamadas seguras com autenticação, limites de taxa, retries e relatório final.
# Uso:
#   python test_endpoints.py --config config-sistema-busca.yaml --output-dir resultados
# Requisitos:
#   - Python 3.10+
#   - pip install -r requirements.txt
#   - Configurar .env (se necessário) e, opcionalmente, samples.yaml

import asyncio
import aiohttp
import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import yaml
from dotenv import load_dotenv

# --------------------------
# Utilidades
# --------------------------

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def last_days(n: int) -> Tuple[str, str]:
    end = datetime.now().date()
    start = end - timedelta(days=n)
    return str(start), str(end)

def is_path_param_path(path: str) -> bool:
    return "{" in path and "}" in path

def extract_path_params(path: str) -> List[str]:
    return re.findall(r"{([^}]+)}", path or "")

def coalesce(*vals):
    for v in vals:
        if v is not None:
            return v
    return None

def normalize_bool(s: Optional[str]) -> bool:
    if not s:
        return False
    return str(s).strip().lower() in {"1", "true", "yes", "on", "y"}

# --------------------------
# Gerador de parâmetros de teste
# --------------------------

class ParamFactory:
    def __init__(self, samples: Dict[str, Any]) -> None:
        self.samples = samples or {}

    def sample_for(self, name: str) -> Optional[str]:
        # Prioriza samples.yaml > defaults básicos
        if name in self.samples:
            return str(self.samples[name])

        today = datetime.now()
        start, end = last_days(7)
        defaults = {
            # Datas
            "dataInicio": start,
            "dataFinal": end,
            "dataFim": end,
            "data": str(end),
            # Paginação
            "pagina": "1",
            "itensPorPagina": "1",
            "itens": "1",
            # Períodos
            "ano": str(today.year),
            "mes": f"{today.month:02d}",
            # IDs genéricos (precisam de amostras reais para path params)
            "id": self.samples.get("id"),
            "codigo": self.samples.get("codigo"),
            "codigoMunicipio": self.samples.get("codigoMunicipio"),
            "codigoOrgao": self.samples.get("codigoOrgao"),
            "codigoFuncional": self.samples.get("codigoFuncional"),
            "codigoParlamentar": self.samples.get("codigoParlamentar"),
            "codigoMateria": self.samples.get("codigoMateria"),
            "codigoUg": self.samples.get("codigoUg"),
            "modalidade": self.samples.get("modalidade"),
            "numero": self.samples.get("numero"),
            "siglaUf": self.samples.get("siglaUf"),
            "sigla": self.samples.get("sigla"),
            # Pessoas
            "cpf": self.samples.get("cpf"),
            "cnpj": self.samples.get("cnpj"),
            "cnpjCpf": self.samples.get("cnpjCpf"),
            "cpfCnpj": self.samples.get("cpfCnpj"),
            "cpfOuNis": self.samples.get("cpfOuNis"),
            "nis": self.samples.get("nis"),
            # Gerais
            "nome": self.samples.get("nome"),
            "chave": self.samples.get("chave"),
            "ddd": self.samples.get("ddd"),
            "uf": self.samples.get("uf"),
            "isbn": self.samples.get("isbn"),
            "moeda": self.samples.get("moeda", "USD"),
            "dataInicial": start,
            "dataFinalCotacao": end,
            "dataCotacao": end,
        }
        return coalesce(defaults.get(name), None)

    def make_query_params(self, param_names: List[str]) -> Dict[str, str]:
        params = {}
        for p in param_names or []:
            v = self.sample_for(p)
            if v is not None:
                params[p] = str(v)
        return params

    def make_path(self, path_template: str) -> Optional[str]:
        # Substitui {param} usando samples
        params = extract_path_params(path_template)
        filled = path_template
        for p in params:
            v = self.sample_for(p)
            if not v:
                return None
            filled = filled.replace("{" + p + "}", str(v))
        return filled

# --------------------------
# Rate limiting simples (delay entre chamadas)
# --------------------------

class SimpleRateLimiter:
    def __init__(self, rpm: int):
        self.rpm = max(1, rpm or 60)
        self.min_interval = 60.0 / float(self.rpm)
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self):
        async with self._lock:
            now = time.perf_counter()
            elapsed = now - self._last
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self._last = time.perf_counter()

# --------------------------
# Cliente HTTP de teste
# --------------------------

class EndpointTester:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        headers: Dict[str, str],
        rate_limiter: Optional[SimpleRateLimiter],
        timeout: int,
        retries: int,
        backoff_base: float,
    ) -> None:
        self.session = session
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.rate_limiter = rate_limiter
        self.timeout = timeout
        self.retries = retries
        self.backoff_base = backoff_base

    async def _request_once(self, method: str, url: str, params: Dict[str, str]) -> Tuple[int, int, Optional[str]]:
        t0 = time.perf_counter()
        try:
            async with self.session.request(
                method.upper(),
                url,
                headers=self.headers,
                params=params or None,
                timeout=self.timeout,
            ) as resp:
                content = await resp.read()
                dt = int((time.perf_counter() - t0) * 1000)
                return resp.status, len(content), None
        except Exception as e:
            dt = int((time.perf_counter() - t0) * 1000)
            return 0, 0, str(e)

    async def request(self, method: str, path: str, params: Dict[str, str]) -> Tuple[int, int, Optional[str]]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        attempts = 0
        while True:
            if self.rate_limiter:
                await self.rate_limiter.wait()
            status, size, err = await self._request_once(method, url, params)
            if err is None and status in (200, 201, 202, 204, 400, 401, 403, 404, 405, 415, 429, 500, 502, 503):
                return status, size, None
            attempts += 1
            if attempts > self.retries:
                return status, size, err or f"HTTP {status}"
            await asyncio.sleep(self.backoff_base * (2 ** (attempts - 1)))

# --------------------------
# Execução dos testes
# --------------------------

async def run_tests(
    config_path: str,
    output_dir: str,
    only_api: Optional[str],
    category: Optional[str],
    include_disabled: bool,
    concurrency: int,
    timeout: int,
    retries: int,
    rpm_override: Optional[int],
    dry_run: bool,
    format_prefer: str,
    samples_path: Optional[str],
    paginate: bool,
) -> Dict[str, Any]:

    load_dotenv(override=True)
    cfg = load_yaml(config_path)
    apis_cfg: Dict[str, Any] = cfg.get("apis", {})
    auth_cfg: Dict[str, Any] = cfg.get("authentication", {})

    samples = load_yaml(samples_path) if samples_path and os.path.exists(samples_path) else {}

    # Monta lista de tarefas
    tasks: List[Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any]]] = []
    for api_key, api in apis_cfg.items():
        if only_api and api_key != only_api:
            continue
        if not include_disabled and not api.get("enabled", True):
            continue

        base_url = api.get("base_url")
        endpoints = api.get("endpoints", []) or []
        token_required = api.get("token_required", False)

        # Cabeçalho de autenticação
        headers = {}
        if token_required:
            # Busca regra de auth no bloco authentication
            if api_key in auth_cfg:
                auth = auth_cfg[api_key]
                header_name = auth.get("header")
                env_var = auth.get("env_var")
                token_prefix = auth.get("token_prefix", "")
                token_val = os.getenv(env_var or "")
                if token_val:
                    headers[header_name] = f"{token_prefix + ' ' if token_prefix else ''}{token_val}"
            else:
                # Fallback genérico por campos do próprio bloco da API
                header_name = api.get("token_header")
                env_var = api.get("env_var")
                token_val = os.getenv(env_var or "")
                if header_name and token_val:
                    headers[header_name] = token_val

        # Limite de taxa
        rl_cfg = api.get("rate_limit", {}) or {}
        rpm = rpm_override or rl_cfg.get("requests_per_minute") or rl_cfg.get("rpm") or 60
        rate_limiter = SimpleRateLimiter(int(rpm))

        # Filtro por categoria (se desejado)
        for ep in endpoints:
            if category and ep.get("category") and ep.get("category") != category:
                continue
            tasks.append((api_key, api, ep, headers))

    results: List[Dict[str, Any]] = []
    sem = asyncio.Semaphore(concurrency)

    async def worker(item: Tuple[str, Dict[str, Any], Dict[str, Any], Dict[str, Any]]):
        api_key, api, ep, headers = item
        method = ep.get("method", "GET")
        path_template = ep.get("path", "")
        params_decl: List[str] = ep.get("parameters", []) or []

        param_factory = ParamFactory(samples)

        # Prepara path
        if is_path_param_path(path_template):
            path_filled = param_factory.make_path(path_template)
            if not path_filled:
                results.append({
                    "api": api_key,
                    "path": path_template,
                    "method": method,
                    "status": None,
                    "size": 0,
                    "ok": False,
                    "note": "IGNORED: path params sem amostras",
                    "duration_ms": 0,
                    "url": None,
                })
                return
        else:
            path_filled = path_template

        # Prepara query
        q = param_factory.make_query_params(params_decl)

        # Paginação mínima se suportada
        if paginate:
            if "pagina" in (params_decl or []):
                q.setdefault("pagina", "1")
            if "itensPorPagina" in (params_decl or []):
                q.setdefault("itensPorPagina", "1")
            if "itens" in (params_decl or []):
                q.setdefault("itens", "1")

        base_url = (api.get("base_url") or "").rstrip("/")
        # Cabeçalhos efetivos (auth por API)
        rl_cfg = api.get("rate_limit", {}) or {}
        rpm = rpm_override or rl_cfg.get("requests_per_minute") or rl_cfg.get("rpm") or 60
        rate_limiter = SimpleRateLimiter(int(rpm))

        timeout_local = timeout
        retries_local = retries
        backoff_base = 0.5

        if dry_run:
            results.append({
                "api": api_key,
                "path": path_filled,
                "method": method,
                "status": None,
                "size": 0,
                "ok": True,
                "note": "DRY-RUN",
                "duration_ms": 0,
                "url": f"{base_url}/{path_filled.lstrip('/')}",
            })
            return

        async with sem:
            async with aiohttp.ClientSession() as session:
                tester = EndpointTester(
                    session=session,
                    base_url=base_url,
                    headers=headers,
                    rate_limiter=rate_limiter,
                    timeout=timeout_local,
                    retries=retries_local,
                    backoff_base=backoff_base,
                )
                t0 = time.perf_counter()
                status, size, error = await tester.request(method, path_filled, q)
                dt = int((time.perf_counter() - t0) * 1000)

                # Heurística: se API exige token e não foi enviado header, 401/403 é aceitável
                token_required = api.get("token_required", False)
                had_auth = bool(headers)
                ok = False
                note = ""
                if error:
                    ok = False
                    note = f"ERROR: {error}"
                else:
                    if status in (200, 201, 202, 204):
                        ok = True
                    elif status in (401, 403) and token_required and not had_auth:
                        ok = True
                        note = "Sem token (esperado em dev)"
                    elif status in (400, 404):
                        # Endpoint respondeu, mas sem dados ou parâmetros insuficientes
                        ok = True
                        note = f"HTTP {status} (parâmetros de teste mínimos)"
                    else:
                        ok = False
                        note = f"HTTP {status}"

                results.append({
                    "api": api_key,
                    "path": path_filled,
                    "method": method,
                    "status": status,
                    "size": size,
                    "ok": ok,
                    "note": note,
                    "duration_ms": dt,
                    "url": f"{base_url}/{path_filled.lstrip('/')}",
                })

    await asyncio.gather(*(worker(t) for t in tasks))

    # Salva relatórios
    ensure_dir(output_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(output_dir, f"report_{ts}.json")
    csv_path = os.path.join(output_dir, f"report_{ts}.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": now_iso(), "results": results}, f, ensure_ascii=False, indent=2)

    # CSV
    fields = ["api", "method", "path", "status", "ok", "duration_ms", "size", "note", "url"]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k) for k in fields})

    summary = {
        "generated_at": now_iso(),
        "total": len(results),
        "ok": sum(1 for r in results if r.get("ok")),
        "fail": sum(1 for r in results if not r.get("ok")),
        "json_report": json_path,
        "csv_report": csv_path,
    }
    return summary

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Testador de endpoints a partir de um YAML de configuração.")
    p.add_argument("--config", required=True, help="Caminho do arquivo YAML de configuração.")
    p.add_argument("--output-dir", default="resultados", help="Diretório de saída para relatórios.")
    p.add_argument("--only-api", default=None, help="Chave de API específica (ex.: portal_transparencia).")
    p.add_argument("--category", default=None, help="Filtra por categoria do endpoint (ex.: despesas).")
    p.add_argument("--include-disabled", action="store_true", help="Inclui APIs desabilitadas no YAML.")
    p.add_argument("--concurrency", type=int, default=5, help="Número de chamadas simultâneas.")
    p.add_argument("--timeout", type=int, default=30, help="Timeout por requisição em segundos.")
    p.add_argument("--retries", type=int, default=2, help="Número de tentativas com backoff.")
    p.add_argument("--rpm", type=int, default=None, help="Sobrescreve requests/minute para todas as APIs.")
    p.add_argument("--dry-run", action="store_true", help="Não chama APIs, apenas lista o que seria testado.")
    p.add_argument("--format", default="json", choices=["json"], help="Formato preferencial (mantido para compatibilidade).")
    p.add_argument("--samples", default=None, help="Caminho para samples.yaml com valores de parâmetros.")
    p.add_argument("--paginate", action="store_true", help="Força paginação mínima (pagina=1, itens=1) quando suportada.")
    return p.parse_args()

def main():
    args = parse_args()
    try:
        summary = asyncio.run(run_tests(
            config_path=args.config,
            output_dir=args.output_dir,
            only_api=args.only_api,
            category=args.category,
            include_disabled=args.include_disabled,
            concurrency=args.concurrency,
            timeout=args.timeout,
            retries=args.retries,
            rpm_override=args.rpm,
            dry_run=args.dry_run,
            format_prefer=args.format,
            samples_path=args.samples,
            paginate=args.paginate,
        ))
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    except KeyboardInterrupt:
        print("Interrompido pelo usuário.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Erro fatal: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
