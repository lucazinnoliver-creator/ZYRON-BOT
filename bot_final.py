import discord
import datetime
import json
import os
import asyncio
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

os.makedirs("data", exist_ok=True)

FILAS_TIPOS = [
    ("mobile_1x1", "Mobile (1v1)", "📱"),
    ("mobile_2x2", "Mobile (2v2)", "📱"),
    ("mobile_3x3", "Mobile (3x3)", "📱"),
    ("mobile_4x4", "Mobile (4x4)", "📱"),
    ("emulador_1x1", "Emulador (1v1)", "🖥️"),
    ("emulador_2x2", "Emulador (2v2)", "🖥️"),
    ("emulador_3x3", "Emulador (3x3)", "🖥️"),
    ("emulador_4x4", "Emulador (4x4)", "🖥️"),
    ("misto_1x1", "Misto (1v1)", "🔀"),
    ("misto_2x2", "Misto (2v2)", "🔀"),
    ("misto_3x3", "Misto (3x3)", "🔀"),
    ("misto_4x4", "Misto (4x4)", "🔀"),
    ("tatico_1x1", "Tático (1v1)", "🚩"),
    ("tatico_2x2", "Tático (2v2)", "🚩"),
    ("tatico_3x3", "Tático (3x3)", "🚩"),
    ("tatico_4x4", "Tático (4x4)", "🚩"),
]

def formatar_valor_br(v):
    try:
        num = float(str(v).replace(",","."))
        return f"{num:.2f}".replace(".", ",")
    except:
        return str(v)

def parse_valores_input(texto):
    valores = []
    partes = texto.split(",")
    for p in partes:
        p = p.strip()
        if not p:
            continue
        try:
            num = float(p.replace(",", "."))
            if num>0:
                valores.append(num)
        except:
            continue
    return valores

def get_categoria_from_key(tipo_key):
    if tipo_key.startswith("mobile"):
        return "mobile"
    if tipo_key.startswith("emulador"):
        return "emulador"
    if tipo_key.startswith("misto"):
        return "misto"
    if tipo_key.startswith("tatico"):
        return "tatico"
    return "mobile"

def get_tamanho_x(tipo_key):
    try:
        return tipo_key.split("_")[1]
    except:
        return "1x1"

def get_tamanho_v(tipo_key):
    return get_tamanho_x(tipo_key).replace("x","v")

def get_categoria_cap(tipo_key):
    mapa = {"mobile": "Mobile", "emulador": "Emulador", "misto": "Misto", "tatico": "Tático"}
    return mapa.get(get_categoria_from_key(tipo_key), "Mobile")

def get_botoes_por_fila(tipo_key):
    if tipo_key in ["mobile_1x1", "emulador_1x1", "misto_1x1"]:
        return ["gelo_normal", "gelo_infinito", "sair"]
    if tipo_key in ["mobile_2x2", "mobile_3x3", "mobile_4x4", "emulador_2x2", "emulador_3x3", "emulador_4x4"]:
        return ["normal", "full_ump_xm8", "sair"]
    if tipo_key == "misto_2x2":
        return ["1_emu", "sair"]
    if tipo_key == "misto_3x3":
        return ["1_emu", "2_emu", "sair"]
    if tipo_key == "misto_4x4":
        return ["1_emu", "2_emu", "3_emu", "sair"]
    if tipo_key == "tatico_1x1":
        return ["mobile", "emulador", "sair"]
    if tipo_key in ["tatico_2x2", "tatico_3x3", "tatico_4x4"]:
        return ["mobile", "emulador", "misto", "sair"]
    return ["sair"]

def get_config(gid):
    p = f"data/{gid}.json"
    if os.path.exists(p):
        with open(p, "r") as f:
            data = json.load(f)
            if not isinstance(data.get("embed_emojis"), dict):
                data["embed_emojis"] = {"modo": "👑", "valor": "💰", "jogadores": "🔥"}
            if "thumbnails" not in data:
                data["thumbnails"] = {"mobile": None, "emulador": None, "misto": None, "tatico": None}
            if "banners" not in data:
                data["banners"] = {"mobile": None, "emulador": None, "misto": None, "tatico": None}
            if "footer" not in data:
                data["footer"] = {"text": None, "icon": None}
            if "embed_titulo" not in data:
                data["embed_titulo"] = None
            if "botoes_emojis" not in data or not isinstance(data.get("botoes_emojis"), dict):
                data["botoes_emojis"] = {}
            if "botoes_textos" not in data or not isinstance(data.get("botoes_textos"), dict):
                data["botoes_textos"] = {}
            if "botoes_cores" not in data or not isinstance(data.get("botoes_cores"), dict):
                data["botoes_cores"] = {}
            if "footers" in data:
                del data["footers"]
            if "taxa_org" not in data:
                data["taxa_org"] = "0,10"
            if "categoria_apostas" not in data:
                data["categoria_apostas"] = None
            if "canal_analistas" not in data:
                data["canal_analistas"] = None
            if "canais_filas" not in data or not isinstance(data.get("canais_filas"), dict):
                data["canais_filas"] = {}
            return data
    return {
        "categoria_apostas": None,
        "canal_analistas": None,
        "valores_filas": [],
        "canais_filas": {},
        "logs": {"log-filas": None, "log-black": None, "log-ticket": None, "log-iniciadas": None, "log-confirmadas": None, "log-recusada": None, "log-criadas": None, "logs-finalizadas": None},
        "taxa_org": "0,10",
        "cor_org": "#1E90FF",
        "vitorias": 1,
        "coins": 1,
        "embed_emojis": {"modo": "👑", "valor": "💰", "jogadores": "🔥"},
        "embed_titulo": None,
        "thumbnails": {"mobile": None, "emulador": None, "misto": None, "tatico": None},
        "banners": {"mobile": None, "emulador": None, "misto": None, "tatico": None},
        "footer": {"text": None, "icon": None},
        "botoes_emojis": {},
        "botoes_textos": {},
        "botoes_cores": {},
        "permissoes": {"permissao_maxima": [], "cargo_mediador_adm": [], "ver_apostas": [], "gerenciar_filas": [], "ss_mobile": [], "ss_emu": []}
    }

def save(gid, c):
    with open(f"data/{gid}.json", "w") as f:
        json.dump(c, f, indent=4)

def tem_perm_max(m, c):
    if not c["permissoes"]["permissao_maxima"]:
        return True
    return any(r.id in c["permissoes"]["permissao_maxima"] for r in m.roles)

def check_max():
    async def pred(i):
        return tem_perm_max(i.user, get_config(i.guild.id))
    return app_commands.check(pred)

def fmt(l):
    return ", ".join([f"<@&{x}>" for x in l]) if l else "Não configurado ainda"

def fmt_embed(l):
    return f"<@&{l[0]}>" if l else "não configurado"

def get_cor_embed(c):
    try:
        return int(c.get("cor_org", "#1E90FF").replace("#",""),16)
    except:
        return 0x2B2D31

BOTOES_INFO = {
    "gelo_normal": {"label": "Gel Normal", "default": None},
    "gelo_infinito": {"label": "Gel Infinito", "default": None},
    "sair": {"label": "Sair da fila", "default": None},
    "normal": {"label": "Normal", "default": None},
    "full_ump_xm8": {"label": "FULL UMP E XM8", "default": None},
    "1_emu": {"label": "1 Emu", "default": None},
    "2_emu": {"label": "2 Emu", "default": None},
    "3_emu": {"label": "3 Emu", "default": None},
    "confirmar": {"label": "Confirmar", "default": None},
    "recusar": {"label": "Recusar", "default": None},
    "misto": {"label": "Misto", "default": None},
    "mobile": {"label": "Mobile", "default": None},
    "emulador": {"label": "Emulador", "default": None},
}
BOTOES_LISTA_UNICA = ["gelo_normal", "gelo_infinito", "sair", "normal", "full_ump_xm8", "1_emu", "2_emu", "3_emu", "confirmar", "recusar", "misto", "mobile", "emulador"]

