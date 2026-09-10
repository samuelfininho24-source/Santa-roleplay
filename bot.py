import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from pathlib import Path

# ============================================================
# SANTA RP — BOT DE WHITELIST, META RP E APROVAÇÃO DE PERSONAGEM
# Requer Python 3.10+ e discord.py 2.x
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")

# IDs DO SEU SERVIDOR — TROQUE PELOS IDs REAIS
GUILD_ID = 0
CATEGORIA_WHITELIST_ID = 0

# Cargo que todo jogador sem whitelist possui
CARGO_SEM_REGISTRO_ID = 0

# Os 2 cargos recebidos quando a whitelist for aprovada
CARGO_WHITELIST_1_ID = 0
CARGO_WHITELIST_2_ID = 0

# Cargo usado no /aprovarpersonagem
CARGO_PERSONAGEM_APROVADA_ID = 0
CARGO_FACCAO_APROVADA_ID = 0
CARGO_EMPRESA_APROVADA_ID = 0
CARGO_CORPORACAO_APROVADA_ID = 0

# Link do servidor Roblox informado por você.
# Coloque o link do seu servidor aqui.
ROBLOX_SERVER_LINK = "https://www.roblox.com/share?code=ef1ac8ea6be62f43b47676811a5fb540&type=Server"

# Arquivo simples para guardar o número da whitelist e votos
DATA_FILE = Path("santa_data.json")
MONEY_FILE = Path("santa_money.json")

# Economia inicial
START_CASH = 1000
START_BANK = 0

BLACK = 0x000000

