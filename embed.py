import discord

def dsEmbed():
    embed = discord.Embed(title=f"🤚  Verificación de reglas", description="Antes de acceder al servidor, por favor, verifica que leíste y estás de acuerdo con las reglas.", color=0xffffff)
    embed.add_field(name="¿Estás de acuerdo con las reglas?", value="Por favor, hace clic en el emoji de la mano para verificar.", inline=False)
    embed.set_footer(text=f"")

    return embed