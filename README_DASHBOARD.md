# Dashboard Grafana Automático

## 🚀 Dashboard Pré-configurado

O dashboard "Fastapi-app" será carregado automaticamente ao iniciar o Docker Compose.

## 📁 Estrutura de Provisioning

```
grafana/
├── provisioning/
│   ├── datasources/
│   │   └── prometheus.yml      # Configura datasource Prometheus
│   └── dashboards/
│       ├── dashboard.yml         # Configura provider de dashboards
│       └── fastapi-dashboard.json  # Seu dashboard personalizado
```

## 🎯 Panels do Dashboard

1. **Erro em tentativa de login** (Gauge)
   - Percentual de falhas de autenticação
   - Query: `(sum(rate(auth_attempts_total{job="fastapi-app", status="failed"}[$__rate_interval]))/sum(rate(auth_attempts_total{job="fastapi-app"}[$__rate_interval]))) * 100`

2. **Throughput** (Stat)
   - Requisições por minuto
   - Query: `sum(rate(request_duration_seconds_count[$__interval]))*60`

3. **Uso de CPU** (Gauge)
   - Percentual de CPU utilizada
   - Query: `rate(process_cpu_seconds_total{job="fastapi-app"}[$__rate_interval])`

4. **Throughput** (Time Series)
   - Gráfico de throughput ao longo do tempo
   - Query: `sum(rate(request_duration_seconds_count[$__interval]))*60`

5. **Auth Attempts Error** (Time Series)
   - Taxa de erro de autenticação ao longo do tempo
   - Query: `(sum(rate(auth_attempts_total{job="fastapi-app", status="failed"}[$__rate_interval]))/sum(rate(auth_attempts_total{job="fastapi-app"}[$__rate_interval]))) * 100`

6. **Uso de CPU** (Time Series)
   - Gráfico de uso de CPU ao longo do tempo
   - Query: `rate(process_cpu_seconds_total{job="fastapi-app"}[$__rate_interval])`

## 🚀 Como Usar

### Iniciar Stack com Dashboard
```bash
docker compose up -d
```

### Acessar Dashboard
1. **Grafana**: http://localhost:3000
2. **Login**: admin/admin
3. **Dashboard**: "Fastapi-app" (já estará disponível)

### Verificar se funcionou
```bash
# Verificar se arquivos foram montados corretamente
docker compose exec grafana ls -la /etc/grafana/provisioning/datasources/
docker compose exec grafana ls -la /etc/grafana/provisioning/dashboards/

# Verificar logs do Grafana
docker compose logs grafana | grep -i provisioning
```

## 🔧 Configuração Detalhada

### Datasource Prometheus
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

### Dashboard Provider
```yaml
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

## 🎨 Personalização

### Modificar Dashboard
1. Edite o arquivo: `grafana/provisioning/dashboards/fastapi-dashboard.json`
2. Reinicie o Grafana: `docker compose restart grafana`
3. O dashboard será atualizado automaticamente

### Adicionar Novo Dashboard
1. Copie o JSON do novo dashboard para: `grafana/provisioning/dashboards/`
2. Reinicie o Grafana: `docker compose restart grafana`

### Modificar Queries
As queries usam as seguintes métricas:
- `auth_attempts_total` - Tentativas de autenticação
- `request_duration_seconds_count` - Contador de requisições
- `process_cpu_seconds_total` - Tempo de CPU do processo

## 🐛 Troubleshooting

### Dashboard não aparece
```bash
# Verificar se arquivos existem
ls -la grafana/provisioning/datasources/
ls -la grafana/provisioning/dashboards/

# Verificar logs
docker compose logs grafana

# Reiniciar Grafana
docker compose restart grafana
```

### Datasource não conecta
1. Verifique se Prometheus está rodando: `http://localhost:9090`
2. Verifique se targets estão UP: `http://localhost:9090/targets`
3. Teste conectividade: `docker compose exec grafana wget -qO- http://prometheus:9090/api/v1/query?query=up`

### Queries não retornam dados
1. Verifique se métricas existem: `curl http://localhost:8000/metrics`
2. Verifique se Prometheus está coletando: `http://localhost:9090/graph?g0.expr=auth_attempts_total`
3. Ajuste o time range no dashboard

## 📈 Métricas Adicionais

Para adicionar novas métricas:

1. **Defina em `src/core/metrics.py`:**
```python
nova_metrica = Counter('nova_metrica', 'Descrição')
```

2. **Use nos endpoints:**
```python
MetricsManager.nova_metrica.inc()
```

3. **Atualize o dashboard JSON** com a nova query

4. **Reinicie os containers:**
```bash
docker compose restart api grafana
```

## 🔄 Atualização Automática

O dashboard é atualizado automaticamente a cada 10 segundos (configurado em `updateIntervalSeconds: 10`).

Modificações no JSON do dashboard são refletidas após reiniciar o Grafana.

## 📚 Documentação

- [Grafana Provisioning](https://grafana.com/docs/grafana/latest/administration/provisioning/)
- [Prometheus Querying](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [FastAPI Metrics](https://fastapi.tiangolo.com/tutorial/middleware/)
