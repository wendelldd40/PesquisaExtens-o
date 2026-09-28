# Pesquisa de Extensão — Tutores de Animais

Dois questionários mobile independentes, com temas e textos próprios, gravando em
tabelas separadas no Supabase para permitir análise comparativa entre os canais.

| | Canal Rua | Canal Clínica/Petshop |
|---|---|---|
| Arquivo | `questionario-rua.html` | `questionario-clinica.html` |
| Gradiente | laranja → coral → vermelho | azul-petróleo → turquesa → verde-água |
| Tabela | `pesquisa_respostas_rua` | `pesquisa_respostas_clinica` |
| Parâmetro na URL | `?ponto=` (local da abordagem) | `?local=` (clínica parceira) |
| Extra | `?por=` (quem aplicou) | — |

**Canal rua (8 passos):** 4 situações de segurança de alimentos de origem animal
(ovos, carne, leite UHT, queijo coalho) → nome → WhatsApp → opt-in de dicas →
autorização LGPD. As situações vêm antes do pedido de contato de propósito: quem já
investiu respondendo entrega o número com muito menos resistência.

**Canal clínica (9 passos):** 5 perguntas sobre alimentação (critério de escolha da
ração, porcionamento, complementos da dieta, barreira percebida e uma pergunta aberta
de dúvida livre) → nome → WhatsApp **opcional** → opt-in → autorização LGPD.

O WhatsApp pode ser pulado, e quem pula não vê a tela de opt-in — não faz sentido
perguntar se quer receber conteúdo de quem não deixou por onde enviar. Nesse caso
`contato` e `aceita_dicas` ficam nulos, o que distingue "não quis receber" de "nem
foi perguntado".

Cada pergunta da clínica foi escolhida para render duas leituras:

| Pergunta | Para a extensão | Para o gestor da clínica |
|---|---|---|
| O que pesa na escolha da ração | peso da orientação técnica na decisão de compra | quanto a indicação do veterinário realmente move a venda |
| Como mede a porção | risco de super e subalimentação na população atendida | gancho concreto para consulta e acompanhamento nutricional |
| O que come além da ração | prevalência de petisco, mesa e dieta natural | perfil de risco nutricional da clientela |
| O que atrapalha | barreira real de acesso ao cuidado | a objeção que trava serviço e venda, quantificada |
| Dúvida aberta (digitada) | material qualitativo, nas palavras do tutor | pauta de conteúdo e de serviço, direto da boca do cliente |

Ao final, quem responde recebe três notas curtas sobre quantidade, petiscos e
alimentação caseira — a contrapartida de quem cedeu dois minutos.

Uma pergunta por tela, barra de progresso, avanço automático ao escolher, sem
aparência de formulário e sem marca — só a identificação de pesquisa acadêmica.

Ao final do questionário de rua aparece **"Ver o que a ciência diz (x de 4)"**, com a
resposta correta e a explicação de cada situação. O feedback só aparece depois do
envio, então não enviesa as respostas seguintes e ainda cumpre o papel educativo da
extensão.

### Gabarito

| Situação | Correta | Por quê |
|---|---|---|
| Ovos | **b** | A cutícula protege a casca; lavar antes de guardar remove a barreira e leva bactérias para os poros |
| Carne | **c** | Lavar não elimina microrganismos e espalha respingos pela cozinha; quem garante é o cozimento |
| Leite UHT | **c** | Validade vem do tratamento a 130–150 °C + embalagem asséptica; a legislação não permite conservantes |
| Queijo coalho | **c** | Olhaduras podem vir do processo ou de bactérias indesejadas; o que vale é procedência, inspeção e conservação |

---

## 1. Subir o banco

No Supabase → **SQL Editor**, execute na ordem:

1. `sql/01_schema.sql` — tabelas, índices e políticas de segurança (RLS)
2. `sql/02_views_analise.sql` — views prontas para os gráficos
3. `sql/03_seed_exemplo.sql` — cadastre aqui suas clínicas e pontos de coleta
4. `sql/04_conhecimento.sql` — questões da rua, gabarito e views de acerto
5. `sql/05_dicionario.sql` — rótulos das perguntas e alternativas (**gerado pelo build**)
6. `sql/06_nutricao.sql` — bloco de nutrição da clínica e relatório por parceiro
7. `sql/07_crm_e_seguranca.sql` — campos do CRM e **fechamento das views** (leia abaixo)

O `05` é gerado automaticamente por `build.py` a partir das perguntas — é o que faz
os gráficos saírem com o texto que o participante leu na tela em vez de `b`, `c`, `d`.
Não edite à mão: mexa nas perguntas e rode o build de novo.

Se você já tinha rodado a versão anterior do `01`, o `04` faz a migração sozinho
(`add column if not exists`) — não precisa recriar nada.

