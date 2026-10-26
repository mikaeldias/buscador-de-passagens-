# buscador-de-passagens

Busca preços de passagens (Google Flights via SerpApi) para trechos definidos em
[config.py](config.py) e envia as cotações para um grupo do Telegram. Roda sem servidor,
no GitHub Actions, a cada 3 horas.

Cada cotação traz: origem e destino, data, preço, quantidade de escalas (e por onde),
tempo total de voo, horários e companhia. Também indica se o menor preço caiu ou subiu
desde a última consulta daquela data.

## Como a cota da SerpApi é respeitada

- Antes de buscar, o robô consulta o saldo real da conta em `account.json`, que não consome cota.
- O saldo (menos uma `RESERVA`) é dividido pelas execuções que faltam até o dia de renovação
  (`DIA_RESET_COTA`). Com 250 buscas/mês e execução a cada 3h, isso dá cerca de 1 busca por execução.
  Se sobrar saldo no fim do ciclo, ele é aproveitado. Se faltar, as buscas são espaçadas.
- Cada busca cobre todos os aeroportos da cidade (`GRU,CGH` → `GIG,SDU`), só ida.
- As combinações trecho × data (`OFFSETS_DIAS`) são percorridas em rodízio, então todas
  as datas de todos os trechos são consultadas igualmente.

## Configuração

1. **Bot do Telegram**: fale com o [@BotFather](https://t.me/BotFather), crie um bot (`/newbot`)
   e guarde o token. Adicione o bot ao grupo e mande uma mensagem qualquer no grupo.
2. **chat_id do grupo**: abra `https://api.telegram.org/bot<TOKEN>/getUpdates` e copie o
   `chat.id` (começa com `-`).
3. **SerpApi**: copie sua API key em https://serpapi.com/manage-api-key.
4. No GitHub, em *Settings → Secrets and variables → Actions*, crie os segredos
   `SERPAPI_KEY`, `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.
5. Ajuste os trechos e o orçamento em [config.py](config.py). Se mudar `INTERVALO_HORAS`,
   altere também o cron em [.github/workflows/buscar.yml](.github/workflows/buscar.yml).
   Ajuste `DIA_RESET_COTA` para o dia em que sua cota renova (veja no painel da SerpApi).

Para testar, rode o workflow manualmente em *Actions → Buscar passagens → Run workflow*.

## Rodando localmente

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest              # testes
.venv/bin/python main.py --dry-run      # mostra uma mensagem de exemplo, sem chamar APIs
cp .env.example .env                    # preencha as chaves
.venv/bin/python main.py                # execução real (consome cota)
```
