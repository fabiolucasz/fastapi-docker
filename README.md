# FastAPI Docker Authentication

API FastAPI com sistema de autenticação completo usando JWT, containerizada com Docker.

## 🚀 Features

- **Autenticação JWT** - Bearer tokens para acesso seguro
- **Hash de senhas** - bcrypt com truncamento automático (72 bytes)
- **CRUD de usuários** - Criação, leitura e autenticação
- **Multi-ambiente** - SQLite (dev) / PostgreSQL (prod)
- **Docker** - Containerização completa
- **FastAPI** - OpenAPI/Swagger automático

## 📁 Estrutura

```
fastapi-docker/
├── src/
│   ├── core/
│   │   ├── config.py      # Configurações de ambiente
│   │   ├── crud.py        # Operações CRUD
│   │   ├── db.py          # Conexão com banco
│   │   ├── deps.py        # Dependências FastAPI
│   │   ├── models.py      # Modelos SQLAlchemy
│   │   ├── schemas.py     # Schemas Pydantic
│   │   └── security.py    # JWT e hash de senhas
│   └── main.py            # Aplicação FastAPI
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .env
```

## 🔧 Configuração

### Variáveis de Ambiente

```bash
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DOMAIN=localhost
ENVIRONMENT=dev  # dev | prod
```

### PostgreSQL (produção)

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_db
```

## 🏃‍♂️ Execução

### Local (Desenvolvimento)

```bash
# Instalar dependências
poetry install

# Iniciar API
fastapi dev

# Acessar: http://localhost:8000/docs
```

### Docker

```bash
# Build e iniciar
docker compose up -d --build

# Logs
docker compose logs -f
```

## 📚 API Endpoints

### Autenticação

- `POST /signup` - Criar novo usuário
- `POST /login/access-token` - Obter token JWT

### Usuários

- `GET /users/me` - Dados do usuário autenticado

### Documentação

- `GET /docs` - Swagger UI
- `GET /openapi.json` - OpenAPI schema

## 🔐 Exemplo de Uso

### 1. Criar Usuário

```bash
curl -X POST "http://localhost:8000/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret123"}'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret123"
```

### 3. Acesso Protegido

```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer <token>"
```

## 🛠️ Tecnologias

- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **Pydantic** - Validação
- **JWT** - Autenticação (python-jose)
- **bcrypt** - Hash de senhas
- **Poetry** - Dependências
- **Docker** - Containerização

## 📝 Notas Técnicas

### Senhas
- Truncamento automático para 72 bytes (limite bcrypt)
- Hash com bcrypt + salt
- Verificação segura com timing-safe comparison

### Banco de Dados
- **Dev**: SQLite com `check_same_thread=False`
- **Prod**: PostgreSQL com psycopg2
- Migrações automáticas via SQLAlchemy

### JWT
- Expiração: 7 dias (padrão)
- Algoritmo: HS256
- Payload: `{"exp": timestamp, "sub": user_id}`

## 🔒 Segurança

- Senhas nunca armazenadas em plaintext
- Tokens com expiração configurável
- CORS configurável por ambiente
- Injeção de dependência para autenticação

## 🐛 Troubleshooting

### Erros Comuns

1. **"password cannot be longer than 72 bytes"**
   - ✅ Corrigido com truncamento automático

2. **"Could not validate credentials"**
   - Verificar SECRET_KEY no .env
   - Token expirado? Use `/login` novamente

3. **"Database connection failed"**
   - Dev: Verificar permissões do arquivo SQLite
   - Prod: Verificar variáveis PostgreSQL

### Docker Issues

```bash
# Limpar containers
docker compose down -v

# Rebuild sem cache
docker compose build --no-cache
```