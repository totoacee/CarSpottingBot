import discord
import requests
import json
import uuid
import os 
from discord.ext import commands
from discord.ext import menus
from dotenv import load_dotenv

# Scripts propios
from patente import determine_year

# BOT INITIAL
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión.')
    await bot.change_presence(activity=discord.Game(name="$spot - $cars - $help"))

    #UPDATE NOTIFICATION
    user = await bot.get_user_id(885742833863110746)
    await user.send("Bot actualizado")


# WELCOME SYSTEM
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1050202180512137226)
    welcome_message = f"Bienvenido {member.mention} a nuestro servidor!"
    await channel.send(welcome_message)

@bot.command(name='testbienvenida')
async def test_welcome(ctx):
    member = ctx.message.author
    channel = bot.get_channel(1050202180512137226)
    welcome_message = f"Bienvenido {member.mention} a nuestro servidor!"
    await channel.send(welcome_message)

# HELP COMMAND
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="Comandos disponibles", color=0xffffff)
    embed.add_field(name="`•` $spot", value="Este comando permite registrar un nuevo auto spoteado en tu coleccion.", inline=False)
    embed.add_field(name="`•` $cars [@usuario]", value="Este comando permite ver los autos registrados por un usuario o por otro usuario si se menciona.", inline=False)
    await ctx.channel.send(embed=embed)

# PING TEST
@bot.command(name='hola')
async def hola(ctx):
    await ctx.send('Hola!')

# WEATHER COMMAND
@bot.command(name='clima')
async def clima(ctx):
    location = "Argentina"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&units=metric&appid=0ed761300a2725ca778c07831ae64d6e"

    weather_response = requests.get(url)
    weather_data = weather_response.json()

    if weather_data["cod"] != "404":
        temperature = weather_data["main"]["temp"]
        pressure = weather_data["main"]["pressure"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]

        response = f"Clima actual en {location}: {description}. Temperatura: {temperature}°C, Presión: {pressure}hPa, Humedad: {humidity}%"
    else:
        response = f"No se puede obtener el clima para {location}."

    await ctx.send(response)

# SPOT SYSTEM COMMAND
@bot.command(name='spot')
async def spot(ctx):
    if ctx.message.channel.id == 1072042430079172678 or ctx.message.channel.id == 1050205565915234394:
        file_name = "spotted_cars.json"
        user_id = str(ctx.author.id)

        # Chequear si el archivo existe
        try:
            with open(file_name, "r") as f:
                cars = json.load(f)
        except FileNotFoundError:
            cars = {}

        # Chequear si el usuario ya se encuentra en el archivo
        if user_id not in cars:
            cars[user_id] = []

        # Pedir la foto del auto
        await ctx.author.send("Por favor, envia una foto del auto o escribi 'cancelar' para cancelar el registro:")
        def check_photo(message):
            return message.author == ctx.author and message.attachments
        photo_message = await bot.wait_for("message", check=check_photo)
        if photo_message.content.lower() == "cancelar":
            await ctx.author.send("Registro cancelado.")
            return
        photo = photo_message.attachments[0].url

        # Pedir la ubicación del auto
        await ctx.author.send("Indique en que **ubicación** encontró el auto (Ej: Vicente Lopez, Buenos Aires): ")
        location_message = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        if location_message.content.lower() == "cancelar":
            await ctx.author.send("Registro cancelado.")
            return
        location = location_message.content

        # Pedir la marca del auto
        await ctx.author.send("Indique cual es la **marca** del auto:")
        brand_message = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        if brand_message.content.lower() == "cancelar":
            await ctx.author.send("Registro cancelado.")
            return
        brand = brand_message.content

        # Pedir el modelo del auto
        await ctx.author.send("Indique cual es el **modelo** del auto:")
        model_message = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        if model_message.content.lower() == "cancelar":
            await ctx.author.send("Registro cancelado.")
            return
        model = model_message.content

        # Pedir año del auto, si es que no se especifico patente
        await ctx.author.send("Indique el **año** del auto (Escribi un punto si no lo sabes):")
        year_message = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        if model_message.content.lower() == "cancelar":
            await ctx.author.send("Registro cancelado.")
        if year_message.content == ".":
            pass
        else:
            year = year_message.content

        # Pedir la patente del auto
        await ctx.author.send("Indique la **patente** del auto (Escribi un punto si no la sabes):")
        license_plate_message = await bot.wait_for("message", check=lambda message: message.author == ctx.author)
        if license_plate_message.content.lower() == "cancelar":
            await ctx.author.send("Registro cancelado.")
            return
        license_plate = license_plate_message.content.upper()
        if license_plate_message == ".":
            license_plate = "???"
        if year_message.content == ".":
            year = determine_year(license_plate)
        

        # Generar una ID única para el auto
        car_id = str(uuid.uuid4())
        

        # Almacenar la información en el archivo JSON
        car = {"location": location, 
                "brand": brand, 
                "model": model, 
                "year": year,
                "license_plate": license_plate, 
                "photo": photo,
                "id": car_id,
                }
        cars[user_id].append(car)
        with open(file_name, "w") as f:
            json.dump(cars, f)

        embed = discord.Embed(title=f"{brand} {model}", color=0xffffff)
        embed.set_image(url=car['photo']) # Agregamos la imagen del auto
        embed.add_field(name="Ubicación", value=location, inline=False)
        embed.add_field(name="Marca", value=brand, inline=False)
        embed.add_field(name="Modelo", value=model, inline=False)
        embed.add_field(name="Año", value=year, inline=False)
        embed.add_field(name="Encontrado por", value=f"<@{int(user_id)}>", inline=False)
        embed.set_footer(text=f"{car_id}")
        # Confirmar que la información se ha guardado
        await ctx.author.send("Gracias, el auto ha sido registrado.")
        await ctx.channel.send(embed=embed)
    else:
        await ctx.send("Este comando solo está disponible en el canal <#1072042430079172678>.")

