# Santa RP Bot

## Railway
1. Envie todos estes arquivos para um repositório no GitHub.
2. No Railway, crie um serviço a partir do repositório.
3. Configure a variável `DISCORD_TOKEN` com o token do bot.
4. O comando de inicialização é definido pelo `Procfile`.

## Arquivos
- `bot.py` — código principal.
- `requirements.txt` — dependências.
- `Procfile` — inicialização no Railway.
- `runtime.txt` — versão do Python.
- `.env.example` — exemplo da variável do token.
- `santa_data.json` — dados da votação/meta RP.
- `santa_ids.json` — IDs dos jogadores, iniciando em 84.
- `santa_money.json` — economia dos jogadores.

## Importante
No `bot.py`, preencha os IDs do servidor/cargos onde está indicado. O bot precisa de `Gerenciar Cargos` e o cargo dele deve ficar acima dos cargos que ele vai atribuir.
