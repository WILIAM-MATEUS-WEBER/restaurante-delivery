# RestaurantOS — Sistema de Restaurante com Delivery

**Autor:** Wiliam Mateus Weber  
**Tema:** Infraestrutura para um Restaurante com Delivery  
**Disciplina:** Cloud Computing e DevOps

---

## Descrição

O **RestaurantOS** é uma aplicação web para gerenciamento de restaurante com delivery. Permite cadastrar produtos (cardápio), gerenciar clientes, criar pedidos com múltiplos itens e acompanhar o status de cada entrega em tempo real.

A aplicação foi desenvolvida para demonstrar um ambiente containerizado com Docker e Docker Compose, simulando uma arquitetura real de Cloud Computing com múltiplos containers conectados em rede dedicada.

---

## Tecnologias Utilizadas

| Camada | Tecnologia |
|--------|-----------|
| Aplicação | Python 3.12 + Flask 3.0 |
| Banco de Dados | PostgreSQL 16 (Alpine) |
| ORM / Driver | psycopg2-binary |
| Servidor WSGI | Gunicorn |
| Containerização | Docker + Docker Compose |
| Frontend | Jinja2 Templates + CSS puro |
| API | REST JSON (endpoints `/api/*`) |

---

## Arquitetura

```
┌─────────────────────────────────────────────┐
│              restaurante-net (bridge)        │
│                                             │
│  ┌──────────────────┐  ┌────────────────┐   │
│  │  restaurante-app │  │ restaurante-db │   │
│  │   (Flask:5000)   │──│  (Postgres:5432│   │
│  │                  │  │   + Volume)    │   │
│  └──────────────────┘  └────────────────┘   │
│          │                                  │
└──────────┼──────────────────────────────────┘
           │
     Host: localhost:5000
```

- **Container app**: Flask + Gunicorn servindo a interface web e API REST
- **Container db**: PostgreSQL com volume nomeado para persistência
- **Rede**: Bridge isolada `restaurante-net`; containers se comunicam por hostname
- **Volume**: `postgres-data` garante dados após `docker compose down`

---

## Instruções de Execução

### Pré-requisitos
- Docker 
- Docker Compose 

### 1. Clonar o repositório
```bash
git clone https://github.com/<seu-usuario>/restaurante-delivery.git
cd restaurante-delivery
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite .env com suas preferências (opcional em desenvolvimento)
```

### 3. Subir os containers
```bash
docker compose up -d --build
```

### 4. Acessar a aplicação
Abra o navegador em: **http://localhost:5000**

### 5. Verificar saúde
```bash
curl http://localhost:5000/health
# {"status": "ok", "db": "connected"}
```

---

## Comandos Úteis

```bash
# Subir em background
docker compose up -d

# Ver logs em tempo real
docker compose logs -f app

# Parar sem remover dados
docker compose stop

# Parar e remover containers (dados persistem no volume)
docker compose down

# Remover containers E dados (cuidado!)
docker compose down -v

# Listar containers rodando
docker ps

# Listar volumes
docker volume ls

# Entrar no container da aplicação
docker exec -it restaurante-app bash

# Entrar no banco de dados
docker exec -it restaurante-db psql -U postgres -d restaurante
```

---

## 🔌 Portas Utilizadas

| Serviço | Porta (host) | Porta (container) |
|---------|-------------|-------------------|
| Aplicação web | 5000 | 5000 |
| PostgreSQL | 5432 | 5432 |

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DB_NAME` | `restaurante` | Nome do banco de dados |
| `DB_USER` | `postgres` | Usuário do banco |
| `DB_PASSWORD` | `postgres123` | Senha do banco |
| `DB_HOST` | `db` | Hostname do container do banco |
| `DB_PORT` | `5432` | Porta do banco |
| `SECRET_KEY` | `...` | Chave secreta Flask (altere em produção!) |
| `FLASK_DEBUG` | `false` | Ativar modo debug (`true` apenas em dev) |
| `APP_PORT` | `5000` | Porta exposta da aplicação |

---

## Banco de Dados

O banco é inicializado automaticamente na primeira execução com as tabelas:

- **produtos** — Cardápio do restaurante
- **clientes** — Cadastro de clientes com endereço
- **pedidos** — Pedidos com status de acompanhamento
- **itens_pedido** — Itens de cada pedido (relação N:N)

Dados de exemplo são inseridos automaticamente para facilitar testes.

---

## API REST

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/produtos` | GET | Lista produtos disponíveis |
| `/api/pedidos` | GET | Lista últimos 50 pedidos |
| `/health` | GET | Status da aplicação e conexão DB |

---

## Docker Compose — Explicação

O `docker-compose.yml` define:

- **Rede** `restaurante-net` (bridge) — isolamento e comunicação entre containers
- **Volume** `postgres-data` — persistência do banco de dados
- **Serviço `db`** — PostgreSQL com healthcheck (app aguarda o banco inicializar)
- **Serviço `app`** — Flask buildado do Dockerfile, conectado ao `db` via hostname

---

## DockerHub

Imagem pública disponível em:

```
docker pull <seu-usuario>/restaurante-delivery:latest
```

Para fazer o push da sua própria imagem:

```bash
docker build -t <usuario>/restaurante-delivery:latest -f Dockerfile ./app
docker login
docker push <usuario>/restaurante-delivery:latest
```

---

## Estrutura do Projeto

```
projeto/
├── app/
│   ├── app.py                  # Aplicação principal Flask
│   ├── requirements.txt        # Dependências Python
│   └── templates/              # Templates Jinja2
│       ├── base.html
│       ├── index.html
│       ├── produtos.html
│       ├── form_produto.html
│       ├── clientes.html
│       ├── form_cliente.html
│       ├── pedidos.html
│       ├── form_pedido.html
│       └── detalhe_pedido.html
├── Dockerfile                  # Build da imagem da aplicação
├── docker-compose.yml          # Orquestração dos containers
├── .env                        # Variáveis de ambiente
├── README.md                   # Este arquivo
└── evidencias/                 # Prints das etapas (capturar manualmente)
```

---

## Evidências

A pasta evidencias/ contém todos os prints das etapas de desenvolvimento local, execução na AWS (EC2), comunicação de containers, persistência em volumes, 
build da imagem e push para o repositório público no DockerHub.
