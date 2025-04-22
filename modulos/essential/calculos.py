import discord,os,asyncio,time,json
from discord.ext import commands
from discord import app_commands
#from modulos.connection.database import BancoServidores


#def calcular_saldo(cash):

#    if abs(cash) >= 1_000_000_000_000:
 #       return "{:,.1f}T".format(cash / 1_000_000_000_000)
 #   elif abs(cash) >= 1_000_000_000:
 #       return "{:,.1f}B".format(cash / 1_000_000_000)
 #   elif abs(cash) >= 1_000_000:
 #       return "{:,.1f}M".format(cash / 1_000_000)
 #   else:
 #       return "{:,.0f}".format(cash)

def calcular_saldo(cash):
    if abs(cash) >= 1_000_000_000_000:
        return "{:,.1f}T".format(int(cash / 1_000_000_000_000 * 10) / 10)
    elif abs(cash) >= 1_000_000_000:
        return "{:,.1f}B".format(int(cash / 1_000_000_000 * 10) / 10)
    elif abs(cash) >= 1_000_000:
        return "{:,.1f}M".format(int(cash / 1_000_000 * 10) / 10)
    else:
        return "{:,.0f}".format(cash)


def calcular_nivel(xp):
    # Defina a relação entre XP e nível
    xp_por_nivel = 500  # Por exemplo, 300 XP para cada nível
    # Calcula o nível baseado no XP
    nivel = xp // xp_por_nivel
    
    return nivel