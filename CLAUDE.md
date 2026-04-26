# Chess Opening Trainer

CLI interativa em Python para jogadores de xadrez estudarem e treinarem
aberturas. O usuário aprende linhas teóricas com contexto histórico de
partidas de mestres e recebe feedback em tempo real do Stockfish sobre
a qualidade dos seus lances.

Público-alvo: jogadores iniantes e intermediários (ELO 1000–1800) que querem
melhorar seu repertório de abertura.

## Stack

- **Python 3.12+** — linguagem principal
- **Click** — framework do CLI (NÃO usar Typer, argparse ou Fire)
- **python-chess** — representação do tabuleiro, parsing PGN, validação de lances
- **stockfish** — bindings Python para o engine via protocolo UCI
- **Rich** — output colorido no terminal (tabuleiro, tabelas, progress bars)
- **SQLite + sqlite3** — persistência de progresso (sem ORM externo)
- **httpx** — cliente HTTP para a Lichess API (quando necessário)
- **pytest** — todos os testes; sem unittest

## Comandos

```bash
# Instalar em modo desenvolvimento
pip install -e ".[dev]"

# Rodar o CLI localmente
python -m pyawn study sicilian
python -m pyawn drill ruy-lopez

# Testes
pytest                        # todos os testes
pytest tests/unit/            # só testes unitários
pytest -k "test_stockfish"    # teste específico
pytest --cov=pyawn    # com cobertura

# Lint e formatação
ruff check .                  # linting
ruff format .                 # formatação
mypy pyawn/           # type checking
```

## Regras do agente

### Sempre fazer
- Ler o arquivo de spec relevante em `.claude/specs/` antes de implementar qualquer feature
- Escrever testes antes da implementação
- Fazer commit ao final de cada task, antes de avançar para a próxima
- Verificar se os testes existentes ainda passam após qualquer mudança

### Nunca fazer
- Modificar o schema do SQLite sem criar uma migration explícita
- Chamar o Stockfish diretamente sem passar pelo módulo `engine/stockfish.py`
- Adicionar dependências ao `pyproject.toml` sem perguntar primeiro
- Apagar ou sobrescrever arquivos de spec em `.claude/specs/`

### Quando parar e perguntar
- Se uma task da spec for ambígua ou contraditória
- Se a implementação exigir mudanças de arquitetura não previstas na spec
- Se os testes existentes quebrarem por um motivo não óbvio
- Se precisar de dados reais da Lichess API para testar (usar fixtures locais)

### Stockfish
- Sempre verificar se o binary do Stockfish está disponível antes de inicializar
- Timeout padrão de 100ms por análise (configurável via env `STOCKFISH_TIMEOUT`)
- Em caso de erro do engine, degradar graciosamente — nunca crashar o CLI