def embed_config(c, guild=None):
    cor = get_cor_embed(c)
    e = discord.Embed(title="BOT CONFIG", description="Configure cargos, canais, logs e etc usando o bot config", color=cor)
    if guild:
        cat_id = c.get('categoria_apostas')
        cat_obj = guild.get_channel(cat_id) if cat_id else None
        cat_txt = f"**{cat_obj.name}**" if cat_obj else "não configurada"
        canal_id = c.get('canal_analistas')
        canal_obj = guild.get_channel(canal_id) if canal_id else None
        canal_txt = canal_obj.mention if canal_obj else "não configurado"
    else:
        cat_id = c.get('categoria_apostas')
        canal_id = c.get('canal_analistas')
        cat_txt = f"<#{cat_id}>" if cat_id else "não configurada"
        canal_txt = f"<#{canal_id}>" if canal_id else "não configurado"
    vals = sorted(c.get("valores_filas", []), reverse=True)
    if vals:
        valores_txt = ", ".join([formatar_valor_br(v) for v in vals])
    else:
        valores_txt = "Nenhum valor cadastrado ainda"
    med = fmt_embed(c["permissoes"]["cargo_mediador_adm"])
    ver = fmt_embed(c["permissoes"]["ver_apostas"])
    t1 = f"🎰 • **Categoria das apostas:** {cat_txt}\n👑 • **Cargo de mediador:** {med}\n👁️ • **Cargo para ver as filas:** {ver}\n🧠 • **Canal analistas:** {canal_txt}\n💰 • **Valores das filas:** {valores_txt}"
    lg = c["logs"]
    t2 = f"📁 • **Canais logs:**\n📄 • **log-filas:** {lg['log-filas'] or 'não configurado'}\n🔒 • **log-black:** {lg['log-black'] or 'não configurado'}\n🎫 • **log-ticket:** {lg['log-ticket'] or 'não configurado'}\n🌐 • **log-iniciadas:** {lg['log-iniciadas'] or 'não configurado'}\n✅ • **log-confirmadas:** {lg['log-confirmadas'] or 'não configurado'}\n❌ • **log-recusada:** {lg['log-recusada'] or 'não configurado'}\n🔥 • **log-criadas:** {lg['log-criadas'] or 'não configurado'}\n🏁 • **logs-finalizadas:** {lg['logs-finalizadas'] or 'não configurado'}"
    t3 = f"💸 • **Taxa da org:** {c['taxa_org']}\n🚩 • **Cor da org:** {c['cor_org']}\n🔥 • **Vitórias e coins:**\nVitorias: {c['vitorias']}\nCoins: {c['coins']}"
    e.add_field(name="", value=t1, inline=False)
    e.add_field(name="", value=t2, inline=False)
    e.add_field(name="", value=t3, inline=False)
    e.set_footer(text=f"Configuração • Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e

def embed_lista(c):
    p = c["permissoes"]
    e = discord.Embed(title="🔒 Gerenciamento de Permissões", color=get_cor_embed(c))
    e.description = f"**Permissão máxima**\n{fmt(p['permissao_maxima'])}\n\n**Cargo Mediador/ADM**\n{fmt(p['cargo_mediador_adm'])}\n\n**Ver apostas**\n{fmt(p['ver_apostas'])}\n\n**Gerenciar filas**\n{fmt(p['gerenciar_filas'])}\n\n**SS Mobile**\n{fmt(p['ss_mobile'])}\n\n**SS Emu**\n{fmt(p['ss_emu'])}"
    return e

def embed_generico(c, titulo, desc, lista):
    return discord.Embed(title=titulo, description=f"{desc}\n\n**Roles/Cargos com esta permissão:**\n{fmt(lista)}", color=get_cor_embed(c))

def embed_filas(c):
    e = discord.Embed(title="⚙️ CONFIGURAÇÕES AVANÇADAS", description="Personalize as configurações avançadas do sistema de filas\n\n**Selecione uma opção abaixo para configurar:**", color=get_cor_embed(c))
    e.set_footer(text=f"Configurações Avançadas • Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e

def embed_setar_filas(c, guild=None, bot_avatar_url=None):
    cor = get_cor_embed(c)
    e = discord.Embed(title="Setar filas de apostas", color=cor)
    canais = c.get("canais_filas", {})
    def get_canal_txt(key):
        cid = canais.get(key)
        if not cid:
            return "Nenhum"
        if guild:
            ch = guild.get_channel(cid)
            return ch.mention if ch else f"<#{cid}>"
        return f"<#{cid}>"
    desc = ""
    desc += "**Filas Mobile:**\n"
    desc += f"Mobile 1x1: {get_canal_txt('mobile_1x1')}\n"
    desc += f"Mobile 2x2: {get_canal_txt('mobile_2x2')}\n"
    desc += f"Mobile 3x3: {get_canal_txt('mobile_3x3')}\n"
    desc += f"Mobile 4x4: {get_canal_txt('mobile_4x4')}\n\n"
    desc += "**Filas Emulador:**\n"
    desc += f"Emulador 1x1: {get_canal_txt('emulador_1x1')}\n"
    desc += f"Emulador 2x2: {get_canal_txt('emulador_2x2')}\n"
    desc += f"Emulador 3x3: {get_canal_txt('emulador_3x3')}\n"
    desc += f"Emulador 4x4: {get_canal_txt('emulador_4x4')}\n\n"
    desc += "**Filas Misto:**\n"
    desc += f"Misto 1x1: {get_canal_txt('misto_1x1')}\n"
    desc += f"Misto 2x2: {get_canal_txt('misto_2x2')}\n"
    desc += f"Misto 3x3: {get_canal_txt('misto_3x3')}\n"
    desc += f"Misto 4x4: {get_canal_txt('misto_4x4')}\n\n"
    desc += "**Filas Tático:**\n"
    desc += f"Tatico 1x1: {get_canal_txt('tatico_1x1')}\n"
    desc += f"Tatico 2x2: {get_canal_txt('tatico_2x2')}\n"
    desc += f"Tatico 3x3: {get_canal_txt('tatico_3x3')}\n"
    desc += f"Tatico 4x4: {get_canal_txt('tatico_4x4')}"
    e.description = desc
    if bot_avatar_url:
        e.set_thumbnail(url=bot_avatar_url)
    return e

def embed_selecionar_canal_fila(c, tipo_label):
    e = discord.Embed(color=get_cor_embed(c))
    e.title = f"Setar {tipo_label}"
    e.description = f"Selecione abaixo o canal onde as filas de **{tipo_label}** serão enviadas.\n\nUse a barra de pesquisa do Discord para achar o canal."
    e.set_footer(text=f"Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e

def criar_embed_fila(c, tipo_key, valor, jogadores_lista=None):
    cor = get_cor_embed(c)
    em = c.get("embed_emojis", {"modo": "👑", "valor": "💰", "jogadores": "🔥"})
    if not isinstance(em, dict):
        em = {"modo": "👑", "valor": "💰", "jogadores": "🔥"}
    titulo_custom = c.get("embed_titulo")
    tam_x = get_tamanho_x(tipo_key)
    tam_v = get_tamanho_v(tipo_key)
    cat_cap = get_categoria_cap(tipo_key)
    cat_key = get_categoria_from_key(tipo_key)
    if titulo_custom:
        titulo = f"{tam_v} | {titulo_custom}"
    else:
        titulo = f"Filas | {cat_cap}"
    e = discord.Embed(title=titulo, color=cor)
    if not jogadores_lista:
        jogadores_txt = "*Nenhum jogador na fila*"
    else:
        linhas = []
        for j in jogadores_lista:
            linhas.append(f"<@{j['id']}> | {j['label']}")
        jogadores_txt = "
".join(linhas)
    e.description = (
        f"# {em.get('modo','👑')}  Formato
"
        f"**{tam_x} {cat_cap}**

"
        f"# {em.get('valor','💰')}  Valor
"
        f"**R$ {formatar_valor_br(valor)}**

"
        f"## {em.get('jogadores','🎯')}  Jogadores
"
        f"{jogadores_txt}"
    )
    thumbs = c.get("thumbnails", {})
    banners = c.get("banners", {})
    footer = c.get("footer", {"text": None, "icon": None})
    thumb_url = thumbs.get(cat_key)
    banner_url = banners.get(cat_key)
    if thumb_url:
        e.set_thumbnail(url=thumb_url)
    if banner_url:
        e.set_image(url=banner_url)
    if footer.get("text") or footer.get("icon"):
        e.set_footer(text=footer.get("text") or " ", icon_url=footer.get("icon") if footer.get("icon") else None)
    else:
        e.set_footer(text=f"Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e


# ===== MEMÓRIA DAS FILAS ATIVAS =====
FILAS_ATIVAS = {}

class FilaView(discord.ui.View):
    def __init__(self, config, gid, tipo_key, valor=None):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.tipo_key = tipo_key
        # compatibilidade: se valor nao vier, tenta pegar do FILAS_ATIVAS ou usa 3.0
        self.valor = valor if valor is not None else 3.0
        botoes_keys = get_botoes_por_fila(tipo_key)
        b_emojis = config.get("botoes_emojis", {})
        b_textos = config.get("botoes_textos", {})
        b_cores = config.get("botoes_cores", {})
        for key in botoes_keys:
            info = BOTOES_INFO.get(key)
            if not info:
                continue
            label = b_textos.get(key) or info["label"]
            emoji = b_emojis.get(key)
            cor_nome = b_cores.get(key, "secondary")
            if key == "sair":
                cor_nome = "danger"
            style_map = {
                "primary": discord.ButtonStyle.primary,
                "secondary": discord.ButtonStyle.secondary,
                "success": discord.ButtonStyle.success,
                "danger": discord.ButtonStyle.danger
            }
            style = style_map.get(cor_nome, discord.ButtonStyle.secondary)
            btn = discord.ui.Button(label=label, emoji=emoji if emoji else None, style=style, custom_id=f"fila_{tipo_key}_{key}_{self.valor}")
            async def make_callback(inter, k=key, lbl=label):
                await self.handle_fila(inter, k, lbl)
            btn.callback = make_callback
            self.add_item(btn)

    async def handle_fila(self, inter: discord.Interaction, modo_key: str, label: str):
        await inter.response.defer(ephemeral=True)
        msg_id = inter.message.id
        user_id = inter.user.id
        if msg_id not in FILAS_ATIVAS:
            FILAS_ATIVAS[msg_id] = {"tipo_key": self.tipo_key, "valor": self.valor, "jogadores": []}
        fila = FILAS_ATIVAS[msg_id]
        if modo_key == "sair":
            antes = len(fila["jogadores"])
            fila["jogadores"] = [j for j in fila["jogadores"] if j["id"] != user_id]
            if len(fila["jogadores"]) == antes:
                await inter.followup.send("❌ Você não está na fila!", ephemeral=True)
                return
            novo_embed = criar_embed_fila(self.config, self.tipo_key, self.valor, fila["jogadores"])
            try:
                await inter.message.edit(embed=novo_embed, view=self)
            except:
                pass
            await inter.followup.send("✅ Você saiu da fila!", ephemeral=True)
            return
        for j in fila["jogadores"]:
            if j["id"] == user_id:
                if j["modo"] == modo_key:
                    await inter.followup.send(f"⚠️ Você já está na fila como **{j['label']}**", ephemeral=True)
                    return
                else:
                    j["modo"] = modo_key
                    j["label"] = label
                    novo_embed = criar_embed_fila(self.config, self.tipo_key, self.valor, fila["jogadores"])
                    try:
                        await inter.message.edit(embed=novo_embed, view=self)
                    except:
                        pass
                    await inter.followup.send(f"🔄 Você trocou para **{label}**", ephemeral=True)
                    await self.checar_match(inter, fila, modo_key, label)
                    return
        fila["jogadores"].append({"id": user_id, "modo": modo_key, "label": label})
        match_encontrado = await self.checar_match(inter, fila, modo_key, label)
        if not match_encontrado:
            novo_embed = criar_embed_fila(self.config, self.tipo_key, self.valor, fila["jogadores"])
            try:
                await inter.message.edit(embed=novo_embed, view=self)
            except:
                pass
            await inter.followup.send(f"✅ Você entrou na fila: **{label}**", ephemeral=True)

    async def checar_match(self, inter: discord.Interaction, fila, modo_key, label):
        jogadores_mesmo_modo = [j for j in fila["jogadores"] if j["modo"] == modo_key]
        if len(jogadores_mesmo_modo) >= 2:
            p1 = jogadores_mesmo_modo[0]
            p2 = jogadores_mesmo_modo[1]
            fila["jogadores"] = [j for j in fila["jogadores"] if j["id"] not in [p1["id"], p2["id"]]]
            novo_embed = criar_embed_fila(self.config, self.tipo_key, self.valor, fila["jogadores"])
            try:
                await inter.message.edit(embed=novo_embed, view=self)
            except:
                pass
            await self.criar_topico_aposta(inter, p1, p2, modo_key, label)
            return True
        return False

    async def criar_topico_aposta(self, inter: discord.Interaction, p1, p2, modo_key, label):
        guild = inter.guild
        c = get_config(guild.id)
        categoria_id = c.get("categoria_apostas")
        canal_alvo = None
        if categoria_id:
            categoria = guild.get_channel(categoria_id)
            if categoria and isinstance(categoria, discord.CategoryChannel):
                for ch in categoria.channels:
                    if isinstance(ch, discord.TextChannel):
                        canal_alvo = ch
                        break
        if not canal_alvo:
            canal_alvo = inter.channel
        try:
            tam_v = get_tamanho_v(self.tipo_key)
            valor_fmt = formatar_valor_br(self.valor)
            thread_name = f"{tam_v} | R$ {valor_fmt} | {label}"
            thread = None
            if isinstance(canal_alvo, discord.TextChannel):
                thread = await canal_alvo.create_thread(
                    name=thread_name,
                    type=discord.ChannelType.private_thread,
                    auto_archive_duration=60,
                    reason=f"Aposta criada: {p1['id']} vs {p2['id']} - {label}"
                )
            else:
                thread = await inter.channel.create_thread(
                    name=thread_name,
                    type=discord.ChannelType.private_thread,
                    auto_archive_duration=60
                )
            if thread:
                embed_aposta = discord.Embed(
                    title=f"✅ Aposta Encontrada!",
                    description=f"**{tam_v} | R$ {valor_fmt}**

**Jogadores:**
<@{p1['id']}> vs <@{p2['id']}>

**Modo:** {label}
**Valor:** R$ {valor_fmt}",
                    color=0x00FF00
                )
                try:
                    await thread.add_user(guild.get_member(p1['id']) or await guild.fetch_member(p1['id']))
                except:
                    pass
                try:
                    await thread.add_user(guild.get_member(p2['id']) or await guild.fetch_member(p2['id']))
                except:
                    pass
                await thread.send(content=f"<@{p1['id']}> <@{p2['id']}>", embed=embed_aposta)
                try:
                    await inter.followup.send(f"🎮 Partida encontrada! {thread.mention} - <@{p1['id']}> vs <@{p2['id']}> ({label})", ephemeral=False)
                except:
                    await inter.channel.send(f"🎮 Partida encontrada! {thread.mention} - <@{p1['id']}> vs <@{p2['id']}> ({label})")
        except Exception as e:
            print(f"Erro ao criar tópico: {e}")
            try:
                await inter.channel.send(f"🎮 **MATCH!** <@{p1['id']}> vs <@{p2['id']}> - **{label}** - R$ {formatar_valor_br(self.valor)}")
            except:
                pass



def embed_visual(c, tipo_preview=None):
    cor = get_cor_embed(c)
    em = c.get("embed_emojis", {"modo": "👑", "valor": "💰", "jogadores": "🔥"})
    if not isinstance(em, dict):
        em = {"modo": "👑", "valor": "💰", "jogadores": "🔥"}
    titulo_custom = c.get("embed_titulo")
    titulo = f"1v1 | {titulo_custom}" if titulo_custom else "Filas Padrão"
    e = discord.Embed(title=titulo, color=cor)
    e.description = f"{em.get('modo','👑')} **Modo**\n1x1 Padrão\n\n{em.get('valor','💰')} **Valor**\nR$ 1,00\n\n{em.get('jogadores','🔥')} **Jogadores**\nNenhum jogador na fila"
    thumbs = c.get("thumbnails", {})
    banners = c.get("banners", {})
    footer = c.get("footer", {"text": None, "icon": None})
    thumb_url = thumbs.get(tipo_preview) if tipo_preview else None
    banner_url = banners.get(tipo_preview) if tipo_preview else None
    if not thumb_url:
        for t in ["misto", "mobile", "emulador", "tatico"]:
            if thumbs.get(t):
                thumb_url = thumbs[t]
                break
    if not banner_url:
        for t in ["misto", "mobile", "emulador", "tatico"]:
            if banners.get(t):
                banner_url = banners[t]
                break
    if thumb_url:
        e.set_thumbnail(url=thumb_url)
    if banner_url:
        e.set_image(url=banner_url)
    if footer.get("text") or footer.get("icon"):
        e.set_footer(text=footer.get("text") or " ", icon_url=footer.get("icon") if footer.get("icon") else None)
    return e

def embed_botoes_lista(c):
    b = c.get("botoes_emojis", {})
    t = c.get("botoes_textos", {})
    cores = c.get("botoes_cores", {})
    if not isinstance(b, dict):
        b = {}
    if not isinstance(t, dict):
        t = {}
    if not isinstance(cores, dict):
        cores = {}
    def get(k):
        return b.get(k) or ""
    def get_txt(k):
        return t.get(k) or BOTOES_INFO.get(k, {"label": k})["label"]
    def get_cor(k):
        mapa = {"primary": "Primary (Azul)", "secondary": "Secondary (Cinza)", "success": "Success (Verde)", "danger": "Danger (Vermelho)"}
        return mapa.get(cores.get(k, "secondary"), "Secondary (Cinza)")
    desc = (
        f"GELD\n\n"
        f"{get('gelo_normal')} {get_txt('gelo_normal')} | Cor: {get_cor('gelo_normal')}\n"
        f"{get('gelo_infinito')} {get_txt('gelo_infinito')} | Cor: {get_cor('gelo_infinito')}\n"
        f"{get('sair')} {get_txt('sair')} | Cor: {get_cor('sair')}\n\n"
        f"MOBILE E EMULADOR\n\n"
        f"{get('normal')} {get_txt('normal')} | Cor: {get_cor('normal')}\n"
        f"{get('full_ump_xm8')} {get_txt('full_ump_xm8')} | Cor: {get_cor('full_ump_xm8')}\n"
        f"{get('sair')} {get_txt('sair')} | Cor: {get_cor('sair')}\n\n"
        f"MISTOS\n\n"
        f"{get('1_emu')} {get_txt('1_emu')} | Cor: {get_cor('1_emu')}\n"
        f"{get('2_emu')} {get_txt('2_emu')} | Cor: {get_cor('2_emu')}\n"
        f"{get('3_emu')} {get_txt('3_emu')} | Cor: {get_cor('3_emu')}\n"
        f"{get('sair')} {get_txt('sair')} | Cor: {get_cor('sair')}\n\n"
        f"TÁTICO E FULL\n\n"
        f"{get('misto')} {get_txt('misto')} | Cor: {get_cor('misto')}\n"
        f"{get('mobile')} {get_txt('mobile')} | Cor: {get_cor('mobile')}\n"
        f"{get('emulador')} {get_txt('emulador')} | Cor: {get_cor('emulador')}\n"
        f"{get('sair')} {get_txt('sair')} | Cor: {get_cor('sair')}\n\n"
        f"CONFIRMAR E CANCELAR PARTIDA\n\n"
        f"{get('confirmar')} {get_txt('confirmar')} | Cor: {get_cor('confirmar')}\n"
        f"{get('recusar')} {get_txt('recusar')} | Cor: {get_cor('recusar')}"
    )
    e = discord.Embed(description=desc, color=get_cor_embed(c))
    return e

class CorModal(discord.ui.Modal, title="Digite a cor"):
    cor_input = discord.ui.TextInput(label="Digite a cor:", placeholder="Ex: #000080", max_length=7)
    def __init__(self, config, gid):
        super().__init__()
        self.config = config
        self.gid = gid
    async def on_submit(self, i):
        txt = str(self.cor_input.value).strip()
        if not txt.startswith("#"):
            txt = "#" + txt
        try:
            int(txt.replace("#", ""), 16)
            self.config["cor_org"] = txt.upper()
            save(self.gid, self.config)
            await i.response.edit_message(embed=embed_visual(self.config), view=CorView(self.config, self.gid))
        except:
            await i.response.send_message("Cor inválida! Use formato #000080", ephemeral=True)

class TituloModal(discord.ui.Modal, title="Alterar Título"):
    titulo_input = discord.ui.TextInput(label="Digite o título", placeholder="Digite 'padrao' para remover o título", required=True, max_length=50)
    def __init__(self, config, gid):
        super().__init__()
        self.config = config
        self.gid = gid
    async def on_submit(self, i):
        texto = str(self.titulo_input.value).strip()
        if texto.lower() == "padrao":
            self.config["embed_titulo"] = None
        else:
            self.config["embed_titulo"] = texto.upper()
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_visual(self.config), view=AlterarEmbedView(self.config, self.gid))

class ThumbnailModal(discord.ui.Modal):
    url_input = discord.ui.TextInput(label="Digite o URL da imagem:", placeholder="digite 'remover' para remover a thumbnail", max_length=500)
    def __init__(self, config, gid, tipo):
        super().__init__(title=f"Thumbnail - {tipo.upper()}")
        self.config = config
        self.gid = gid
        self.tipo = tipo
    async def on_submit(self, i):
        texto = str(self.url_input.value).strip()
        if texto.lower() == "remover":
            self.config["thumbnails"][self.tipo] = None
        else:
            self.config["thumbnails"][self.tipo] = texto
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_visual(self.config, self.tipo), view=ThumbnailView(self.config, self.gid))

class BannerModal(discord.ui.Modal):
    url_input = discord.ui.TextInput(label="Digite o URL da imagem:", placeholder="digite 'remover' para remover o banner", max_length=500)
    def __init__(self, config, gid, tipo):
        super().__init__(title=f"Banner - {tipo.upper()}")
        self.config = config
        self.gid = gid
        self.tipo = tipo
    async def on_submit(self, i):
        texto = str(self.url_input.value).strip()
        if texto.lower() == "remover":
            self.config["banners"][self.tipo] = None
        else:
            self.config["banners"][self.tipo] = texto
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_visual(self.config, self.tipo), view=BannerView(self.config, self.gid))

class FooterModal(discord.ui.Modal, title="Alterar Rodapé"):
    rodape_input = discord.ui.TextInput(label="Digite o rodapé", placeholder="Digite 'remover' para deixar sem rodapé", max_length=200, required=False)
    emoji_input = discord.ui.TextInput(label="Link do emoji", placeholder="Digite 'remover' para remover a imagem do rodapé", max_length=500, required=False)
    def __init__(self, config, gid):
        super().__init__(title="Alterar Rodapé")
        self.config = config
        self.gid = gid
        ft = self.config.get("footer", {})
        if ft.get("text"):
            self.rodape_input.default = ft.get("text")
        if ft.get("icon"):
            self.emoji_input.default = ft.get("icon")
    async def on_submit(self, i):
        txt = str(self.rodape_input.value).strip()
        icon = str(self.emoji_input.value).strip()
        if txt.lower() == "remover":
            self.config["footer"]["text"] = None
        elif txt!= "":
            self.config["footer"]["text"] = txt
        if icon.lower() == "remover":
            self.config["footer"]["icon"] = None
        elif icon!= "":
            self.config["footer"]["icon"] = icon
        if txt.lower() == "remover" and icon.lower() == "remover":
            self.config["footer"] = {"text": None, "icon": None}
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_visual(self.config), view=AlterarEmbedView(self.config, self.gid))