A pontuação não é calculada pelo formulário: a coluna `acertos` é **gerada pelo
próprio banco** a partir do gabarito em `pesquisa_gabarito`. Ninguém consegue forjar
a nota pela requisição.

A chave `anon` usada nos formulários **só consegue inserir**, nunca ler as respostas.
A leitura fica para usuários autenticados (você, no painel ou no SQL Editor).

## 2. Ligar os formulários

**Já está ligado** ao projeto `xplulvkgumomxjpctdah`. A URL e a chave `anon` estão no
topo do `<script>` dos três arquivos. Se um dia trocar de projeto, é só editar ali
(e, nos questionários, em `build.py`, que os regera).

A chave `anon` é pública por natureza — ela fica visível no código do formulário. O
que impede alguém de usá-la para ler seus dados é o RLS: com os arquivos SQL
aplicados, essa chave **só consegue inserir**, nunca ler.

## 3. Criar o acesso ao painel

O painel lê dados, então exige login. No Supabase:

**Authentication → Users → Add user**, com e-mail e senha, e marque *Auto Confirm User*.
Crie um usuário para cada pessoa da equipe que vai acompanhar os resultados.

Não existe cadastro aberto no painel — quem não estiver nessa lista não entra. Para
ver o painel antes de ter qualquer dado, use o botão **"Ver com dados de demonstração"**
na tela de login: ele monta a interface inteira com números simulados.

## 4. Publicar

Qualquer hospedagem estática serve (Vercel, GitHub Pages, Cloudflare Pages) — são
arquivos únicos, sem dependência externa. Suba os três HTMLs e monte as URLs:

```
Rua:     https://seu-dominio/questionario-rua.html?ponto=orla&por=wendell
Clínica: https://seu-dominio/questionario-clinica.html?local=chamego
```

Gere um QR Code por clínica, cada um com seu `?local=` — é isso que permite ranquear
quais parceiros mais converteram. Na rua, deixe um atalho na tela inicial do celular
com o `?ponto=` do dia.

Para gerar os QR Codes: `python3 gerar_qrcodes.py https://seu-dominio`

O painel fica em `https://seu-dominio/painel.html`. Ele não aparece em lugar nenhum
para quem responde — só quem tem o link e um login entra.

## 5. Analisar

Views prontas para consulta e gráficos:

| View | Serve para |
|---|---|
| `vw_pesquisa_unificada` | base única com os dois canais |
| `vw_resumo_por_canal` | volume, % de adesão às dicas, tempo médio |
| `vw_comparativo_canais` | tabela rua × clínica do relatório |
| `vw_respostas_por_dia` | série temporal da coleta |
| `vw_respostas_por_hora` | melhor horário de abordagem |
| `vw_desempenho_origem` | ranking de clínicas e pontos de rua |
| `vw_funil` | taxa de abandono por etapa |
| `vw_acerto_por_questao` | % de acerto e % de "não sei" em cada situação |
| `vw_distribuicao_alternativas` | quantos marcaram cada letra (barras empilhadas) |
| `vw_distribuicao_acertos` | histograma de 0 a 4 acertos |
| `vw_acertos_por_ponto` | onde o conhecimento é menor, por ponto de coleta |
| `vw_acertos_x_interesse` | quem erra mais quer mais dicas? justificativa da ação |
| `vw_respostas_questoes` | formato longo, uma linha por participante/questão |

Bloco de nutrição (clínica):

| View | Serve para |
|---|---|
| `vw_nutricao_indicadores` | os números da conclusão, já em percentual |
| `vw_nutricao_distribuicao` | distribuição de cada pergunta, com rótulos legíveis |
| `vw_nutricao_orientacao_x_porcao` | quem escolhe pelo veterinário porciona melhor? |
| `vw_nutricao_duvidas` | todas as dúvidas abertas, por clínica |
| `vw_nutricao_termos_duvidas` | termos mais citados, para nuvem de palavras |
| `vw_nutricao_respostas` | formato longo do bloco de nutrição |

**Relatório para o parceiro.** Uma função devolve o consolidado de uma clínica
específica, pronto para virar o PDF que você entrega ao gestor:

```sql
select * from fn_relatorio_clinica('chamego');
```

Exportação para o relatório:

```sql
select * from vw_pesquisa_unificada order by criado_em;
```

## O painel

`painel.html` — mesmo padrão dos questionários: arquivo único, sem dependência
externa, os gráficos são SVG desenhado na hora. Quatro abas:

**Visão geral** — total de respostas, contatos, adesão às dicas e tempo médio;
respostas por dia separadas por canal; ranking de locais de coleta; e o funil de
abandono, que mostra em qual etapa as pessoas desistem.

**Rua · conhecimento** — média de acertos, quantos gabaritaram, taxa de acerto por
situação, histograma da pontuação, a distribuição completa de cada situação (com a
correta destacada — ver *para onde vai o erro* diz mais que a taxa de acerto) e o
acerto por ponto de coleta.

