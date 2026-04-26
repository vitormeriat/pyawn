# Spec Changelog

Registro de divergências entre a especificação inicial e a implementação real.
Cada entrada documenta o quê mudou, por quê e o impacto nas specs afetadas.

---

## v0.2 — Interface inicial (2026-04-26)

**Commit:** `54b81ae`
**Specs afetadas:** `02-board-display.md`, `steering/structure.md`, `steering/tech.md`

### Mudanças

#### 1. Módulo `ui/` adicionado (não previsto)

- **Spec original:** sem menção a um módulo `ui/`
- **Implementação:** criado `src/pyawn/ui/theme.py` com constantes de cor, símbolos Unicode e box-drawing
- **Motivo:** centralizar constantes visuais evita duplicação entre `renderer.py` e `cli.py`
- **Ação:** atualizar `steering/structure.md` para incluir `ui/`

#### 2. Board sem separadores de célula

- **Spec original** (`02-board-display.md`): layout com bordas `┌──┬──┐` entre casas
- **Implementação:** casas sem separadores — blocos coloridos contíguos, estilo chs
- **Motivo:** separadores adicionam ruído visual; o contraste de cor das casas já delimita bem
- **Contrato afetado:** somente o layout visual; a assinatura de `render_board()` permanece idêntica à spec
- **Ação:** atualizar critério de aceitação de layout em `02-board-display.md`

#### 3. Padrão `_menu_item()` com `Text` objects

- **Spec original** (`01-cli.md`): menus com `click.prompt()` + `click.Choice()`
- **Implementação:** helper `_menu_item(key, label, note)` usando `rich.Text` para itens de menu
- **Motivo:** `[b]` em f-strings com markup Rich é interpretado como tag bold — `Text` objects evitam o parser de markup e permitem colchetes literais
- **Contrato afetado:** detalhe interno de `cli.py`; comportamento externo (menus navegáveis) está conforme a spec
- **Ação:** registrar padrão em `steering/tech.md`

#### 4. Stub `openings/loader.py` (dados hardcoded)

- **Spec original** (`03-openings-data.md`): loader lê JSON de `openings/data/*.json`
- **Implementação:** dados hardcoded em dict Python; sem arquivos JSON ainda
- **Motivo:** validar UI sem precisar criar dataset completo — os JSONs vêm na próxima iteração
- **Contrato afetado:** as funções públicas (`list_openings`, `get_opening`) têm a mesma assinatura da spec; apenas a fonte dos dados é diferente
- **Ação:** nenhuma — divergência intencional e temporária; marcar como pendente na spec

---

## v0.1 — Specs e steering iniciais (2026-04-26)

**Commit:** `a909271`
**Specs criadas:**
- `01-cli.md` — CLI entrypoint e navegação
- `02-board-display.md` — renderização do tabuleiro
- `03-openings-data.md` — dados de abertura (formato JSON + loader)
- `04-study-mode.md` — modo estudo guiado
- `05-drill-mode.md` — modo treino com validação
- `06-stockfish-engine.md` — wrapper UCI do Stockfish
- `07-progress-db.md` — persistência SQLite

**Steering criados:**
- `product.md` — visão do produto, MVP, comandos
- `structure.md` — layout de diretórios e invariantes de arquitetura
- `tech.md` — stack, convenções, ferramentas

**Status:** nenhuma implementação — specs representam intenção inicial pura.

---

## Template para novas entradas

```markdown
## vX.Y — <descrição curta> (AAAA-MM-DD)

**Commit:** `<hash>`
**Specs afetadas:** `<arquivo>`

### Mudanças

#### N. <título da mudança>

- **Spec original:** <o que a spec dizia>
- **Implementação:** <o que foi feito de diferente>
- **Motivo:** <por que divergiu>
- **Contrato afetado:** <impacto na interface pública, se houver>
- **Ação:** <o que precisa ser atualizado nas specs/steering>
```
