# Deploy

## Render (recomendado)

1. Crie um repositório no GitHub e envie estes arquivos (inclua `agent_workspace/` na raiz do repo).
2. No Render, clique em New > Web Service > Connect a repo.
3. Escolha este repositório. O Render detectará o `render.yaml` na raiz.
4. Clique em Create Web Service. Plano: Free. O serviço vai usar `agent_workspace` como root.
5. Depois de subir, acesse:
   - `/web/1.html`, `/web/2.html`, `/web/5.html` (frontend)
   - `/docs` (Swagger)

### Variáveis de ambiente (Service > Environment)
- `DATASUS_LOGIN` e `DATASUS_PASSWORD` (opcional – ativa DataSUS real)
- `TRANSPARENCIA_API_KEY` (opcional – Portal da Transparência)

## Rodar localmente
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r agent_workspace/requirements.txt
cd agent_workspace
uvicorn main_fastapi:app --host 0.0.0.0 --port 8010
```
Abra: http://127.0.0.1:8010/web/1.html

## Estrutura principal
- `agent_workspace/main_fastapi.py` – app FastAPI (servindo `/web`)
- `agent_workspace/datasus_real.py` – DataSUS (DEMAS)
- `agent_workspace/siconfi.py` – SICONFI (Tesouro)
- `agent_workspace/transparencia.py` – Portal da Transparência
- `agent_workspace/camara.py` – Câmara dos Deputados
- `agent_workspace/senado.py` – Senado (XML->JSON)
- `agent_workspace/1.html .. 5.html` – telas