def embed_cor_botao(c, nome_botao):
    e = discord.Embed(color=get_cor_embed(c))
    e.description = f"🍪 Selecione a cor para: **{nome_botao}**\n\n**Cores disponíveis:**\n\n🔵 Primary (Azul)\n⚫ Secondary (Cinza)\n🟢 Success (Verde)\n🔴 Danger (Vermelho)"
    return e

class CorBotaoEstiloSelect(discord.ui.Select):
    def __init__(self, config, gid, botao_key):
        self.config = config
        self.gid = gid
        self.botao_key = botao_key
        opts = [
            discord.SelectOption(label="Primary (Azul)", value="primary", description="Cor azul padrão do Discord", emoji="🔵"),
            discord.SelectOption(label="Secondary (Cinza)", value="secondary", description="Cor cinza secundária", emoji="⚫"),
            discord.SelectOption(label="Success (Verde)", value="success", description="Cor verde de sucesso", emoji="🟢"),
            discord.SelectOption(label="Danger (Vermelho)", value="danger", description="Cor vermelha de perigo", emoji="🔴"),
        ]
        super().__init__(placeholder="Escolha uma cor", options=opts)
    async def callback(self, i):
        if "botoes_cores" not in self.config or not isinstance(self.config["botoes_cores"], dict):
            self.config["botoes_cores"] = {}
        self.config["botoes_cores"][self.botao_key] = self.values[0]
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_botoes_lista(self.config), view=BotoesCoresMainView(self.config, self.gid))

