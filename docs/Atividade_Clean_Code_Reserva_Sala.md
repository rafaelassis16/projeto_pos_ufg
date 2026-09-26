# Atividade Clean Code - Reserva de sala

## Como executar o MVP para testes

Os comandos abaixo devem ser executados no PowerShell a partir da pasta interna do projeto. Os sublinhados dos nomes de arquivos devem ser digitados normalmente, sem barras invertidas (`\`).

### Teste visual pelo frontend

1. Acesse a pasta do frontend:

```powershell
cd "C:\Users\rafaelassis\Documents\VS Code\projeto_pos_ufg\projeto_pos_ufg\frontend"
```

2. Instale as dependencias, caso seja a primeira execucao:

```powershell
npm install
```

3. Inicie a aplicacao:

```powershell
npm run dev
```

4. Abra no navegador o endereco exibido no terminal, normalmente `http://localhost:5173/`, e selecione a aba **Reserva de Sala**.

Para validar as regras, podem ser usados estes exemplos:

| Caso | Sala | Data | Inicio | Termino | Resultado esperado |
|------|------|------|--------|---------|--------------------|
| Conflito | SALA-01 | 26/09/2026 | 10:30 | 11:30 | Reserva indisponivel |
| Limite permitido | SALA-01 | 26/09/2026 | 11:00 | 12:00 | Reserva disponivel |
| Sala diferente | SALA-02 | 26/09/2026 | 10:30 | 11:30 | Reserva disponivel |
| Horario invalido | SALA-01 | 26/09/2026 | 11:00 | 11:00 | Mensagem de erro |

O frontend usa dados ficticios locais para demonstrar a regra de conflito. A aba **Reserva de Sala** pode ser testada sem iniciar o backend.

### Testes automatizados

Em outro terminal, retorne para a pasta interna do projeto e ative o ambiente virtual:

```powershell
cd "C:\Users\rafaelassis\Documents\VS Code\projeto_pos_ufg\projeto_pos_ufg"
.\.venv\Scripts\Activate.ps1
```

Execute os testes da reserva de sala:

```powershell
python -m pytest app/tests/unit/test_room_booking.py
```

O resultado esperado e `6 passed`.

## 1. Problema definido

O problema escolhido foi um toy problem de reserva de sala. O objetivo e verificar se uma nova reserva conflita com reservas ja existentes da mesma sala no mesmo dia.

### Entradas

| Campo | Tipo | Regra |
|-------|------|-------|
| `room_id` | `str` | Identificador da sala. Nao pode ser vazio. |
| `booking_date` | `date` | Data da reserva. |
| `start_time` | `time` | Horario inicial da reserva. |
| `end_time` | `time` | Horario final da reserva. Deve ser posterior ao inicio. |
| `existing_reservations` | `list[Reservation]` | Reservas ja cadastradas para comparacao. |

### Saidas

| Saida | Descricao |
|-------|-----------|
| `ConflictResult.has_conflict` | `True` quando existe sobreposicao de horarios para a mesma sala no mesmo dia. |
| `ConflictResult.conflicting_reservations` | Tupla com as reservas que conflitam com a reserva solicitada. |
| `RoomBookingService.can_reserve` | Atalho booleano que retorna `True` quando a reserva pode ser feita. |
| `InvalidReservationError` | Excecao customizada para entradas invalidas. |

### Regras esperadas

1. Uma reserva so conflita com outra se for da mesma sala e do mesmo dia.
2. Existe conflito quando `inicio_solicitado < fim_existente` e `fim_solicitado > inicio_existente`.
3. Uma reserva das 10h as 11h impede outra das 10h30 as 11h30.
4. Uma reserva das 10h as 11h permite outra que comece exatamente as 11h.
5. O termino deve ser posterior ao inicio.
6. O identificador da sala nao pode ser vazio.
7. A solucao deve usar apenas dados ficticios e nao deve depender de banco de dados.

### Exemplos

| Caso | Reserva existente | Nova reserva | Resultado esperado |
|------|-------------------|--------------|--------------------|
| Funcionamento normal | SALA-01, 26/09/2026, 10h-11h | SALA-01, 26/09/2026, 10h30-11h30 | Conflito |
| Limite permitido | SALA-01, 26/09/2026, 10h-11h | SALA-01, 26/09/2026, 11h-12h | Sem conflito |
| Sala diferente | SALA-01, 26/09/2026, 10h-11h | SALA-02, 26/09/2026, 10h30-11h30 | Sem conflito |
| Dia diferente | SALA-01, 26/09/2026, 10h-11h | SALA-01, 27/09/2026, 10h30-11h30 | Sem conflito |
| Erro | - | SALA-01, 26/09/2026, 11h-11h | `InvalidReservationError` |
| Erro | - | sala vazia, 26/09/2026, 10h-11h | `InvalidReservationError` |

## 2. Orientacao de geracao enviada ao agente

Foi usado o agente local `.agents/skills/Agente-Desenvolvedor-de-Software`.

Convencoes do projeto e criterios explicitados:

- Linguagem Python 3.10+.
- Nomes devem revelar intencao, por exemplo `Reservation`, `ConflictResult`, `RoomBookingService`.
- Cada funcao deve ter uma responsabilidade unica: validar reserva, detectar sobreposicao, retornar resultado.
- Usar type hints em todos os atributos e assinaturas publicas.
- Usar docstrings Google Style nas classes/funcoes publicas.
- Usar excecao customizada para violacao de regra de negocio.
- Nao adicionar dependencias novas ao `requirements.txt`.
- Nao acessar banco de dados nem arquivos externos.
- Evitar comentarios que repitam o codigo; comentar apenas quando houver decisao de negocio nao obvia.
- Criar testes unitarios Pytest para casos normais, de limite e de erro.
- Preservar as regras de negocio antes de qualquer ajuste estetico.

## 3. Revisao critica inicial

Leitura humana da solucao gerada:

| Classificacao | Local | Apontamento | Justificativa |
|---------------|-------|-------------|---------------|
| [melhora] | `app/services/room_booking.py` | O modulo foi isolado em `services`, sem misturar com banco ou rotas. | Mantem escopo pequeno e facilita testes unitarios. |
| [melhora] | `Reservation` | Os nomes dos campos sao explicitos. | Reduz ambiguidade entre data, sala e horarios. |
| [bloqueia] | validacao de horarios | E obrigatorio rejeitar `end_time <= start_time`. | Sem isso, reservas com duracao zero ou negativa poderiam passar. |
| [bloqueia] | validacao de sala | E obrigatorio rejeitar `room_id` vazio. | Sala vazia impediria a regra "mesma sala" de ter significado confiavel. |
| [melhora] | resultado | Retornar tambem as reservas conflitantes ajuda a diagnosticar o problema. | Melhora uso futuro sem quebrar a saida booleana. |
| [estilo] | dataclasses imutaveis | `frozen=True` foi usado para reservas e resultados. | Preferencia de imutabilidade em objetos de valor. |

Checklist adicional:

- Nao ha segredos, tokens ou dados reais no codigo.
- Nao foram adicionadas dependencias externas.
- A validacao de entrada cobre sala vazia e horario final invalido.
- Os testes representam as regras definidas na especificacao.

## 4. Revisao solicitada ao agente

Apontamentos do agente, com localizacao e justificativa:

| Classificacao | Local | Apontamento | Justificativa |
|---------------|-------|-------------|---------------|
| [bloqueia] | `RoomBookingService._validate_reservation` | Garantir que o fim seja posterior ao inicio. | Afeta a correcao da regra principal. |
| [bloqueia] | `RoomBookingService._validate_reservation` | Garantir que `room_id` nao esteja vazio. | Afeta a confiabilidade da comparacao por sala. |
| [melhora] | `ConflictResult` | Expor as reservas conflitantes alem do booleano. | Facilita explicacao do resultado e evolucao para API. |
| [melhora] | `test_room_booking.py` | Incluir teste de fronteira para uma reserva que comeca exatamente no fim da anterior. | Evita regressao na regra mais importante do enunciado. |
| [estilo] | docstrings | Manter docstrings nas classes e metodos publicos. | Ajuda manutencao e esta alinhado ao skill usado. |

## 5. Ajustes selecionados

Foram mantidos os ajustes que preservam a regra de negocio:

- `InvalidReservationError` para entradas invalidas.
- `ConflictResult` com booleano e lista de conflitos.
- Testes especificos para sobreposicao, fronteira permitida, sala diferente, dia diferente e erros.
- Nenhuma nova dependencia.

## 6. Conferencia da solucao

Comando usado:

```bash
pytest app/tests/unit/test_room_booking.py
```

Resultado esperado:

```text
6 passed
```

Arquivos principais:

- `app/services/room_booking.py`
- `app/tests/unit/test_room_booking.py`
