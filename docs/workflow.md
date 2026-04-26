# Workflow de Desenvolvimento — pyawn

## Filosofia

As specs em `.claude/specs/` definem **o quê e por quê**. O código define o **como**.
Spec e código precisam estar em sincronia em cada commit — spec sem código é wishful thinking;
código sem spec é dívida de documentação.

---

## Fluxo Spec-First (SDD adaptado)

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. LEIA a spec da feature antes de tocar no código               │
│    Arquivo: .claude/specs/NN-<feature>.md                        │
│    Se não existe → crie a spec primeiro                          │
├──────────────────────────────────────────────────────────────────┤
│ 2. IMPLEMENTE contra a spec                                      │
│    Trate os critérios de aceitação como checklist                │
│    Escreva os testes antes da implementação                      │
├──────────────────────────────────────────────────────────────────┤
│ 3. A implementação revelou que a spec estava errada?             │
│    Sim → atualize a spec ANTES de continuar o código             │
│    Registre a decisão em docs/spec-changelog.md                  │
├──────────────────────────────────────────────────────────────────┤
│ 4. Padrões descobertos → steering/tech.md                        │
│    Estrutura que mudou → steering/structure.md                   │
│    Decisões arquiteturais → spec da feature afetada              │
├──────────────────────────────────────────────────────────────────┤
│ 5. COMMIT: spec + código juntos, nunca separados                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## O que vai onde

| Tipo de decisão | Onde registrar |
|-----------------|----------------|
| Contrato público (interface, assinaturas, comportamento externo) | `.claude/specs/NN-feature.md` |
| Mudança em relação à spec original | `docs/spec-changelog.md` |
| Padrão de implementação descoberto | `.claude/steering/tech.md` |
| Estrutura de diretórios alterada | `.claude/steering/structure.md` |
| Detalhe interno de implementação | Nenhum lugar — o código fala por si |
| Regras e preferências do agente | `CLAUDE.md` |

---

## Regras de ouro

- **Nunca commitar código sem spec correspondente** — se a feature não tem spec, crie antes
- **Nunca retrofitar spec depois do código** — se a spec mudou, atualize-a antes de seguir
- **Specs definem contratos, não detalhes** — "use `Text` objects" pertence ao steering, não à spec
- **`spec-changelog.md` é o diff humano** — para cada divergência, registre: o quê mudou, por quê e quando

---

## Ciclo por feature

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌────────┐
│  Leia spec  │────▶│  Escreva     │────▶│  Implemente   │────▶│ Commit │
│             │     │  testes      │     │               │     │        │
└─────────────┘     └──────────────┘     └───────┬───────┘     └────────┘
                                                  │
                                          spec estava errada?
                                                  │ sim
                                                  ▼
                                         ┌────────────────┐
                                         │ Atualize spec  │
                                         │ + changelog    │
                                         └────────────────┘
```

---

## Nomenclatura de specs

```
.claude/specs/
  01-cli.md              # prefixo numérico para ordenação
  02-board-display.md
  03-openings-data.md
  ...
```

Prefixos sugeridos por área:
- `0X` — infraestrutura e CLI
- `1X` — dados e abertura
- `2X` — modos de uso (study, drill)
- `3X` — engine e análise
- `9X` — features futuras / pós-MVP