class CorBotaoEstiloView(discord.ui.View):
    def __init__(self, config, gid, botao_key):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.botao_key = botao_key
        self.add_item(CorBotaoEstiloSelect(config, gid, botao_key))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_botoes_lista(self.config), view=BotoesCoresMainView(self.config, self.gid))

class BotaoCorSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        b_textos = config.get("botoes_textos", {})
        if not isinstance(b_textos, dict):
            b_textos = {}
        opts = []
        for k in BOTOES_LISTA_UNICA:
            info = BOTOES_INFO[k]
            nome_atual = b_textos.get(k) or info["label"]
            opts.append(discord.SelectOption(label=nome_atual, value=k))
        super().__init__(placeholder="Selecione o botão para mudar a cor", options=opts)
    async def callback(self, i):
        key = self.values[0]
        nome = self.config.get("botoes_textos", {}).get(key) or BOTOES_INFO[key]["label"]
        await i.response.edit_message(embed=embed_cor_botao(self.config, nome), view=CorBotaoEstiloView(self.config, self.gid, key))

class BotaoEmojiSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        b_emojis = config.get("botoes_emojis", {})
        b_textos = config.get("botoes_textos", {})
        if not isinstance(b_emojis, dict):
            b_emojis = {}
        if not isinstance(b_textos, dict):
            b_textos = {}
        opts = []
        for k in BOTOES_LISTA_UNICA:
            info = BOTOES_INFO[k]
            nome_atual = b_textos.get(k) or info["label"]
            emoji_atual = b_emojis.get(k)
            try:
                opts.append(discord.SelectOption(label=nome_atual, value=k, emoji=emoji_atual if emoji_atual and len(emoji_atual) <= 4 and not emoji_atual.startswith("<") else None))
            except:
                opts.append(discord.SelectOption(label=nome_atual, value=k))
        super().__init__(placeholder="Selecione qual emoji deseja alterar", options=opts)
    async def callback(self, i):
        key = self.values[0]
        nome_atual = self.config.get("botoes_textos", {}).get(key) or BOTOES_INFO[key]["label"]
        await i.response.send_message(f"📩 **Envie o emoji no chat que deseja definir para \"{nome_atual}\"**\n\nEnvie um emoji normal ou um emoji do servidor. Digite `remover` para voltar ao padrão ou `cancelar` para cancelar.", ephemeral=True)
        def check(m):
            return m.author.id == i.user.id and m.channel.id == i.channel.id
        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            content = msg.content.strip()
            if content.lower() == "cancelar":
                try:
                    await msg.delete()
                except:
                    pass
                try:
                    await i.delete_original_response()
                except:
                    pass
                return
            try:
                await msg.delete()
            except:
                pass
            if "botoes_emojis" not in self.config or not isinstance(self.config["botoes_emojis"], dict):
                self.config["botoes_emojis"] = {}
            if content.lower() == "remover":
                if key in self.config["botoes_emojis"]:
                    del self.config["botoes_emojis"][key]
            else:
                self.config["botoes_emojis"][key] = content
            save(self.gid, self.config)
            await i.message.edit(embed=embed_botoes_lista(self.config), view=BotoesEmojisMainView(self.config, self.gid))
            try:
                await i.delete_original_response()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                await i.delete_original_response()
            except:
                pass

class BotaoTextoSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        b_textos = config.get("botoes_textos", {})
        if not isinstance(b_textos, dict):
            b_textos = {}
        opts = []
        for k in BOTOES_LISTA_UNICA:
            info = BOTOES_INFO[k]
            nome_atual = b_textos.get(k) or info["label"]
            opts.append(discord.SelectOption(label=nome_atual, value=k))
        super().__init__(placeholder="Selecione qual botão deseja renomear", options=opts)
    async def callback(self, i):
        key = self.values[0]
        nome_atual = self.config.get("botoes_textos", {}).get(key) or BOTOES_INFO[key]["label"]
        await i.response.send_message(f"✏️ **Digite o texto:**\nEx: Gel Normal ou Gel Infinito...\n\nBotão atual: `{nome_atual}`\n\nVocê tem 60 segundos. Digite `remover` para voltar ao padrão ou `cancelar` para cancelar.", ephemeral=True)
        def check(m):
            return m.author.id == i.user.id and m.channel.id == i.channel.id
        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            content = msg.content.strip()
            if content.lower() == "cancelar":
                try:
                    await msg.delete()
                except:
                    pass
                try:
                    await i.delete_original_response()
                except:
                    pass
                return
            try:
                await msg.delete()
            except:
                pass
            if "botoes_textos" not in self.config or not isinstance(self.config["botoes_textos"], dict):
                self.config["botoes_textos"] = {}
            if content.lower() == "remover":
                if key in self.config["botoes_textos"]:
                    del self.config["botoes_textos"][key]
            else:
                self.config["botoes_textos"][key] = content[:80]
            save(self.gid, self.config)
            await i.message.edit(embed=embed_botoes_lista(self.config), view=BotoesTextosMainView(self.config, self.gid))
            try:
                await i.delete_original_response()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                await i.delete_original_response()
            except:
                pass

class BotoesEmojisMainView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(BotaoEmojiSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=BotoesConfigView(self.config, self.gid))

class BotoesTextosMainView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(BotaoTextoSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=BotoesConfigView(self.config, self.gid))

class BotoesCoresMainView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(BotaoCorSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=BotoesConfigView(self.config, self.gid))

class BotoesConfigView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
    @discord.ui.button(label="Alterar Emojis", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def emojis(self, i, b):
        await i.response.edit_message(embed=embed_botoes_lista(self.config), view=BotoesEmojisMainView(self.config, self.gid))
    @discord.ui.button(label="Alterar Texto", emoji="✏️", style=discord.ButtonStyle.secondary, row=0)
    async def texto(self, i, b):
        await i.response.edit_message(embed=embed_botoes_lista(self.config), view=BotoesTextosMainView(self.config, self.gid))
    @discord.ui.button(label="Alterar Cor", emoji="🎨", style=discord.ButtonStyle.secondary, row=0)
    async def cor(self, i, b):
        await i.response.edit_message(embed=embed_botoes_lista(self.config), view=BotoesCoresMainView(self.config, self.gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=0)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=VisualView(self.config, self.gid))

class CorSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = [
            discord.SelectOption(label="Vermelho", value="#FF0000", emoji="🔴"),
            discord.SelectOption(label="Azul", value="#1E90FF", emoji="🔵"),
            discord.SelectOption(label="Verde", value="#00FF00", emoji="🟢"),
            discord.SelectOption(label="Amarelo", value="#FFFF00", emoji="🟡"),
            discord.SelectOption(label="Roxo", value="#800080", emoji="🟣"),
            discord.SelectOption(label="Rosa", value="#FF69B4", emoji="🌸"),
            discord.SelectOption(label="Laranja", value="#FFA500", emoji="🟠"),
            discord.SelectOption(label="Azul Marinho", value="#000080", emoji="🔷"),
            discord.SelectOption(label="Preto", value="#000000", emoji="⚫"),
        ]
        super().__init__(placeholder="👉 Selecione uma cor", options=opts)
    async def callback(self, inter):
        self.config["cor_org"] = self.values[0]
        save(self.gid, self.config)
        await inter.response.edit_message(embed=embed_visual(self.config), view=CorView(self.config, self.gid))

class CorView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(CorSelect(config, gid))
    @discord.ui.button(label="Digitar Cor", emoji="✏️", style=discord.ButtonStyle.secondary, row=1)
    async def digitar(self, i, b):
        await i.response.send_modal(CorModal(self.config, self.gid))
    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=VisualView(self.config, self.gid))

