import discord
from discord.ext import commands
from requests import get
from urllib import request
from json import load, dump
from bs4 import BeautifulSoup
import subprocess
import os

async def setup(bot):
    await bot.add_cog(Teambuilder(bot))

class Teambuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        print('Successfully unloaded Teambuilder')


    async def load_dict(self, path):
        with open(path, "r") as file:
            data = load(file)
        return data
    
    async def get_formats(self):
        pass


    @commands.group(
        brief="Commands related to the teambuilding process"
    )
    async def team(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Team Subcommands",
                description="pass"
            )
            await ctx.send(embed=embed)


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Creates a new team",
        aliases=['c', 'new', 'n']
    )
    async def create(self, ctx):
        username = ctx.author.name
        path = './json/teams.json'
        data = await self.load_dict(path)
        max_key = 0

        if username in data:
            for key in data[username].keys():
                max_key += 1
            team_number = max_key + 1
        else:
            data[username] = {}
            team_number = 1

        data[username][team_number] = {}
        with open(path, "w") as file:
            dump(data, file, indent=4)

        await ctx.send(f"Blank team {team_number} has been created! Type `p!team view {team_number}` to view team.")


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Deletes an existing team",
        aliases=['d','del']
    )
    async def delete(self, ctx, name):
        self.bot.team_name = name
        self.bot.yes_or_no_check = 0
        username = ctx.author.name
        path = './json/teams.json'
        data = await self.load_dict(path)

        self.bot.data = data
        self.bot.name = username
        self.bot.team = name

        if username in data and name in data[username]:
            self.bot.yes_or_no = await ctx.send(f"Are you sure you want to delete `{name}`?", view=YesOrNo(self.bot))
            with open(path, "w") as file:
                dump(data, file, indent=4)
        else:
            await ctx.send(f"Team `{name}` was not found. Check for any spelling errors.")


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Renames an existing team",
        aliases=['r']
    )
    async def rename(self, ctx, old_name, new_name):
        username = ctx.author.name
        path = './json/teams.json'
        data = await self.load_dict(path)

        if username in data and old_name in data[username]:
            data[username][new_name] = data[username][old_name]
            del data[username][old_name]

            with open(path, "w") as file:
                dump(data, file, indent=4)

            await ctx.send(f"Team `{old_name}` has been renamed to `{new_name}`. Type `p!team view {new_name}` to view team.")
        else:
            await ctx.send(f"Team `{old_name}` was not found. Check for any spelling errors.")


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Fetches info about the requested team",
        aliases=['i', 'info', 'vi']
    )
    async def view(self, ctx, name):
        username = ctx.author.name
        path = './json/teams.json'
        data = await self.load_dict(path)

        if username in data and name in data[username] and data[username][name] != {}:
            pass
        elif username in data and name in data[username] and data[username][name] == {}:
            await ctx.send(f"Team `{name}` is empty! Add members with `p!team add {name}`.")
        else:
            await ctx.send(f"Team `{name}` was not found. Check for any spelling errors.")


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Imports a set from the Showdown! website teambuilder, takes team or member as mode",
        aliases=['import', 'imp']
    )
    async def import_team(self, ctx, mode, file):
        mode = mode.lower()
        match mode:
            case 'team':
                pass
            case 'member':
                pass


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Validates a team given the format",
        aliases=['v', 'format','f']
    )
    async def validate(self, ctx, name, format):
        username = ctx.author.name
        path = './json/teams.json'
        format_path = './json/formats.json'
        data = await self.load_dict(path)
        format_data = await self.load_dict(format_path)

        if username in data and name in data[username]:
            gen = format[:4]
            tier = format[4:]
            if gen in format_data and tier in format_data[gen]:
                wd = os.getcwd()
                os.chdir("C:/Users/smart/pokemon-showdown")
                validate = subprocess.run(["node pokemon-showdown validate-team", f"{format}", f'"{data[username][name]["packed"]}"'])
                os.chdir(wd)
                print(validate.stdout)
            else:
                await ctx.send(f"Format {format} has either not been implemented yet, or does not exist on the site. Check for any spelling errors.")
        else:
            await ctx.send(f"Team `{name}` was not found. Check for any spelling errors.")


    @commands.cooldown(1, 5, commands.BucketType.user)
    @team.command(
        brief="Adds a member to the specified team",
        aliases=['a']
    )
    async def add(self, ctx, name, mon):
        list = await self.get_formats()
        await ctx.send(list)



class YesOrNo(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=90)
        self.bot = bot

    @discord.ui.button(label="Confirm", emoji="👍", style=discord.ButtonStyle.green)
    async def yes(self, interaction, button):
        await self.bot.yes_or_no.edit(view=self, content=f"Successfully deleted `{self.bot.team_name}`.")
        await interaction.response.defer() # makes sure it doesnt say interaction failed
        self.bot.yes_or_no_check = 1
        self.disabled = True

        del self.bot.data[self.bot.name][self.bot.team]
        with open('./json/teams.json', "w") as file:
                dump(self.bot.data, file, indent=4)

    @discord.ui.button(label="Cancel", emoji="👎", style=discord.ButtonStyle.red)
    async def no(self, interaction, button):
        await self.bot.yes_or_no.edit(view=self, content=f"Deletion of `{self.bot.team_name}` has been cancelled.")
        await interaction.response.defer() # makes sure it doesnt say interaction failed
        self.bot.yes_or_no_check = 0
        self.disabled = True