import discord
from discord.ext import commands
from os import listdir

TOKEN = "TOKEN"
intents = discord.Intents.default()
intents.message_content = True
help_command = commands.DefaultHelpCommand(no_category = 'Misc Commands')


class MyBot(commands.Bot):
    async def setup_hook(self) -> None:
        print(f"Logging in as: {self.user}")

        print("=" * 50)
        print("--- Attempting to load all cogs... --- ")
        for filename in listdir("./cogs"):
            if filename.endswith('.py'):
                print(f"Attempting to load {filename}")
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Successfully loaded {filename}")
        print("=" * 50)
        
        print(f"{self.user} has successfully connected! Use prefix {self.command_prefix}")
        

bot = MyBot(
    command_prefix=commands.when_mentioned_or('p!'),
    intents=intents,
    help_command=help_command
    )

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"p!help | {len(bot.guilds)} servers "))

@bot.command(
    brief="Reloads all cogs",
    description="Reloads all cogs"
)
async def reload(ctx):
    if ctx.author.id == 783032678575243356 or ctx.author.id == 1065824423552225371:
        for filename in listdir("./cogs"):
            if filename.endswith('.py'):
                try:
                    await bot.unload_extension(f'cogs.{filename[:-3]}')
                except:
                    continue
        for filename in listdir("./cogs"):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                await ctx.send(f"Successfully reloaded `{filename}`")

bot.run(TOKEN)