class VisualView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
    @discord.ui.button(label="Escolher Cor", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def cor(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=CorView(self.config, self.gid))
    @discord.ui.button(label="Alterar Embed", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def embed(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=AlterarEmbedView(self.config, self.gid))
    @discord.ui.button(label="Alterar Botões", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def botoes(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=BotoesConfigView(self.config, self.gid))
    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.danger, row=0)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_filas(self.config), view=FilasView(self.config, self.gid))

class AlterarEmbedView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
    @discord.ui.button(label="Alterar Emojis", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def emojis(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=EmojisView(self.config, self.gid))
    @discord.ui.button(label="Alterar Título", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def titulo(self, i, b):
        await i.response.send_modal(TituloModal(self.config, self.gid))
    @discord.ui.button(label="Alterar Thumbnail", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def thumb(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=ThumbnailView(self.config, self.gid))
    @discord.ui.button(label="Alterar Banner", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def banner(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=BannerView(self.config, self.gid))
    @discord.ui.button(label="Alterar Rodapé", emoji="⚙️", style=discord.ButtonStyle.secondary, row=0)
    async def rodape(self, i, b):
        await i.response.send_modal(FooterModal(self.config, self.gid))
    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=VisualView(self.config, self.gid))

class EmojiTipoSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        if not isinstance(self.config.get("embed_emojis"), dict):
            self.config["embed_emojis"] = {"modo": "👑", "valor": "💰", "jogadores": "🔥"}
        opts = [
            discord.SelectOption(label="Modo", value="modo", description=f"Atual: {self.config['embed_emojis'].get('modo','👑')}"),
            discord.SelectOption(label="Valor", value="valor", description=f"Atual: {self.config['embed_emojis'].get('valor','💰')}"),
            discord.SelectOption(label="Jogador", value="jogadores", description=f"Atual: {self.config['embed_emojis'].get('jogadores','🔥')}"),
        ]
        super().__init__(placeholder="Selecione qual emoji deseja alterar", options=opts)
    async def callback(self, i):
        tipo = self.values[0]
        await i.response.send_message(f"✏️ **Envie o emoji que deseja usar para \"{tipo.upper()}\"**\n\nVocê tem 60 segundos. Digite `cancelar` para cancelar.", ephemeral=True)
        def check(m):
            return m.author.id == i.user.id and m.channel.id == i.channel.id
        try:
            msg = await bot.wait_for("message", timeout=60.0, check=check)
            if msg.content.lower() == "cancelar":
                try:
                    await msg.delete()
                except:
                    pass
                try:
                    await i.delete_original_response()
                except:
                    pass
                return
            novo_emoji = msg.content.strip()
            try:
                await msg.delete()
            except:
                pass
            if "embed_emojis" not in self.config or not isinstance(self.config["embed_emojis"], dict):
                self.config["embed_emojis"] = {"modo": "👑", "valor": "💰", "jogadores": "🔥"}
            self.config["embed_emojis"][tipo] = novo_emoji
            save(self.gid, self.config)
            await i.message.edit(embed=embed_visual(self.config), view=EmojisView(self.config, self.gid))
            try:
                await i.delete_original_response()
            except:
                pass
        except asyncio.TimeoutError:
            try:
                await i.delete_original_response()
            except:
                pass

class EmojisView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(EmojiTipoSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=AlterarEmbedView(self.config, self.gid))

class ThumbnailTipoSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = [
            discord.SelectOption(label="Mobile", value="mobile", emoji="📱"),
            discord.SelectOption(label="Emulador", value="emulador", emoji="🖥️"),
            discord.SelectOption(label="Misto", value="misto", emoji="🔀"),
            discord.SelectOption(label="Tático", value="tatico", emoji="🎯"),
        ]
        super().__init__(placeholder="Selecione o tipo de thumbnail", options=opts)
    async def callback(self, i):
        await i.response.send_modal(ThumbnailModal(self.config, self.gid, self.values[0]))

class BannerTipoSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = [
            discord.SelectOption(label="Mobile", value="mobile", emoji="📱"),
            discord.SelectOption(label="Emulador", value="emulador", emoji="🖥️"),
            discord.SelectOption(label="Misto", value="misto", emoji="🔀"),
            discord.SelectOption(label="Tático", value="tatico", emoji="🎯"),
        ]
        super().__init__(placeholder="Selecione o tipo de banner", options=opts)
    async def callback(self, i):
        await i.response.send_modal(BannerModal(self.config, self.gid, self.values[0]))

class ThumbnailView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(ThumbnailTipoSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=AlterarEmbedView(self.config, self.gid))

class BannerView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(BannerTipoSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_visual(self.config), view=AlterarEmbedView(self.config, self.gid))

def embed_taxa_org(c):
    e = discord.Embed(color=get_cor_embed(c))
    e.set_author(name="⚙️ Configuração de Taxa da Organização")
    e.add_field(name="💲 Sistema de Taxas", value="Configure a taxa cobrada para criação de salas da organização", inline=False)
    e.add_field(name="⚙️ Informações:", value="↪ A taxa será aplicada em cada criação de sala\n↪ Valor configurado aparecerá nos embeds de fila\n↪ Use o botão abaixo para definir o valor", inline=False)
    e.add_field(name="✅ Taxa Atual Configurada:", value=f"```{c.get('taxa_org','0,10')}```", inline=False)
    e.set_footer(text=f"Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e

class TaxaModal(discord.ui.Modal, title="❓ - Qual será o novo valor?"):
    valor_input = discord.ui.TextInput(label="Digite aqui o novo valor da taxa!", placeholder="Ex: 0,10", required=True, max_length=4)
    def __init__(self, config, gid):
        super().__init__(title="❓ - Qual será o novo valor?")
        self.config = config
        self.gid = gid
    async def on_submit(self, i):
        valor = str(self.valor_input.value).strip().replace(".", ",")
        if not valor.startswith("0,"):
            await i.response.send_message("❌ Só pode colocar taxa em centavos! Ex: 0,10", ephemeral=True)
            return
        try:
            partes = valor.split(",")
            if len(partes)!=2 or not partes[1].isdigit() or len(partes[1])>2:
                raise ValueError
            centavos = int(partes[1])
            if centavos<=0 or centavos>=100:
                raise ValueError
        except:
            await i.response.send_message("❌ Formato inválido! Use apenas centavos ex: 0,10 até 0,99", ephemeral=True)
            return
        self.config["taxa_org"] = valor
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_taxa_org(self.config), view=TaxaView(self.config, self.gid))

class TaxaView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
    @discord.ui.button(label="Definir Quantidade", emoji="✏️", style=discord.ButtonStyle.secondary, row=0)
    async def definir(self, i, b):
        await i.response.send_modal(TaxaModal(self.config, self.gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=0)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_filas(self.config), view=FilasView(self.config, self.gid))

def embed_configurar_categoria(c, guild=None):
    atual = c.get("categoria_apostas")
    if guild and atual:
        obj = guild.get_channel(atual)
        atual_txt = f"**{obj.name}**" if obj else f"<#{atual}>"
    else:
        atual_txt = f"<#{atual}>" if atual else "não configurada"
    e = discord.Embed(color=get_cor_embed(c))
    e.title = "CONFIGURAR CATEGORIA"
    e.description = f"Configure a categoria das apostas usando o painel abaixo\n\n🎯 | Selecione abaixo, a nova categoria de novas filas:\n\n**Categoria atual:** {atual_txt}"
    e.set_footer(text=f"Configuração • Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e

def embed_canal_analistas(c, guild=None):
    atual = c.get("canal_analistas")
    if guild and atual:
        obj = guild.get_channel(atual)
        atual_txt = obj.mention if obj else f"<#{atual}>"
    else:
        atual_txt = f"<#{atual}>" if atual else "não configurado"
    e = discord.Embed(color=get_cor_embed(c))
    e.title = "CANAL ANALISTAS"
    e.description = f"Configure o canal para analistas usando o painel abaixo\n\n📢 | Selecione abaixo o canal para analistas:\n\n**Canal atual:** {atual_txt}"
    e.set_footer(text=f"Configuração • Hoje às {datetime.datetime.now().strftime('%H:%M')}")
    return e

def embed_canais_config(c, guild=None):
    cat = c.get("categoria_apostas")
    canal = c.get("canal_analistas")
    if guild:
        cat_obj = guild.get_channel(cat) if cat else None
        canal_obj = guild.get_channel(canal) if canal else None
        cat_txt = f"**{cat_obj.name}**" if cat_obj else "não configurada"
        canal_txt = canal_obj.mention if canal_obj else "não configurado"
    else:
        cat_txt = f"<#{cat}>" if cat else "não configurada"
        canal_txt = f"<#{canal}>" if canal else "não configurado"
    e = discord.Embed(color=get_cor_embed(c))
    e.set_author(name="CONFIGURAR CANAIS")
    e.description = f"Configure categorias e canais usando o painel abaixo\n\n🛠️ | Selecione o que deseja configurar:\n\n🎰 • Categorias das apostas\nCategoria atual: {cat_txt}\n\n🧠 • Canal analistas\nCanal atual: {canal_txt}\n\n⚙️ Configuração • Hoje às {datetime.datetime.now().strftime('%H:%M')}"
    return e

class CategoriaChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        super().__init__(channel_types=[discord.ChannelType.category], placeholder="🔍 - Defina a categoria!", min_values=1, max_values=1)
    async def callback(self, i):
        categoria = self.values[0]
        self.config["categoria_apostas"] = categoria.id
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_configurar_categoria(self.config, i.guild), view=CategoriaSelectView(self.config, self.gid))

class CategoriaSelectView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(CategoriaChannelSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_canais_config(self.config, i.guild), view=CanaisConfigView(self.config, self.gid))

class CanalAnalistaChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        super().__init__(channel_types=[discord.ChannelType.text], placeholder="Selecione um canal de texto", min_values=1, max_values=1)
    async def callback(self, i):
        canal = self.values[0]
        self.config["canal_analistas"] = canal.id
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_canal_analistas(self.config, i.guild), view=CanalAnalistaSelectView(self.config, self.gid))

class CanalAnalistaSelectView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(CanalAnalistaChannelSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_canais_config(self.config, i.guild), view=CanaisConfigView(self.config, self.gid))

class CanaisCategoriasSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = [
            discord.SelectOption(label="Categorias das apostas", description="Definir a categoria onde as filas serão criadas", value="categoria_apostas", emoji="🎰"),
            discord.SelectOption(label="Canal analistas", description="Definir o canal de analistas", value="canal_analistas", emoji="🧠"),
        ]
        super().__init__(placeholder="Escolha uma opção", options=opts)
    async def callback(self, i):
        if self.values[0] == "categoria_apostas":
            await i.response.edit_message(embed=embed_configurar_categoria(self.config, i.guild), view=CategoriaSelectView(self.config, self.gid))
        elif self.values[0] == "canal_analistas":
            await i.response.edit_message(embed=embed_canal_analistas(self.config, i.guild), view=CanalAnalistaSelectView(self.config, self.gid))

class CanaisConfigView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(CanaisCategoriasSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_filas(self.config), view=FilasView(self.config, self.gid))

def embed_gerenciar_valores(c):
    vals = sorted(c.get("valores_filas", []), reverse=True)
    if vals:
        lista_formatada = ", ".join([formatar_valor_br(v) for v in vals])
    else:
        lista_formatada = "Nenhum valor cadastrado"
    e = discord.Embed(color=0x2B2D31)
    e.title = "Gerenciar Valores"
    e.description = f"**Sistema de Valores das Apostas**\nConfigure os valores disponíveis para apostas nas filas\n\n**Opções Disponíveis:**\n↪ Adicione um valor - Adiciona novo valor à lista\n↪ Remove um valor - Remove valor existente\n↪ Digitar valores - Insere manualmente todos os valores\n\n**Valores Cadastrados:**\n```{lista_formatada}```\n\n**Valores serão usados nas filas de apostas**\nHorário: {datetime.datetime.now().strftime('%H:%M')}"
    return e

def embed_remover_valor(c):
    vals = sorted(c.get("valores_filas", []), reverse=True)
    lista = ", ".join([formatar_valor_br(v) for v in vals]) if vals else "Nenhum"
    e = discord.Embed(color=0x2B2D31)
    e.set_author(name="NEON APOSTAS")
    e.title = "🗑️ Remover Valor"
    e.description = f"**Selecione o valor para remover**\nEscolha o valor que deseja remover da lista\n\n**Valores Cadastrados:**\n```{lista}```\n\n❗ Selecione um valor abaixo para remover\nHoje às {datetime.datetime.now().strftime('%H:%M')}"
    return e

class ValorRemoverSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        vals = sorted(config.get("valores_filas", []), reverse=True)
        opts = []
        for v in vals[:25]:
            br = formatar_valor_br(v)
            opts.append(discord.SelectOption(label=f"R$ {br}", description=f"Remover o valor {br}", value=str(v), emoji="💲"))
        if not opts:
            opts = [discord.SelectOption(label="Nenhum valor", value="none")]
        super().__init__(placeholder="Selecione o valor para remover", options=opts, min_values=1, max_values=1)
    async def callback(self, i):
        if self.values[0] == "none":
            await i.response.send_message("Nenhum valor para remover", ephemeral=True)
            return
        try:
            valor_sel = float(self.values[0])
        except:
            await i.response.send_message("Erro", ephemeral=True)
            return
        lista = self.config.get("valores_filas", [])
        nova = [x for x in lista if float(x)!= valor_sel]
        self.config["valores_filas"] = sorted(nova, reverse=True)
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_gerenciar_valores(self.config), view=GerenciarValoresView(self.config, self.gid))

class RemoverValorView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(ValorRemoverSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_gerenciar_valores(self.config), view=GerenciarValoresView(self.config, self.gid))

class DefinirValoresModal(discord.ui.Modal, title="Definir Valores"):
    valores_input = discord.ui.TextInput(label="Informe os valores separados por vírgula", placeholder="Ex: 100, 50, 20, 10, 5, 3, 2, 1, 0.50", style=discord.TextStyle.long, max_length=4000, required=True)
    def __init__(self, config, gid):
        super().__init__(title="Definir Valores")
        self.config = config
        self.gid = gid
    async def on_submit(self, i):
        vals = parse_valores_input(str(self.valores_input.value))
        if not vals:
            await i.response.send_message("❌ Nenhum valor válido! Use: 100, 50, 20, 10", ephemeral=True)
            return
        vals_unicos = []
        for v in vals:
            if v not in vals_unicos:
                vals_unicos.append(v)
        self.config["valores_filas"] = sorted(vals_unicos, reverse=True)
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_gerenciar_valores(self.config), view=GerenciarValoresView(self.config, self.gid))

class AdicionarValorModal(discord.ui.Modal, title="Adicionar Valor"):
    valor_input = discord.ui.TextInput(label="Informe o valor", placeholder="Digite o valor (ex: 100, 50.00, 0.50)", max_length=20, required=True)
    def __init__(self, config, gid):
        super().__init__(title="Adicionar Valor")
        self.config = config
        self.gid = gid
    async def on_submit(self, i):
        texto = str(self.valor_input.value).strip()
        try:
            primeiro = texto.split(",")[0].strip()
            num = float(primeiro.replace(",", "."))
            if num <= 0:
                raise ValueError
        except:
            await i.response.send_message("❌ Valor inválido!", ephemeral=True)
            return
        if "valores_filas" not in self.config:
            self.config["valores_filas"] = []
        self.config["valores_filas"].append(num)
        vistos = []
        for v in self.config["valores_filas"]:
            if v not in vistos:
                vistos.append(v)
        self.config["valores_filas"] = sorted(vistos, reverse=True)
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_gerenciar_valores(self.config), view=GerenciarValoresView(self.config, self.gid))

