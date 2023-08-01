import discord
from discord.ext import commands
from urllib import parse
from requests import get
from json import loads
from datetime import datetime

async def setup(bot):
    await bot.add_cog(Info(bot))

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        print('Successfully unloaded Info')

    async def search_setup(self, old_query):
        query = parse.quote_plus(old_query)
        return query
    
    async def replay_embed_setup(self, ctx, ids : list, formats : list, dates : list, player1, player2):
        self.bot.num = 1
        self.bot.max = len(ids)
        self.bot.pages = {}
        base_replay = "https://replay.pokemonshowdown.com/"
        link_num = 1
        index = 0

        for id in ids:
            index = ids.index(id)
            date = datetime.fromtimestamp(dates[index]).strftime("%m-%d-%Y")
            self.bot.pages[link_num] = discord.Embed(
                title=f"Replay: {player1[index]} vs. {player2[index]}",
                description=f"`Date:` {date} \n`Format:` {formats[index]}",
                url=base_replay+id,
                )
            self.bot.pages[link_num].set_thumbnail(url='https://pokemonshowdown.com/images/icon.png')
            self.bot.pages[link_num].set_footer(text="Created by kaplow. | Requested by {}".format(ctx.author.name))
            link_num += 1

        self.bot.embed = await ctx.send(embed=self.bot.pages[self.bot.num], view=Paginator(self.bot))
            

    async def replay_setup(self, link):
        replay_ids = []
        replay_formats = []
        player_ones = []
        player_twos = []
        replay_dates = []
        replay_json = get(link)
        replay_json = replay_json.text
        replay_data = loads(replay_json)

        for replay in replay_data:
            replay_ids.append(replay['id'])
            replay_formats.append(replay['format'])
            replay_dates.append(replay['uploadtime'])
            player_ones.append(replay['p1'])
            player_twos.append(replay['p2'])

        return replay_ids, replay_formats, replay_dates, player_ones, player_twos
    

    async def pokedex_setup(self, link):
        dex_json = get(link)
        dex_json = dex_json.text
        dex_data = loads(dex_json)

        return dex_data

    async def pokedex_embed_setup(self, ctx, dict, query):
        self.bot.num = 1
        self.bot.max = 2
        self.bot.pages = {}
        types = []
        stats = []
        abilities = []
        measurements = []
        eggs = []
        evo_line = []

        link = "https://dex.pokemonshowdown.com/pokemon/"
        for value in dict[query]['types']:
            types.append(value)
        if len(types) > 1:
            types = f"{types[0]}/{types[1]}"
        else:
            types = types[0]

        for key, value in dict[query]['baseStats'].items():
            stats.append(value)
        stats = f"`HP:` {stats[0]} \n`ATK:` {stats[1]} \n`DEF:` {stats[2]} \n`SPA:` {stats[3]} \n`SPD:` {stats[4]} \n`SPE:` {stats[5]}"

        for key, value in dict[query]['abilities'].items():
            abilities.append(value)
        if len(abilities) == 2:
            abilities = f"{abilities[0]} \n{abilities[1]}"
        elif len(abilities) == 3:
            abilities = f"{abilities[0]} \n{abilities[1]} \n{abilities[2]}"
        else:
            abilities = abilities[0]


        self.bot.pages[1] = discord.Embed(
            title=f"{dict[query]['name']} - #{dict[query]['num']} - {dict[query]['tier']}",
            url=link+query
        )
        self.bot.pages[1].add_field(
            name="Type",
            value=types,
            inline=True
        )
        self.bot.pages[1].add_field(
            name="Ability",
            value=abilities,
            inline=True
        )
        self.bot.pages[1].add_field(
            name="Stats",
            value=stats,
            inline=False
        )
        self.bot.pages[1].set_thumbnail(url=f"https://play.pokemonshowdown.com/sprites/gen5/{dict[query]['name'].lower()}.png")
        self.bot.pages[1].set_footer(text="Created by kaplow. | Requested by {}".format(ctx.author.name))

        measurements = f"{dict[query]['heightm']} m, {dict[query]['weightkg']} kg"
        for value in dict[query]['eggGroups']:
            eggs.append(value)
        if len(eggs) == 2:
            eggs = f"{eggs[0]} \n{eggs[1]}"
        else:
            eggs = eggs[0]

        if ('prevo') in dict[query] and ('evos') in dict[query]:
            if len(dict[query]['evos']) == 1:
                evo_line = f"`Previous:` {dict[query]['prevo']} \n`Next:` {dict[query]['evos'][0]}"
            elif len(dict[query]['evos']) == 2:
                evo_line = f"`Previous:` {dict[query]['prevo']} \n`Next:` {dict[query]['evos'][0]}, {dict[query]['evos'][1]}"   
        elif ('prevo') in dict[query] and ('evos') not in dict[query]:
            evo_line = f"`Previous:` {dict[query]['prevo']}"
        else:
            evo_line = "N/A"


        self.bot.pages[2] = discord.Embed(
            title=f"{dict[query]['name']} - #{dict[query]['num']} - {dict[query]['tier']}",
            url=link+query
        )
        self.bot.pages[2].add_field(
            name="Measurements",
            value=measurements,
            inline=True
        )
        self.bot.pages[2].add_field(
            name="Egg Group",
            value=eggs,
            inline=True
        )
        self.bot.pages[2].add_field(
            name="Evolution Line",
            value=evo_line,
            inline=False
        )
        self.bot.pages[2].set_thumbnail(url=f"https://play.pokemonshowdown.com/sprites/gen5/{dict[query]['name'].lower()}.png")
        self.bot.pages[2].set_footer(text="Created by kaplow. | Requested by {}".format(ctx.author.name))

        self.bot.embed = await ctx.send(embed=self.bot.pages[1], view=Paginator(self.bot))
        



    @commands.group(
        brief="Commands that fetch dex info given search query"
    )
    async def dex(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Pokédex Subcommands",
                description="`Name:` Fetches Pokémon dex info based on name"
            )
            await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @dex.command(
        brief="Fetches Pokémon dex info based on name",
        aliases=['n']
    )
    async def name(self, ctx, *, query):
        dex_dict = {}
        link = "https://play.pokemonshowdown.com/data/pokedex.json"

        dex_dict = await self.pokedex_setup(link)
        await self.pokedex_embed_setup(ctx, dex_dict, query)





    @commands.group(
        brief="Commands that fetch replays given search query"
    )
    async def replay(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Replay Subcommands",
                description="`User:` Fetches replays based on only user(s) \n`Format:` Fetches replays based on only format \n`Battle:` Fetches replays based on format and user(s)"
            )
            await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @replay.command(
        brief="Fetches replays based on only user(s)",
        aliases=['u']
    )
    async def user(self, ctx, player1, player2=None):
        template = "https://replay.pokemonshowdown.com/search.json?user="
        player1 = await self.search_setup(player1)
        if player2==None:
            page_link = f"{template}{player1}" 
        else:
            player2 = await self.search_setup(player2)
            page_link = f"{template}{player1}&user2={player2}"
        replay_ids, replay_formats, replay_dates, player_ones, player_twos = await self.replay_setup(page_link)
        
        await self.replay_embed_setup(ctx, replay_ids, replay_formats, replay_dates, player_ones, player_twos)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @replay.command(
        brief="Fetches replays based on only format",
        aliases=['f']
    )
    async def format(self, ctx, format):
        template = "https://replay.pokemonshowdown.com/search.json?format="
        page_link = template + format

        replay_ids, replay_formats, replay_dates, player_ones, player_twos = await self.replay_setup(page_link)
        
        await self.replay_embed_setup(ctx, replay_ids, replay_formats, replay_dates, player_ones, player_twos)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @replay.command(
        brief="Fetches replays based on format and user(s)",
        aliases=['b', 'uf', 'fu']
    )
    async def battle(self, ctx, player1, player2, format):
        template = "https://replay.pokemonshowdown.com/search.json?user="
        player1 = await self.search_setup(player1)
        player2 = await self.search_setup(player2)
        page_link = f"{template}{player1}&user2={player2}&format={format}"
        replay_ids, replay_formats, replay_dates, player_ones, player_twos = await self.replay_setup(page_link)
        
        await self.replay_embed_setup(ctx, replay_ids, replay_formats, replay_dates, player_ones, player_twos)

    

