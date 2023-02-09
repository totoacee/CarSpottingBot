import discord
import requests
import json
import uuid
from discord.ext import menus

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} ha iniciado sesión.')
    await client.change_presence(activity=discord.Game(name="$spot - Bot oficial de ARGENTINA CAR SPOTTING"))

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # Hola command
    elif message.content.lower().startswith('hola') and len(message.content.split(' ')) == 1:
        await message.channel.send('Hola!')

    # Clima command
    elif message.content.startswith('$clima'):
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

        await message.channel.send(response)

    #Spot command
    elif message.content.startswith('$spot'):
        file_name = "spotted_cars.json"
        user_id = str(message.author.id)
        
        # Chequear si el archivo existe
        try:
            with open(file_name, "r") as f:
                cars = json.load(f)
        except FileNotFoundError:
            cars = {}
        
        # Chequear si el usuario ya se encuentra en el archivo
        if user_id not in cars:
            cars[user_id] = []
        
        # Pedir la ubicación del auto
        await message.author.send("Indique en que ubicación encontró el auto o escriba 'cancelar' para cancelar el registro:")
        location_message = await client.wait_for("message", check=lambda message: message.author == message.author)
        if location_message.content.lower() == "cancelar":
            await message.author.send("Registro cancelado.")
            return
        location = location_message.content
        
        # Pedir la marca del auto
        await message.author.send("Indique cual es la marca del auto:")
        brand_message = await client.wait_for("message", check=lambda message: message.author == message.author)
        brand = brand_message.content

        # Pedir el modelo del auto
        await message.author.send("Indique cual es el modelo del auto:")
        model_message = await client.wait_for("message", check=lambda message: message.author == message.author)
        model = model_message.content
        
        # Pedir la patente del auto
        await message.author.send("Indique la patente del auto:")
        license_plate_message = await client.wait_for("message", check=lambda message: message.author == message.author)
        license_plate = license_plate_message.content
        
        # Generar una ID única para el auto
        car_id = str(uuid.uuid4())
        
        # Agregar la información del auto al archivo
        car = {
            "id": car_id,
            "location": location,
            "brand": brand,
            "model": model,
            "license_plate": license_plate
        }
        cars[user_id].append(car)
        
        # Guardar el archivo
        with open(file_name, "w") as f:
            json.dump(cars, f, indent=4)
        
        await message.author.send(f"Auto agregado con éxito, ID: {car_id}")
    
@client.event
async def on_message(message: discord.Message):    
    #Find Cars command
    class Cars(menus.ListPageSource):
        async def format_page(self, menu, car):
            embed = discord.Embed(title=f"Auto ID {car['id']}", color=0x00ff00)
            embed.add_field(name="Ubicación", value=car['location'], inline=False)
            embed.add_field(name="Marca", value=car['brand'], inline=False)
            embed.add_field(name="Modelo", value=car['model'], inline=False)
            embed.add_field(name="Patente", value=car['license_plate'], inline=False)
            embed.set_footer(text=f"Página {menu.current_page + 1} de {self.get_max_pages()}")
            return embed

    class CarMenu(menus.Menu):
        def __init__(self, source, cars, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cars = cars
            self.source = source

        async def send_initial_message(self, ctx, channel):
            return await channel.send(embed=self.source.format_page(self, self.cars[0]))

        @menus.button("\U000025C0")
        async def on_previous(self, payload):
            self.current_page -= 1
            await self.message.edit(embed=self.source.format_page(self, self.cars[self.current_page]))

        @menus.button("\U000025B6")
        async def on_next(self, payload):
            self.current_page += 1
            await self.message.edit(embed=self.source.format_page(self, self.cars[self.current_page]))

        @menus.button("\U0000274C")
        async def on_cancel(self, payload):
            self.stop()

    if message.content.startswith('$cars'):
        user_id = str(message.author.id)
    if message.mentions:
        mentioned_user = message.mentions[0]
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
    if user_id in cars:
        user = client.get_user(int(user_id))
        cars = cars[user_id]
        if not cars:
            embed = discord.Embed(title="No hay elementos", description="No hay autos para mostrar", color=0x00ff00)
            await message.channel.send(embed=embed)
        else:
            source = Cars(cars, per_page=1)
            menu = CarMenu(source, cars)
            ctx = await client.get_context(message, cls=discord.ext.commands.Context)
            await menu.start(ctx=ctx)

    #Reset collection command
    elif message.content.startswith('$reset'):
        user_id = str(message.author.id)
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
            response = f"La colección de autos del usuario {client.get_user(int(user_id))} ha sido reiniciada."
        else:
            response = f"El usuario {client.get_user(int(user_id))} no tiene ninguna colección de autos."
        
        await message.channel.send(response)



client.run("MTA1MjAyMDA0OTIwNjA2NzI4MA.GYKmcZ.jrPu7hXyU-lWtj_GL2j1ILFi7GppdY4OXpsNZk")