class GerenciarValoresView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
    @discord.ui.button(label="Adicionar um valor", emoji="➕", style=discord.ButtonStyle.secondary, row=0)
    async def add(self, i, b):
        await i.response.send_modal(AdicionarValorModal(self.config, self.gid))
    @discord.ui.button(label="Remover um valor", emoji="🗑️", style=discord.ButtonStyle.secondary, row=0)
    async def remover(self, i, b):
        await i.response.edit_message(embed=embed_remover_valor(self.config), view=RemoverValorView(self.config, self.gid))
    @discord.ui.button(label="Digitar valores", emoji="✏️", style=discord.ButtonStyle.secondary, row=0)
    async def digitar(self, i, b):
        await i.response.send_modal(DefinirValoresModal(self.config, self.gid))
    @discord.ui.button(label="Voltar", emoji="↩️", style=discord.ButtonStyle.danger, row=0)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_filas(self.config), view=FilasView(self.config, self.gid))

class CanalFilaChannelSelect(discord.ui.ChannelSelect):
    def __init__(self, config, gid, tipo_key, tipo_label):
        self.config = config
        self.gid = gid
        self.tipo_key = tipo_key
        self.tipo_label = tipo_label
        super().__init__(channel_types=[discord.ChannelType.text, discord.ChannelType.voice], placeholder=f"🔍 Selecione o canal para {tipo_label}", min_values=1, max_values=1)
    async def callback(self, i):
        canal = self.values[0]
        if "canais_filas" not in self.config:
            self.config["canais_filas"] = {}
        self.config["canais_filas"][self.tipo_key] = canal.id
        save(self.gid, self.config)
        avatar_url = i.client.user.display_avatar.url if i.client.user.display_avatar else None
        await i.response.edit_message(embed=embed_setar_filas(self.config, i.guild, avatar_url), view=SetarFilasView(self.config, self.gid))

class CanalFilaSelectView(discord.ui.View):
    def __init__(self, config, gid, tipo_key, tipo_label):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.tipo_key = tipo_key
        self.tipo_label = tipo_label
        self.add_item(CanalFilaChannelSelect(config, gid, tipo_key, tipo_label))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        avatar_url = i.client.user.display_avatar.url if i.client.user.display_avatar else None
        await i.response.edit_message(embed=embed_setar_filas(self.config, i.guild, avatar_url), view=SetarFilasView(self.config, self.gid))

class TipoFilaSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = []
        for key, label, emoji in FILAS_TIPOS:
            opts.append(discord.SelectOption(label=label, value=key, emoji=emoji, description=f"Definir canal para {label}"))
        super().__init__(placeholder="Selecione o tipo de fila", options=opts, min_values=1, max_values=1)
    async def callback(self, i):
        tipo_key = self.values[0]
        label = next((x[1] for x in FILAS_TIPOS if x[0]==tipo_key), tipo_key)
        await i.response.edit_message(embed=embed_selecionar_canal_fila(self.config, label), view=CanalFilaSelectView(self.config, self.gid, tipo_key, label))

class SetarFilasView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(TipoFilaSelect(config, gid))
    @discord.ui.button(label="Enviar filas novas", emoji="⚙️", style=discord.ButtonStyle.secondary, row=1)
    async def enviar(self, i, b):
        await i.response.defer(ephemeral=True)
        c = get_config(i.guild.id)
        canais = c.get("canais_filas", {})
        if not canais:
            await i.followup.send("❌ Nenhum canal de fila configurado!", ephemeral=True)
            return
        valores = sorted(c.get("valores_filas", []), reverse=True)
        if not valores:
            valores = [1.0]
        total = 0
        for tipo_key, canal_id in canais.items():
            canal = i.guild.get_channel(canal_id)
            if not canal:
                continue
            for valor in valores:
                embed = criar_embed_fila(c, tipo_key, valor)
                view = FilaView(c, i.guild.id, tipo_key)
                try:
                    await canal.send(embed=embed, view=view)
                    total += 1
                except Exception as e:
                    print(f"Erro ao enviar fila {tipo_key} no canal {canal_id}: {e}")
                await asyncio.sleep(0.6)
        await i.followup.send(f"✅ {total} filas enviadas com sucesso! Todos os modos com todos os valores.", ephemeral=True)
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_filas(self.config), view=FilasView(self.config, self.gid))

class FilasSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = [
            discord.SelectOption(label="Configurar Visual", description="Personalize o visual dos embeds, cores, botões e etc da fila", emoji="⚙️"),
            discord.SelectOption(label="Taxa da org", description="Configure as taxas da organização", emoji="⚙️"),
            discord.SelectOption(label="Configurar canais e categorias", description="Configure os canais e categorias das fila, analista, Streamer", emoji="⚙️"),
            discord.SelectOption(label="Gerenciar valores", description="Adiciona ou remova valores das apostas", emoji="⚙️"),
            discord.SelectOption(label="Setar Canais", description="Escolha os canais onde as filas serão postadas", emoji="⚙️"),
            discord.SelectOption(label="Streamer", description="Configure as filas streamer", emoji="⚙️"),
            discord.SelectOption(label="Coins e Vitórias", description="Mude a quantidade de coins e vitórias", emoji="⚙️"),
            discord.SelectOption(label="Criar Botão", description="Crie um botão totalmente customizado", emoji="⚙️"),
        ]
        super().__init__(placeholder="Selecione uma configuração", options=opts)
    async def callback(self, i):
        if self.values[0] == "Configurar Visual":
            await i.response.edit_message(embed=embed_visual(self.config), view=VisualView(self.config, self.gid))
        elif self.values[0] == "Taxa da org":
            await i.response.edit_message(embed=embed_taxa_org(self.config), view=TaxaView(self.config, self.gid))
        elif self.values[0] == "Configurar canais e categorias":
            await i.response.edit_message(embed=embed_canais_config(self.config, i.guild), view=CanaisConfigView(self.config, self.gid))
        elif self.values[0] == "Gerenciar valores":
            await i.response.edit_message(embed=embed_gerenciar_valores(self.config), view=GerenciarValoresView(self.config, self.gid))
        elif self.values[0] == "Setar Canais":
            avatar_url = i.client.user.display_avatar.url if i.client.user.display_avatar else None
            await i.response.edit_message(embed=embed_setar_filas(self.config, i.guild, avatar_url), view=SetarFilasView(self.config, self.gid))
        else:
            await i.response.defer()

class FilasView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(FilasSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.danger, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_config(self.config, i.guild), view=BotView(self.config, self.gid))

class RoleMenu(discord.ui.RoleSelect):
    def __init__(self, config, gid, key, titulo, desc):
        super().__init__(placeholder="Selecione o role/cargo!", min_values=1, max_values=1)
        self.config = config
        self.gid = gid
        self.key = key
        self.titulo = titulo
        self.desc = desc
    async def callback(self, i):
        self.config["permissoes"][self.key] = [self.values[0].id]
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_generico(self.config, self.titulo, self.desc, self.config["permissoes"][self.key]), view=ViewGenerico(self.config, self.gid, self.key, self.titulo, self.desc))

class RoleView(discord.ui.View):
    def __init__(self, config, gid, key, titulo, desc):
        super().__init__(timeout=120)
        self.add_item(RoleMenu(config, gid, key, titulo, desc))
        self.config = config
        self.gid = gid
        self.key = key
        self.titulo = titulo
        self.desc = desc
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.secondary, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_generico(self.config, self.titulo, self.desc, self.config["permissoes"][self.key]), view=ViewGenerico(self.config, self.gid, self.key, self.titulo, self.desc))

class ViewGenerico(discord.ui.View):
    def __init__(self, config, gid, key, titulo, desc):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.key = key
        self.titulo = titulo
        self.desc = desc
    @discord.ui.button(label="Adicionar Role", emoji="➕", style=discord.ButtonStyle.success)
    async def add(self, i, b):
        await i.response.edit_message(view=RoleView(self.config, self.gid, self.key, self.titulo, self.desc))
    @discord.ui.button(label="Remover Role", emoji="➖", style=discord.ButtonStyle.danger)
    async def rem(self, i, b):
        self.config["permissoes"][self.key] = []
        save(self.gid, self.config)
        await i.response.edit_message(embed=embed_generico(self.config, self.titulo, self.desc, []), view=ViewGenerico(self.config, self.gid, self.key, self.titulo, self.desc))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.secondary, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_lista(self.config), view=PermView(self.config, self.gid))

