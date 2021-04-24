import datetime
import json
from discord.ext import commands
from requests import get


class RandomThings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.place = 'Moscow'

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        for guild in self.guilds:
            print(
                f'{self.user} подключились к чату:\n'
                f'{guild.name}(id: {guild.id})')

    async def on_message(self, message):
        if message.author == self.user:
            return
        else:
            await message.channel.send('Введите /help_bot для справки.')

    @commands.command(name='exit')
    async def exit(self, ctx):
        await self.bot.logout()

    @commands.command(name='place')
    async def place(self, ctx, word):
        self.place = word.capitalize()
        await ctx.send('Place changed to {}'.format(word))

    @commands.command(name='current')
    async def current(self, ctx):
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + self.place + "&format=json"
        response = get(geocoder_request)
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        x, y = toponym_coodrinates.split()
        # x, y = '55.75396', '37.620393'
        url = 'https://api.weather.yandex.ru/v2/forecast'
        apiheaders = {'X-Yandex-API-Key': 'f82463f5-b42a-454d-8827-30f5c0933cd8'}
        wparams = {'lat': x, 'lon': y, 'lang': 'ru_RU', 'limit': '1', 'hours': 'false', 'extra': 'false'}
        req = get(url, headers=apiheaders, params=wparams).json()
        with open("last_request.json", "w") as write_file:
            json.dump(req, write_file)
        data = req['fact']
        text = 'Current weather in {} today {} at time {}:\n'.format(self.place,
                                                                     datetime.datetime.today().strftime("%d-%m-%Y"),
                                                                     datetime.datetime.today().strftime("%H:%M"))
        text += 'Temperature: {};\n'.format(data['temp'])
        text += 'Pressure: {} mm;\n'.format(data['pressure_mm'])
        text += 'Humidity: {}%;\n'.format(data['humidity'])
        text += '{},\n'.format(data['condition'].capitalize())
        text += 'Wind {}, {} m/s.'.format(data['wind_dir'], data['wind_speed'])

        await ctx.send(str(text))

    @commands.command(name='forecast')
    async def forecast(self, ctx, days):
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + self.place + "&format=json"
        response = get(geocoder_request)
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        x, y = toponym_coodrinates.split()
        # x, y = '55.75396', '37.620393'
        url = 'https://api.weather.yandex.ru/v2/forecast'
        apiheaders = {'X-Yandex-API-Key': 'f82463f5-b42a-454d-8827-30f5c0933cd8'}
        if int(days) > 7:
            days = 7
        wparams = {'lat': x, 'lon': y, 'lang': 'ru_RU', 'limit': int(days), 'hours': 'false', 'extra': 'false'}
        req = get(url, headers=apiheaders, params=wparams).json()
        with open("last_request.json", "w") as write_file:
            json.dump(req, write_file)
        text = ''
        for data in req['forecasts']:
            text += 'Weather forecast in {} for {}:\n'.format(self.place, data['date'])
            text += 'Temperature: {};\n'.format(data['parts']['day']['temp_avg'])
            text += 'Pressure: {} mm;\n'.format(data['parts']['day']['pressure_mm'])
            text += 'Humidity: {}%;\n'.format(data['parts']['day']['humidity'])
            text += '{},\n'.format(data['parts']['day']['condition'].capitalize())
            text += 'Wind {}, {} m/s.\n'.format(data['parts']['day']['wind_dir'], data['parts']['day']['wind_speed'])
            text += '\n'

        await ctx.send(str(text))

    @commands.command(name='help_bot')
    async def stop(self, ctx):
        await ctx.send("""/place - задает место прогноза
        # /place {place}
    /current - присылает сообщение о текущей погоде
        # /current
    /forecast - сообщает прогноз дневной температуры и осадков на указанное количество дней
        # /forecast {days}""")


bot = commands.Bot(command_prefix='/')
bot.add_cog(RandomThings(bot))
TOKEN = "ODMxMTY1MzE4Nzg0NjE0NDIw.YHRRBg.WisH7vsUwyAu1o3xDSeQaEU9UG4"
bot.run(TOKEN)
