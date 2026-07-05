# Checklist de pruebas - ICEBERG v10

## 1. Local Windows

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\activate
$env:ICEBERG_MODO_LOCAL="true"
$env:ICEBERG_ENTORNO="local"
python -m streamlit run app.py
```

Validar:

- [ ] Abre `http://localhost:8501`.
- [ ] Muestra `Modo actual: Local Windows`.
- [ ] Valida credenciales.
- [ ] Descarga.
- [ ] Consolida.
- [ ] Filtra.
- [ ] Abre carpeta.
- [ ] Abre ubicación.
- [ ] Abre archivo.
- [ ] Descarga archivo.
- [ ] Descarga ZIP.

---

## 2. GitHub Codespaces

```bash
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Validar:

- [ ] Puerto `8501` disponible en **Ports**.
- [ ] Muestra `Modo actual: GitHub Codespaces`.
- [ ] No muestra botones locales.
- [ ] Valida credenciales.
- [ ] Descarga.
- [ ] Consolida.
- [ ] Filtra.
- [ ] Descarga archivo.
- [ ] Descarga ZIP.

---

## 3. Docker local

```powershell
cd C:\Users\ASUS\Documents\Github\descarga_iceberg
docker compose up --build
```

Abrir:

```text
http://localhost:8501
```

Validar:

- [ ] Muestra `Modo actual: Docker / Servidor`.
- [ ] No muestra botones locales.
- [ ] Valida credenciales.
- [ ] Descarga.
- [ ] Consolida.
- [ ] Filtra.
- [ ] Descarga archivo.
- [ ] Descarga ZIP.

Detener:

```powershell
docker compose down
```