QUESTOES = [
    {
        "pergunta": "O que é RDM?",
        "opcoes": {
            "A": "Matar outro jogador sem uma situação de RP que justifique",
            "B": "Roubar um veículo durante uma perseguição",
            "C": "Sair do servidor depois de uma cena",
            "D": "Conversar fora do personagem"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é VDM?",
        "opcoes": {
            "A": "Usar um veículo para atropelar/matar alguém sem contexto de RP",
            "B": "Usar voz no jogo",
            "C": "Entrar em uma empresa",
            "D": "Fazer uma abordagem policial"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Metagaming?",
        "opcoes": {
            "A": "Usar uma informação obtida fora do RP dentro do RP",
            "B": "Criar um personagem novo",
            "C": "Comprar uma casa",
            "D": "Trabalhar como médico"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Powergaming?",
        "opcoes": {
            "A": "Forçar ações ou situações impossíveis/sem dar chance de reação ao outro jogador",
            "B": "Trabalhar em uma empresa",
            "C": "Fazer uma corrida",
            "D": "Usar um veículo oficial"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que significa RP?",
        "opcoes": {
            "A": "Roleplay: interpretar um personagem dentro da situação proposta",
            "B": "Regras Públicas",
            "C": "Ranking de Polícia",
            "D": "Registro de Pessoa"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Anti-RP?",
        "opcoes": {
            "A": "Uma atitude que quebra a interpretação e as regras da situação de RP",
            "B": "Uma profissão dentro da cidade",
            "C": "Um tipo de veículo",
            "D": "Uma forma de ganhar dinheiro"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Combat Logging?",
        "opcoes": {
            "A": "Sair do jogo para evitar uma situação de RP",
            "B": "Trocar de roupa",
            "C": "Entrar em uma casa",
            "D": "Mudar de profissão"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é Fear RP?",
        "opcoes": {
            "A": "Valorizar a vida do personagem diante de uma situação de perigo",
            "B": "Ter medo de entrar no servidor",
            "C": "Usar uma roupa escura",
            "D": "Fugir de uma profissão"
        },
        "resposta": "A"
    },
    {
        "pergunta": "O que é OOC?",
        "opcoes": {
            "A": "Algo dito ou feito fora da interpretação do personagem",
            "B": "Uma corporação policial",
            "C": "Uma empresa",
            "D": "Um veículo"
        },
        "resposta": "A"
    },
    {
        "pergunta": "Durante uma situação de RP, qual é a melhor atitude?",
        "opcoes": {
            "A": "Respeitar as regras, interpretar a situação e dar continuidade ao RP",
            "B": "Abandonar a situação sempre que perder",
            "C": "Usar informações externas para ganhar vantagem",
            "D": "Ignorar os outros jogadores"
        },
        "resposta": "A"
    }
]


def carregar_dados():
    if not DATA_FILE.exists():
        return {"proximo_numero": 1, "votos_sim": [], "votos_nao": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"proximo_numero": 1, "votos_sim": [], "votos_nao": []}


def salvar_dados(dados):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


dados = carregar_dados()


def carregar_economia():
    if not MONEY_FILE.exists():
        return {}
    try:
        with open(MONEY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def salvar_economia(economia):
    with open(MONEY_FILE, "w", encoding="utf-8") as f:
        json.dump(economia, f, ensure_ascii=False, indent=2)


economia = carregar_economia()


def obter_conta(user_id):
    chave = str(user_id)
    if chave not in economia:
        economia[chave] = {"cash": START_CASH, "bank": START_BANK}
        salvar_economia(economia)
    return economia[chave]


def dinheiro(valor):
    return f"R$ {valor:,.0f}".replace(",", ".")


def embed_preto(titulo, descricao):
    return discord.Embed(
        title=titulo,
        description=descricao,
        color=BLACK
    )


intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True


def cargo(guild, role_id):
    return guild.get_role(role_id)


class MetaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Sim",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="santa_meta_sim"
    )
    async def sim(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        if user_id in dados["votos_sim"] or user_id in dados["votos_nao"]:
            await interaction.response.send_message(
                "❌ Você já votou nessa meta.",
                ephemeral=True
            )
            return

        dados["votos_sim"].append(user_id)
        salvar_dados(dados)
        await atualizar_meta(interaction.message)
        await interaction.response.send_message(
            "✅ Seu voto foi registrado como **Sim**.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Não",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="santa_meta_nao"
    )
    async def nao(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        if user_id in dados["votos_sim"] or user_id in dados["votos_nao"]:
            await interaction.response.send_message(
                "❌ Você já votou nessa meta.",
                ephemeral=True
            )
            return

        dados["votos_nao"].append(user_id)
        salvar_dados(dados)
        await atualizar_meta(interaction.message)
        await interaction.response.send_message(
            "❌ Seu voto foi registrado como **Não**.",
            ephemeral=True
        )


async def atualizar_meta(message):
    sim = len(dados["votos_sim"])
    nao = len(dados["votos_nao"])

    embed = embed_preto(
        "🌆 META RP — CIDADE ON 🌆",
        f"""👮 Corporações: **ATIVAS**
🏥 Hospital: **ATIVO**
🚒 Bombeiros: **ATIVOS**
🏢 Empresas: **ABERTAS**

━━━━━━━━━━━━━━━━━━━━

📢 **A cidade deve abrir o RP?**

🗳️ **Votos:** {sim + nao} VOTOS

━━━━━━━━━━━━━━━━━━━━"""
    )

    embed.set_footer(text=f"✅ {sim} votos a favor • ❌ {nao} votos contra")
    await message.edit(embed=embed, view=MetaView())


class AbrirWhitelistView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir Whitelist",
        emoji="📋",
        style=discord.ButtonStyle.primary,
        custom_id="santa_abrir_whitelist"
    )
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        membro = interaction.user

        categoria = guild.get_channel(CATEGORIA_WHITELIST_ID)
        if categoria is None or not isinstance(categoria, discord.CategoryChannel):
            await interaction.response.send_message(
                "❌ A categoria da whitelist não foi configurada corretamente.",
                ephemeral=True
            )
            return

        # Evita duas whitelists simultâneas da mesma pessoa.
        for canal in categoria.channels:
            if canal.topic == f"whitelist:{membro.id}":
                await interaction.response.send_message(
                    f"❌ Você já possui uma whitelist aberta: {canal.mention}",
                    ephemeral=True
                )
                return

        numero = dados["proximo_numero"]
        dados["proximo_numero"] += 1
        salvar_dados(dados)

        nome = f"whitelist-{numero:03d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            membro: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                read_message_history=True
            )
        }

        # Permite a equipe com Manage Channels ver os canais.
        for role in guild.roles:
            if role.permissions.manage_channels:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )

        canal = await guild.create_text_channel(
            nome,
            category=categoria,
            overwrites=overwrites,
            topic=f"whitelist:{membro.id}"
        )

        await interaction.response.send_message(
            f"✅ Sua whitelist **#{numero:03d}** foi criada: {canal.mention}",
            ephemeral=True
        )

        embed = embed_preto(
            f"📋 WHITELIST #{numero:03d}",
            f"""Olá, {membro.mention}!

Responda às **10 perguntas** abaixo usando os botões **A, B, C ou D**.

🎯 **Aprovação:** 8/10 ou mais
❌ Menos de 8 acertos = reprovado

Boa sorte!"""
        )
        await canal.send(embed=embed)
        await enviar_pergunta(canal, membro, 0, 0)


async def enviar_pergunta(canal, membro, indice, acertos):
    if indice >= len(QUESTOES):
        if acertos >= 8:
            resultado = "🎉 **WHITELIST APROVADA!**"
            descricao = f"Você acertou **{acertos}/10** perguntas."

            sem_registro = cargo(canal.guild, CARGO_SEM_REGISTRO_ID)
            cargo1 = cargo(canal.guild, CARGO_WHITELIST_1_ID)
            cargo2 = cargo(canal.guild, CARGO_WHITELIST_2_ID)

            erros = []
            if sem_registro:
                try:
                    await membro.remove_roles(sem_registro, reason="Whitelist aprovada")
                except discord.Forbidden:
                    erros.append("Não consegui remover o cargo Sem Registro.")

            for r in (cargo1, cargo2):
                if r:
                    try:
                        await membro.add_roles(r, reason="Whitelist aprovada")
                    except discord.Forbidden:
                        erros.append(f"Não consegui adicionar o cargo {r.name}.")
                else:
                    erros.append("Um dos cargos de aprovação não foi configurado.")

            if erros:
                descricao += "\n\n⚠️ " + "\n".join(erros)

            await canal.send(embed=embed_preto(resultado, descricao))
        else:
            await canal.send(
                embed=embed_preto(
                    "❌ WHITELIST REPROVADA",
                    f"Você acertou **{acertos}/10**.\n\nÉ necessário acertar **8/10** para ser aprovado."
                )
            )

        await canal.send(
            embed=embed_preto(
                "🔒 FINALIZADO",
                "Esta whitelist foi finalizada. A equipe pode apagar este canal quando quiser."
            )
        )
        return

    q = QUESTOES[indice]

    class QuestaoView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)

        async def responder(self, interaction, escolha):
            if interaction.user.id != membro.id:
                await interaction.response.send_message(
                    "❌ Esta whitelist pertence a outro jogador.",
                    ephemeral=True
                )
                return

            novo_acerto = acertos + (1 if escolha == q["resposta"] else 0)

            if escolha == q["resposta"]:
                texto = "✅ Resposta correta!"
            else:
                texto = f"❌ Resposta incorreta. A resposta certa era **{q['resposta']}**."

            await interaction.response.edit_message(
                embed=embed_preto(
                    f"📝 PERGUNTA {indice + 1}/10",
                    f"{texto}\n\nCarregando a próxima pergunta..."
                ),
                view=None
            )

            await enviar_pergunta(canal, membro, indice + 1, novo_acerto)

        @discord.ui.button(label="A", style=discord.ButtonStyle.secondary)
        async def a(self, interaction, button):
            await self.responder(interaction, "A")

        @discord.ui.button(label="B", style=discord.ButtonStyle.secondary)
        async def b(self, interaction, button):
            await self.responder(interaction, "B")

        @discord.ui.button(label="C", style=discord.ButtonStyle.secondary)
        async def c(self, interaction, button):
            await self.responder(interaction, "C")

        @discord.ui.button(label="D", style=discord.ButtonStyle.secondary)
        async def d(self, interaction, button):
            await self.responder(interaction, "D")

    opcoes = "\n".join(
        f"**{letra})** {texto}" for letra, texto in q["opcoes"].items()
    )

    embed = embed_preto(
        f"📝 PERGUNTA {indice + 1}/10",
        f"**{q['pergunta']}**\n\n{opcoes}"
    )
    embed.set_footer(text=f"Acertos atuais: {acertos}")

    await canal.send(embed=embed, view=QuestaoView())


class SantaBot(commands.Bot):
    async def setup_hook(self):
        self.add_view(MetaView())
        self.add_view(AbrirWhitelistView())

        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()


bot = SantaBot(command_prefix=commands.when_mentioned, intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Santa Bot conectado como {bot.user}.")


# ============================================================
# ECONOMIA — TODOS OS COMANDOS SÃO SLASH (/)
# ============================================================

@bot.tree.command(name="saldo", description="Mostra o saldo da carteira e do banco.")
@app_commands.describe(membro="Jogador que deseja consultar (opcional).")
async def saldo(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    conta = obter_conta(membro.id)
    embed = embed_preto(
        "💰 SANTA BANK — SALDO",
        f"👤 **Conta:** {membro.mention}\n\n"
        f"💵 **Carteira:** {dinheiro(conta['cash'])}\n"
        f"🏦 **Banco:** {dinheiro(conta['bank'])}\n"
        f"💰 **Total:** {dinheiro(conta['cash'] + conta['bank'])}"
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="topmoney", description="Mostra os jogadores mais ricos.")
async def topmoney(interaction: discord.Interaction):
    if not economia:
        await interaction.response.send_message(embed=embed_preto("🏆 TOP MONEY", "Ainda não existem contas na economia."))
        return

    contas = []
    for user_id, conta in economia.items():
        try:
            total = int(conta.get("cash", 0)) + int(conta.get("bank", 0))
            contas.append((total, int(user_id)))
        except (TypeError, ValueError):
            continue

    contas.sort(reverse=True)
    linhas = []
    for posicao, (total, user_id) in enumerate(contas[:10], start=1):
        membro = interaction.guild.get_member(user_id) if interaction.guild else None
        nome = membro.display_name if membro else f"Usuário {user_id}"
        linhas.append(f"**{posicao}.** {nome} — **{dinheiro(total)}**")

    await interaction.response.send_message(
        embed=embed_preto("🏆 TOP MONEY — SANTA RP", "\n".join(linhas) if linhas else "Nenhuma conta encontrada.")
    )


@bot.tree.command(name="pagar", description="Transfere dinheiro da sua carteira para outro jogador.")
@app_commands.describe(jogador="Jogador que receberá o dinheiro.", valor="Valor a pagar.")
async def pagar(interaction: discord.Interaction, jogador: discord.Member, valor: app_commands.Range[int, 1, 1000000000]):
    if jogador.id == interaction.user.id:
        await interaction.response.send_message(embed=embed_preto("❌ PAGAMENTO", "Você não pode pagar a si mesmo."), ephemeral=True)
        return
    if jogador.bot:
        await interaction.response.send_message(embed=embed_preto("❌ PAGAMENTO", "Você não pode pagar um bot."), ephemeral=True)
        return

    pagador = obter_conta(interaction.user.id)
    recebedor = obter_conta(jogador.id)
    valor = int(valor)

    if pagador["cash"] < valor:
        await interaction.response.send_message(
            embed=embed_preto("❌ SALDO INSUFICIENTE", f"Você tem apenas **{dinheiro(pagador['cash'])}** na carteira."),
            ephemeral=True
        )
        return

    pagador["cash"] -= valor
    recebedor["cash"] += valor
    salvar_economia(economia)

    await interaction.response.send_message(
        embed=embed_preto(
            "💸 PAGAMENTO REALIZADO",
            f"👤 **Pagador:** {interaction.user.mention}\n"
            f"👤 **Recebedor:** {jogador.mention}\n"
            f"💵 **Valor:** {dinheiro(valor)}\n\n"
            "✅ Pagamento realizado com sucesso!"
        )
    )


@bot.tree.command(name="sacar", description="Saca dinheiro do banco para a carteira.")
@app_commands.describe(valor="Valor que deseja sacar.")
async def sacar(interaction: discord.Interaction, valor: app_commands.Range[int, 1, 1000000000]):
    valor = int(valor)
    conta = obter_conta(interaction.user.id)

    if conta["bank"] < valor:
        await interaction.response.send_message(
            embed=embed_preto("❌ SALDO BANCÁRIO INSUFICIENTE", f"Você possui **{dinheiro(conta['bank'])}** no banco."),
            ephemeral=True
        )
        return

    conta["bank"] -= valor
    conta["cash"] += valor
    salvar_economia(economia)

    await interaction.response.send_message(
        embed=embed_preto(
            "🏦 SAQUE REALIZADO",
            f"💵 Valor sacado: **{dinheiro(valor)}**\n"
            f"💵 Carteira: **{dinheiro(conta['cash'])}**\n"
            f"🏦 Banco: **{dinheiro(conta['bank'])}**"
        )
    )


@bot.tree.command(name="depositar", description="Deposita dinheiro da carteira no banco.")
@app_commands.describe(valor="Valor que deseja depositar.")
async def depositar(interaction: discord.Interaction, valor: app_commands.Range[int, 1, 1000000000]):
    valor = int(valor)
    conta = obter_conta(interaction.user.id)

    if conta["cash"] < valor:
        await interaction.response.send_message(
            embed=embed_preto("❌ DINHEIRO INSUFICIENTE", f"Você possui apenas **{dinheiro(conta['cash'])}** na carteira."),
            ephemeral=True
        )
        return

    conta["cash"] -= valor
    conta["bank"] += valor
    salvar_economia(economia)

    await interaction.response.send_message(
        embed=embed_preto(
            "🏦 DEPÓSITO REALIZADO",
            f"💵 Valor depositado: **{dinheiro(valor)}**\n"
            f"💵 Carteira: **{dinheiro(conta['cash'])}**\n"
            f"🏦 Banco: **{dinheiro(conta['bank'])}**"
        )
    )


# ============================================================
# SISTEMA DE ID — PRIMEIRO NOVO ID: 84
# ============================================================
ID_FILE = Path("santa_ids.json")
ID_INICIAL = 84

def carregar_ids():
    if not ID_FILE.exists():
        return {"proximo_id": ID_INICIAL, "usuarios": {}}
    try:
        with open(ID_FILE, "r", encoding="utf-8") as f:
            dados_ids = json.load(f)
        dados_ids.setdefault("proximo_id", ID_INICIAL)
        dados_ids.setdefault("usuarios", {})
        return dados_ids
    except (json.JSONDecodeError, OSError):
        return {"proximo_id": ID_INICIAL, "usuarios": {}}

def salvar_ids(ids):
    with open(ID_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)

ids = carregar_ids()

@bot.tree.command(name="id", description="Recebe seu ID da cidade.")
async def id_cmd(interaction: discord.Interaction):
    chave = str(interaction.user.id)
    usuarios = ids.setdefault("usuarios", {})

    if chave in usuarios:
        numero = int(usuarios[chave])
    else:
        numero = int(ids.get("proximo_id", ID_INICIAL))
        ids["proximo_id"] = numero + 1
        usuarios[chave] = numero
        salvar_ids(ids)

    nome = interaction.user.display_name.replace("@", "")
    apelido = f"{numero:02d} | {nome}"[:32]

    erro_nick = None
    try:
        if interaction.guild and interaction.guild.me and interaction.guild.me.guild_permissions.manage_nicknames:
            await interaction.user.edit(nick=apelido, reason="ID Santa RP")
        else:
            erro_nick = "O bot não possui a permissão Gerenciar Apelidos."
    except discord.Forbidden:
        erro_nick = "O bot não conseguiu alterar seu apelido. Coloque o cargo do bot acima do cargo do jogador."

    texto = (
        f"👤 **Jogador:** {interaction.user.mention}\n"
        f"🪪 **ID:** `{numero:02d}`\n\n"
        "✅ Seu ID foi registrado com sucesso!"
    )
    if erro_nick:
        texto += f"\n\n⚠️ **Aviso:** {erro_nick}"

    await interaction.response.send_message(embed=embed_preto("🪪 SANTA RP — ID", texto))


@bot.tree.command(name="metarp", description="Envia a votação para abrir o RP.")
@app_commands.checks.has_permissions(administrator=True)
async def metarp(interaction: discord.Interaction):
    dados["votos_sim"] = []
    dados["votos_nao"] = []
    salvar_dados(dados)

    embed = embed_preto(
        "🌆 META RP — CIDADE ON 🌆",
        """👮 Corporações: **ATIVAS**
🏥 Hospital: **ATIVO**
🚒 Bombeiros: **ATIVOS**
🏢 Empresas: **ABERTAS**
🗳️ Votos: **0 VOTOS**

━━━━━━━━━━━━━━━━━━━━

📢 **A cidade deve abrir o RP?**

━━━━━━━━━━━━━━━━━━━━"""
    )
    embed.set_footer(text="✅ 0 votos a favor • ❌ 0 votos contra")

    await interaction.response.send_message(embed=embed, view=MetaView())


@bot.tree.command(name="rpsanta", description="Envia o aviso de RP online.")
@app_commands.checks.has_permissions(administrator=True)
async def rpsanta(interaction: discord.Interaction):
    embed = embed_preto(
        "🟢 RP ON — CIDADE ONLINE",
        """👮 Corporações: **ATIVAS**
🏥 Hospital: **ATIVO**
🚒 Bombeiros: **ATIVOS**
🏢 Empresas: **ABERTAS**
🚕 Táxis: **ATIVOS**
⛽ Postos: **ABERTOS**

━━━━━━━━━━━━━━━━━━━━

📢 **ATENÇÃO, CIDADÃOS!**

O RP está oficialmente ON! Entrem em personagem, respeitem a imersão e aproveitem a cidade.

🔥 **BOM RP A TODOS!**"""
    )

    view = discord.ui.View()
    view.add_item(
        discord.ui.Button(
            label="ENTRAR NO RP",
            emoji="🎮",
            style=discord.ButtonStyle.success,
            url=ROBLOX_SERVER_LINK
        )
    )

    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.command(name="whitelist", description="Envia o painel para abrir a whitelist.")
@app_commands.checks.has_permissions(administrator=True)
async def whitelist(interaction: discord.Interaction):
    embed = embed_preto(
        "📋 SANTA RP — WHITELIST",
        """Clique no botão abaixo para iniciar sua whitelist.

📌 O bot criará um canal privado com seu número de whitelist.
📝 Serão 10 perguntas de GTA RP.
🎯 É necessário acertar **8/10** para passar.

Boa sorte!"""
    )

    await interaction.response.send_message(
        embed=embed,
        view=AbrirWhitelistView()
    )


# ============================================================
# APROVAÇÕES — PERSONAGEM, FACÇÃO, EMPRESA E CORPORAÇÃO
# ============================================================

async def adicionar_cargo_aprovacao(
    interaction: discord.Interaction,
    jogador: discord.Member,
    role_id: int,
    titulo: str,
    texto: str
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ Este comando só pode ser usado dentro do servidor.",
            ephemeral=True
        )
        return

    if not role_id or role_id <= 0:
        await interaction.response.send_message(
            "❌ O cargo desta aprovação ainda não foi configurado no bot.py. "
            "Preencha o ID do cargo correspondente.",
            ephemeral=True
        )
        return

    role = cargo(interaction.guild, role_id)
    if role is None:
        await interaction.response.send_message(
            f"❌ Não encontrei o cargo com ID `{role_id}` neste servidor.",
            ephemeral=True
        )
        return

    bot_member = interaction.guild.me or interaction.guild.get_member(bot.user.id)
    if bot_member is None or not bot_member.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ O bot precisa da permissão **Gerenciar Cargos**.",
            ephemeral=True
        )
        return

    if role.managed:
        await interaction.response.send_message(
            "❌ Esse cargo é gerenciado por uma integração e não pode ser atribuído pelo bot.",
            ephemeral=True
        )
        return

    if bot_member.top_role <= role:
        await interaction.response.send_message(
            f"❌ Não consigo adicionar **{role.name}**. "
            "Coloque o cargo do bot **acima** desse cargo na hierarquia do servidor.",
            ephemeral=True
        )
        return

    try:
        await jogador.add_roles(
            role,
            reason=f"{titulo} por {interaction.user}"
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ O Discord recusou a alteração do cargo. Verifique a hierarquia e a permissão Gerenciar Cargos.",
            ephemeral=True
        )
        return
    except discord.HTTPException as erro:
        print(f"Erro ao adicionar cargo {role.id}: {erro!r}")
        await interaction.response.send_message(
            "❌ O Discord retornou um erro ao adicionar o cargo. Veja o console do bot para mais detalhes.",
            ephemeral=True
        )
        return

    embed = embed_preto(
        titulo,
        f"👤 **Jogador:** {jogador.mention}\n\n"
        f"{texto}\n"
        f"👮 **Aprovado por:** {interaction.user.mention}"
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="aprovarpersonagem",
    description="Aprova o personagem de um jogador."
)
@app_commands.describe(jogador="Jogador que terá o personagem aprovado.")
@app_commands.checks.has_permissions(administrator=True)
async def aprovarpersonagem(interaction: discord.Interaction, jogador: discord.Member):
    await adicionar_cargo_aprovacao(
        interaction, jogador, CARGO_PERSONAGEM_APROVADA_ID,
        "✅ PERSONAGEM APROVADO",
        "🎭 O personagem foi aprovado com sucesso."
    )


@bot.tree.command(
    name="aprovarfaccao",
    description="Aprova a facção de um jogador."
)
@app_commands.describe(jogador="Jogador que terá a facção aprovada.")
@app_commands.checks.has_permissions(administrator=True)
async def aprovarfaccao(interaction: discord.Interaction, jogador: discord.Member):
    await adicionar_cargo_aprovacao(
        interaction, jogador, CARGO_FACCAO_APROVADA_ID,
        "✅ FACÇÃO APROVADA",
        "⚔️ A facção foi aprovada com sucesso."
    )


@bot.tree.command(
    name="aprovarempresa",
    description="Aprova a empresa de um jogador."
)
@app_commands.describe(jogador="Jogador que terá a empresa aprovada.")
@app_commands.checks.has_permissions(administrator=True)
async def aprovarempresa(interaction: discord.Interaction, jogador: discord.Member):
    await adicionar_cargo_aprovacao(
        interaction, jogador, CARGO_EMPRESA_APROVADA_ID,
        "✅ EMPRESA APROVADA",
        "🏢 A empresa foi aprovada com sucesso."
    )


@bot.tree.command(
    name="aprovarcorporacao",
    description="Aprova a corporação de um jogador."
)
@app_commands.describe(jogador="Jogador que terá a corporação aprovada.")
@app_commands.checks.has_permissions(administrator=True)
async def aprovarcorporacao(interaction: discord.Interaction, jogador: discord.Member):
    await adicionar_cargo_aprovacao(
        interaction, jogador, CARGO_CORPORACAO_APROVADA_ID,
        "✅ CORPORAÇÃO APROVADA",
        "👮 A corporação foi aprovada com sucesso."
    )


# ============================================================
# APROVAR SALÁRIO — ENVIA O VALOR PARA O BANCO DO JOGADOR
# ============================================================

@bot.tree.command(
    name="aprovarsalario",
    description="Aprova e paga um salário para um jogador."
)
@app_commands.describe(
    jogador="Jogador que receberá o salário.",
    valor="Valor do salário em reais."
)
@app_commands.checks.has_permissions(administrator=True)
async def aprovarsalario(
    interaction: discord.Interaction,
    jogador: discord.Member,
    valor: app_commands.Range[int, 1, 1000000000]
):
    conta = obter_conta(jogador.id)
    conta["bank"] += int(valor)
    salvar_economia(economia)

    embed = embed_preto(
        "💰 SALÁRIO APROVADO",
        f"""👤 **Funcionário:** {jogador.mention}
💵 **Valor enviado:** {dinheiro(int(valor))}
🏦 **Novo saldo bancário:** {dinheiro(conta["bank"])}

✅ O salário foi aprovado e enviado para a conta do jogador.
👮 **Aprovado por:** {interaction.user.mention}"""
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.error
async def erro_comando(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        mensagem = "❌ Você precisa ser administrador para usar este comando."
    else:
        print(f"Erro: {repr(error)}")
        mensagem = "❌ Ocorreu um erro ao executar o comando."

    if interaction.response.is_done():
        await interaction.followup.send(mensagem, ephemeral=True)
    else:
        await interaction.response.send_message(mensagem, ephemeral=True)


bot.run(TOKEN)
