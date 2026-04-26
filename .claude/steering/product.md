---
inclusion: always
---

# Product — pyawn

## Visão

CLI interativa para jogadores de xadrez (ELO 1000–1800) memorizarem aberturas, suas variações e entenderem os planos estratégicos por trás de cada linha. Inspirado no Lotus Chess e na UX do [chs](https://github.com/nickzuber/chs).

## Objetivo do usuário

Após uso regular, o jogador deve conseguir:
- Reproduzir de memória as linhas principais das 5 aberturas do MVP
- Reconhecer variações e adaptar o jogo quando o oponente sai da linha principal
- Entender o plano estratégico (não apenas a sequência de lances)

## Público-alvo

Jogadores iniciantes e intermediários (ELO 1000–1800) que querem construir um repertório sólido de aberturas.

## Escopo do MVP

### 5 aberturas

| ID | Abertura | Variações incluídas |
|----|----------|---------------------|
| `sicilian` | Defesa Siciliana | Najdorf, Dragon, Scheveningen |
| `ruy-lopez` | Ruy López (Abertura Espanhola) | Marshall, Berlim |
| `french` | Defesa Francesa | Winawer, Clássica, Advance |
| `caro-kann` | Defesa Caro-Kann | Clássica, Advance, Troca |
| `italian` | Jogo Italiano | Giuoco Piano, Gambito Evans |

### Fora do MVP
- Aberturas de peão da dama (Queen's Gambit, etc.)
- Modo multiplayer ou online
- Integração runtime com Lichess API
- Suporte a Windows (Stockfish tem dependências diferentes)

## Comandos principais

```
python -m pyawn          # abre menu principal
python -m pyawn study    # menu de aberturas → sessão de estudo
python -m pyawn drill    # menu de aberturas → sessão de treino
```

## Modos de uso

### `study` — Aprendizado guiado
- Usuário navega por um menu hierárquico: abertura → variação
- O tabuleiro é renderizado no terminal a cada lance
- Usuário **digita o próximo lance** em notação algébrica (ex: `e4`, `Nf3`, `O-O`)
- Cada lance vem acompanhado de texto explicando o plano estratégico
- Stockfish **não é usado** neste modo

### `drill` — Treino com validação
- Usuário seleciona abertura + variação via menu
- Sistema apresenta a posição e o usuário tenta reproduzir a linha
- Stockfish valida se o lance segue a linha de abertura estudada
- **Dois níveis de dificuldade:**
  1. **Linha principal** — treino de memória pura
  2. **Variações** — testa adaptação quando o "oponente" desvia da linha
- Feedback imediato: acerto, erro com dica, ou erro com resposta correta

## Dados das aberturas

Dados armazenados **localmente** no pacote (JSON + PGN). Sem chamadas de rede em runtime. Dataset curado manualmente ou extraído offline de fontes abertas (Lichess, TWIC).

## Persistência

SQLite local (`~/.pyawn/progress.db`) rastreia:
- Quais aberturas e variações foram estudadas
- Resultados por sessão de drill (acertos, erros, data)
- Histórico de progresso por abertura

## Princípios de UX

- Interface 100% terminal, sem browser ou GUI
- Menu interativo para seleção (nunca forçar o usuário a decorar nomes de comando)
- Tabuleiro sempre visível durante estudo e drill
- Degradação graciosa se Stockfish não estiver disponível (drill funciona sem avaliação de centipawns, apenas valida a linha)