# SHOW COLLECTION COMMAND
@bot.command(name='cars')
async def cars(ctx):
#Find Cars command
    class Cars(menus.ListPageSource):
        async def format_page(self, menu, car):
            embed = discord.Embed(title=f"Coleccion de {bot.get_user(int(user_id))}", color=0xffffff)
            embed.set_image(url=car['photo']) # Agregamos la imagen del auto
            embed.add_field(name="Ubicación", value=car['location'], inline=False)
            embed.add_field(name="Marca", value=car['brand'], inline=False)
            embed.add_field(name="Modelo", value=car['model'], inline=False)
            embed.add_field(name="Año", value=car['year'], inline=False)
            embed.add_field(name="Encontrado por", value=f"<@{int(user_id)}>", inline=False)
            embed.add_field(name="", value=car['id'], inline=False)
            embed.set_footer(text=f"Página {menu.current_page + 1} de {self.get_max_pages()}")
            return embed

    class CarMenu(menus.Menu):
        def __init__(self, source, cars, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cars = cars
            self.source = source
            self.current_page = 0


        async def send_initial_message(self, ctx, channel):
            return await channel.send(embed=await self.source.format_page(self, self.cars[0]))

        @menus.button("\U000025C0")
        async def on_previous(self, payload):
            try:
                self.current_page -= 1
                await self.message.edit(embed=await self.source.format_page(self, self.cars[self.current_page]))
            except IndexError:
                pass

        @menus.button("\U000025B6")
        async def on_next(self, payload):
            try:
                self.current_page += 1
                await self.message.edit(embed=await self.source.format_page(self, self.cars[self.current_page]))
            except IndexError:
                pass

        @menus.button("\U0000274C")
        async def on_cancel(self, payload):
            self.stop()

    if ctx.message.channel.id == 1072041611401375744 or ctx.message.channel.id == 1050205565915234394:
        user_id = str(ctx.message.author.id)
        if ctx.message.mentions:
            mentioned_user = ctx.message.mentions[0]
            user_id = str(mentioned_user.id)
        else:
            mentioned_user = None
        file_name = "spotted_cars.json"

        # Chequear si el archivo existe
        try:
            with open(file_name, "r") as f:
                cars = json.load(f)
        except FileNotFoundError:
            cars = {}

        # Chequear si el usuario ya se encuentra en el archivo
        if user_id in cars and cars[user_id]:
            user = bot.get_user(int(user_id))
            cars = cars[user_id]
            if not cars:
                embed = discord.Embed(title=f"Coleccion de {bot.get_user(int(user_id))}", description="Este usuario no tiene autos en su colección.", color=0xffffff)
                await ctx.channel.send(embed=embed)
            else:
                source = Cars(cars, per_page=1)
                menu = CarMenu(source, cars)
                await menu.start(ctx)
        elif user_id not in cars:
            embed = discord.Embed(title=f"Coleccion de {bot.get_user(int(user_id))}", description="Este usuario no tiene autos en su colección.", color=0xffffff)
            await ctx.channel.send(embed=embed)
        else:
            await ctx.send("Este comando solo está disponible en el canal <#1072041611401375744>.")

# RESET COLLECTION COMMAND
@bot.command(name='reset')
async def reset(ctx):
    user_id = str(ctx.author.id)
    file_name = "spotted_cars.json"
    
    try:
        with open(file_name, "r") as f:
            cars = json.load(f)
    except FileNotFoundError:
        cars = {}
    
    if user_id in cars:
        cars[user_id] = []
        with open(file_name, "w") as f:
            json.dump(cars, f)
        response = f"La colección de autos de {bot.get_user(int(user_id))} ha sido reiniciada."
    else:
        response = f"El usuario {bot.get_user(int(user_id))} no tiene ninguna colección de autos."
    
    await ctx.channel.send(response)

# ADMIN COMMANDS
@bot.command()
@commands.has_role("Owner")
async def embed(ctx):
    from embed import dsEmbed
    await ctx.channel.send(embed=dsEmbed())
    await ctx.message.delete()

@bot.command(name="ping")
@commands.has_role("Owner")
async def embed(ctx):
    await ctx.channel.send("Pong!")

load_dotenv()
bot.run(os.environ["TOKEN"])