class PermSelect(discord.ui.Select):
    def __init__(self, config, gid):
        self.config = config
        self.gid = gid
        opts = [
            discord.SelectOption(label="Permissão máxima", description="Acesso total ao sistema", emoji="👑"),
            discord.SelectOption(label="Cargo Mediador/ADM", description="Cargos de mediadores e administradores", emoji="👨‍💼"),
            discord.SelectOption(label="Ver apostas", description="Visualizar apostas e estatísticas", emoji="📊"),
            discord.SelectOption(label="Gerenciar filas", description="Remover mediadores das filas", emoji="📋"),
            discord.SelectOption(label="SS Mobile", description="Screenshots de dispositivos móveis", emoji="📱"),
            discord.SelectOption(label="SS Emu", description="Screenshots de emuladores", emoji="🖥️")
        ]
        super().__init__(placeholder="Selecione a categoria", options=opts)
    async def callback(self, i):
        mapa = {
            "Permissão máxima": ("permissao_maxima", "👑 Permissão máxima", "Acesso total ao sistema"),
            "Cargo Mediador/ADM": ("cargo_mediador_adm", "👨‍💼 Cargo Mediador/ADM", "Cargos de mediadores e administradores"),
            "Ver apostas": ("ver_apostas", "👁️ Ver apostas / Ver filas", "Visualizar apostas e estatísticas"),
            "Gerenciar filas": ("gerenciar_filas", "📋 Gerenciar filas", "Remover mediadores das filas"),
            "SS Mobile": ("ss_mobile", "📱 SS Mobile", "Screenshots de dispositivos móveis"),
            "SS Emu": ("ss_emu", "🖥️ SS Emu", "Screenshots de emuladores")
        }
        key, titulo, desc = mapa[self.values[0]]
        e = embed_generico(self.config, titulo, desc, self.config["permissoes"][key])
        v = ViewGenerico(self.config, self.gid, key, titulo, desc)
        await i.response.edit_message(embed=e, view=v)

class PermView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
        self.add_item(PermSelect(config, gid))
    @discord.ui.button(label="Voltar", emoji="⬅️", style=discord.ButtonStyle.secondary, row=1)
    async def voltar(self, i, b):
        await i.response.edit_message(embed=embed_config(self.config, i.guild), view=BotView(self.config, self.gid))

class BotView(discord.ui.View):
    def __init__(self, config, gid):
        super().__init__(timeout=None)
        self.config = config
        self.gid = gid
    @discord.ui.button(label="Config Filas", emoji="⚙️", style=discord.ButtonStyle.primary, row=0)
    async def b1(self, i, b):
        await i.response.edit_message(embed=embed_filas(self.config), view=FilasView(self.config, self.gid))
    @discord.ui.button(label="Permissões", emoji="⚙️", style=discord.ButtonStyle.primary, row=0)
    async def perm(self, i, b):
        await i.response.edit_message(embed=embed_lista(self.config), view=PermView(self.config, self.gid))
    @discord.ui.button(label="Configurações", emoji="👤", style=discord.ButtonStyle.primary, row=0)
    async def b2(self, i, b):
        await i.response.send_message("Em breve!", ephemeral=True)
    @discord.ui.button(label="Editar perfil", emoji="⚙️", style=discord.ButtonStyle.primary, row=0)
    async def b3(self, i, b):
        await i.response.send_message("Em breve!", ephemeral=True)
    @discord.ui.button(label="Todas logs", emoji="⚙️", style=discord.ButtonStyle.primary, row=1)
    async def b4(self, i, b):
        await i.response.send_message("Em breve!", ephemeral=True)
    @discord.ui.button(label="Config Rank", emoji="⚙️", style=discord.ButtonStyle.primary, row=1)
    async def b5(self, i, b):
        await i.response.send_message("Em breve!", ephemeral=True)
    @discord.ui.button(label="Embed Aviso", emoji="🗒️", style=discord.ButtonStyle.primary, row=1)
    async def b6(self, i, b):
        await i.response.send_message("Em breve!", ephemeral=True)
    @discord.ui.button(label="Enviar filas novas", emoji="⚙️", style=discord.ButtonStyle.secondary, row=2)
    async def b7(self, i, b):
        await i.response.send_message("Em breve!", ephemeral=True)

class ResultadoView(discord.ui.View):
    def __init__(self, atendente_id, tipo):
        super().__init__(timeout=None)
        self.atendente_id = atendente_id
        self.tipo = tipo
    async def check_atendente(self, i):
        if i.user.id!= self.atendente_id:
            await i.response.send_message(f"❌ | Só o <@{self.atendente_id}> que aceitou pode definir!", ephemeral=True)
            return False
        return True
    @discord.ui.button(label="W.O", style=discord.ButtonStyle.secondary, row=0)
    async def wo(self, i, b):
        if not await self.check_atendente(i):
            return
        await i.response.send_message(f"{i.user.mention} Definiu W.O!", ephemeral=False)
    @discord.ui.button(label="Limpo", style=discord.ButtonStyle.success, row=0)
    async def limpo(self, i, b):
        if not await self.check_atendente(i):
            return
        await i.response.send_message(f"{i.user.mention} Definiu Limpo!", ephemeral=False)

class AtenderSSView(discord.ui.View):
    def __init__(self, autor, tipo, config, canal_origem_id):
        super().__init__(timeout=300)
        self.autor = autor
        self.tipo = tipo
        self.config = config
        self.canal_origem_id = canal_origem_id
    @discord.ui.button(label="Atender", style=discord.ButtonStyle.success, emoji="✅")
    async def atender(self, i, b):
        c = self.config
        key = "ss_mobile" if self.tipo == "ssmob" else "ss_emu"
        nome_cargo = "SS Mobile" if self.tipo == "ssmob" else "SS Emu"
        if not c["permissoes"][key]:
            await i.response.send_message(f"❌ | Cargo {nome_cargo} não configurado.", ephemeral=True)
            return
        if not any(r.id in c["permissoes"][key] for r in i.user.roles):
            await i.response.send_message(f"❌ | Você não possui permissão para atender análises {nome_cargo}.", ephemeral=True)
            return
        canal_origem = i.guild.get_channel(self.canal_origem_id)
        if not canal_origem:
            await i.response.send_message("Canal de origem não encontrado!", ephemeral=True)
            return
        e = discord.Embed(color=0x00FF7F)
        e.description = f"**Análise confirmada**\nAguarde as instruções de {i.user.mention}\nA definição será W.O ou se está limpo nos será feita nos botões abaixo"
        e.set_footer(text=f"Hoje às {datetime.datetime.now().strftime('%H:%M')}")
        await canal_origem.send(f"{i.user.mention} aceitou a análise.")
        await canal_origem.send(embed=e, view=ResultadoView(i.user.id, self.tipo))
        await i.response.send_message(f"✅ Você aceitou a análise de {self.autor.mention}!", ephemeral=True)
        try:
            await i.message.delete()
        except:
            pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.lower()
    if content.startswith(".ssmob") or content.startswith(".ssemu"):
        tipo = "ssmob" if content.startswith(".ssmob") else "ssemu"
        c = get_config(message.guild.id)
        cargos_mediador = c["permissoes"].get("cargo_mediador_adm", [])
        if cargos_mediador:
            if not any(r.id in cargos_mediador for r in message.author.roles):
                await message.channel.send(f"❌ | {message.author.mention} Você não tem permissão para usar `{tipo}`! Precisa do cargo de Mediador/ADM.", delete_after=10)
                return
        key = "ss_mobile" if tipo == "ssmob" else "ss_emu"
        if not c["permissoes"][key]:
            await message.channel.send(f"❌ | Cargo {'SS Mobile' if tipo == 'ssmob' else 'SS Emu'} não configurado! Configure em `/botconfig` > Permissões", delete_after=10)
            return
        canal_analista_id = c.get("canal_analistas")
        if not canal_analista_id:
            await message.channel.send("❌ Canal de analistas não configurado! Use `/botconfig`", delete_after=10)
            return
        canal_analista = message.guild.get_channel(canal_analista_id)
        if not canal_analista:
            await message.channel.send("❌ Canal de analistas não encontrado!")
            return
        e = discord.Embed(title=f"Nova solicitação de {tipo.upper()} 📱", description=f"**Solicitante:** {message.author.mention}\n**Canal:** {message.channel.mention}\n**Tipo:** {tipo.upper()}\n\nClique em atender para analisar!", color=0x00FF7F)
        e.set_thumbnail(url=message.author.display_avatar.url if message.author.display_avatar else None)
        e.set_footer(text=f"Solicitado às {datetime.datetime.now().strftime('%H:%M')}")
        view = AtenderSSView(message.author, tipo, c, message.channel.id)
        await canal_analista.send(embed=e, view=view)
        await message.channel.send(f"✅ {message.author.mention} Sua solicitação de **{tipo.upper()}** foi enviada para {canal_analista.mention}!")
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Logado {bot.user}")
    await bot.tree.sync()

@bot.tree.error
async def on_app_command_error(i, e):
    if isinstance(e, app_commands.CheckFailure):
        try:
            await i.response.send_message("você não tem permissão para usar este comando.", ephemeral=True)
        except:
            await i.followup.send("você não tem permissão para usar este comando.", ephemeral=True)

@bot.tree.command(name="botconfig")
@check_max()
async def botconfig(i: discord.Interaction):
    c = get_config(i.guild.id)
    await i.response.send_message(embed=embed_config(c, i.guild), view=BotView(c, i.guild.id))

bot.run("SEU_TOKEN_AQUI")