class Paginator(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=90)
        self.bot = bot

    @discord.ui.button(label="First", emoji="⏪", style=discord.ButtonStyle.blurple)
    async def first(self, interaction, button):
        await self.bot.embed.edit(view=self, embed=self.bot.pages[self.bot.num]) # sends to first page
        self.bot.num = 1
        await interaction.response.defer() # makes sure it doesnt say interaction failed


    @discord.ui.button(label="Previous", emoji="⬅️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction, button):
        self.bot.num -= 1 # sends to previous page
        if self.bot.num < 1: # checks if invalid number
            self.bot.num = 1
        await self.bot.embed.edit(view=self, embed=self.bot.pages[self.bot.num])
        await interaction.response.defer() # makes sure it doesnt say interaction failed


    @discord.ui.button(label="Next", emoji="➡️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction, button):
        self.bot.num += 1 # sends to next page
        if self.bot.num > self.bot.max: # checks if invalid number
            self.bot.num = self.bot.max
        await self.bot.embed.edit(view=self, embed=self.bot.pages[self.bot.num])
        await interaction.response.defer() # makes sure it doesnt say interaction failed
        

    @discord.ui.button(label="Last", emoji="⏩", style=discord.ButtonStyle.blurple)
    async def last(self, interaction, button):
        await self.bot.embed.edit(view=self, embed=self.bot.pages[self.bot.max]) # sends to last page
        self.bot.num = self.bot.max
        await interaction.response.defer() # makes sure it doesnt say interaction failed