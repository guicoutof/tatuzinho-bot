# Tatuzinho Bot ⚽

Bot do Discord para previsão de resultados de partidas de futebol utilizando machine learning.

## Features

- `/predict <home_team> <away_team>` — Prevê o resultado de uma partida com probabilidades, placar mais provável e nível de confiança.

## Pré-requisitos

- Python 3.12+
- Token de bot do Discord
- (Opcional) Docker

## Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/tatuzinho-bot.git
   cd tatuzinho-bot
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copie o arquivo de ambiente e preencha as variáveis:
   ```bash
   cp .env.example .env
   ```

### Variáveis de Ambiente

| Variável | Obrigatório | Descrição |
|---|---|---|
| `DISCORD_BOT_TOKEN` | Sim | Token do bot do Discord |
| `API_BASE_URL` | Não | URL base da API de previsões (default: `https://tatuzinho.onrender.com`) |
| `PROXY_URL` | Não | Proxy para conexão com Discord (formato: `http://user:pass@host:port`) |

## Execução

### Local

```bash
python -m discord_bot.main
```

### Docker

```bash
docker build -t tatuzinho-bot .
docker run --env-file .env tatuzinho-bot
```

## Estrutura do Projeto

```
tatuzinho-bot/
├── discord_bot/
│   ├── __init__.py
│   ├── main.py          # Ponto de entrada e health server
│   ├── config.py        # Carregamento de variáveis de ambiente
│   └── cogs/
│       ├── __init__.py
│       └── predictions.py  # Comando /predict
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Comandos

### `/predict`

Prevê o resultado de uma partida de futebol.

**Uso:** `/predict home_team: Brasil away_team: Argentina`

**Resposta:** Embed com probabilidades (casa, empate, visitante), barras de progresso, placar mais provável e confiança.