**Clínica · nutrição** — indicadores de porcionamento e complementos, distribuição de
cada pergunta, o cruzamento orientação × porcionamento e as dúvidas abertas, com
ranking dos termos mais citados.

**Contatos** — o CRM: lista com busca, filtro por canal e status, paginação, e por
linha um seletor de status (novo, contatado, respondeu, não responde, descartado),
campo de anotação e botão que abre o WhatsApp com a mensagem já escrita. Status e
anotação gravam direto no banco. Exporta contatos ou a base completa em CSV.

O período (7/30/90 dias) e o local filtram todas as abas de uma vez. Há tema claro e
escuro, e a impressão sai limpa (Ctrl+P) para anexar ao relatório.

O painel lê o dicionário de perguntas do banco, então se você mudar as perguntas e
rodar `python3 build.py` + o `05_dicionario.sql`, os gráficos acompanham sozinhos —
sem mexer no código do painel.

## Detalhes de implementação

- **Sem sinal não perde resposta.** Se o envio falhar, a resposta é guardada no
  `localStorage` e sobe sozinha quando a conexão voltar ou na próxima abertura.
  Essencial na coleta de rua.
- **Duplicidade.** O mesmo número não entra duas vezes (índice único sobre os
  dígitos do telefone); o participante vê "Você já participou" em vez de erro.
- **Telemetria do funil.** Cada etapa registra um evento anônimo em
  `pesquisa_eventos`, o que dá a taxa de abandono — dado forte para o relatório.
- **Validação de telefone brasileiro**: DDD válido, 10 ou 11 dígitos, nono dígito 9,
  rejeita sequências repetidas.
- **Acessibilidade**: respeita `prefers-reduced-motion`, alvos de toque ≥ 44px,
  safe-area do iPhone, funciona de 320px a tablets.
- **Segurança das views.** O `07` corrige um risco real: por padrão o Supabase dá
  SELECT no schema `public` ao papel `anon`, e uma view comum roda com os privilégios
  do dono, **ignorando o RLS das tabelas de base**. Sem essa correção, qualquer pessoa
  com a chave `anon` (visível no formulário) leria nome e telefone de todo mundo pelas
  views. O script marca todas com `security_invoker = on` e revoga o acesso de `anon`.
  A consulta de conferência está comentada no fim do arquivo.
- **Paleta dos gráficos** validada para daltonismo e contraste nos temas claro e
  escuro, com rótulo direto em toda barra — a cor nunca carrega a informação sozinha.

## Arquivos

```
questionario-rua.html        formulário do canal rua (single-file)
questionario-clinica.html    formulário do canal clínica (single-file)
painel.html                  painel de resultados + CRM (single-file)
build.py                     gera os dois a partir de um template único
verificar.py                 percorre o fluxo dos questionários e tira screenshots
verificar_painel.py          percorre as abas do painel e tira screenshots
gerar_qrcodes.py             gera os QR Codes dos locais cadastrados
sql/01_schema.sql            tabelas, índices e RLS
sql/02_views_analise.sql     views de análise
sql/03_seed_exemplo.sql      locais e pontos de exemplo
sql/04_conhecimento.sql      questões da rua, gabarito e views de acerto
sql/05_dicionario.sql        rótulos (GERADO por build.py, não editar)
sql/06_nutricao.sql          bloco de nutrição e relatório por clínica
sql/07_crm_e_seguranca.sql   campos de CRM e fechamento das views
screenshots/                 verificação visual das telas
```

## Mexer nas perguntas

Todo o roteiro vive em `build.py`. Cada passo é um dicionário na lista `PASSOS` do
tema, e o HTML monta as telas a partir dele — adicionar, remover ou reordenar
perguntas é editar essa lista e rodar `python3 build.py`.

```python
{
  "tipo": "escolha", "campo": "q5_pescado", "selo": "Situação 5", "tema": "Pescado",
  "titulo": "...",
  "opcoes": [{"v": "a", "t": "..."}, {"v": "b", "t": "..."}],
  "correta": "b",
  "explicacao": "...",
}
```

Tipos disponíveis: `texto`, `tel`, `longo` (textarea), `escolha` e `consent`.
Qualquer passo aceita `"opcional": True` (ganha um botão "Pular") e
`"exigeCampo": "contato"`, que só mostra o passo se aquele campo tiver sido
preenchido. O nome em `campo` é a
coluna correspondente no Supabase — ao criar uma questão nova, acrescente a coluna
na tabela e a linha em `pesquisa_gabarito`.

Depois de qualquer alteração, rode `python3 verificar.py`: ele percorre o fluxo
inteiro dos dois questionários em viewport de celular, confere as validações, o
gabarito e a gravação, e atualiza os screenshots.
