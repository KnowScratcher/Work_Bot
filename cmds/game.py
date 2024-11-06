from discord import *
from discord.ext import commands
from discord.ui import *
from core.classes import Cog_Extension
from actions import check_new,loading,error
import json
import logging
from collections import defaultdict

players:list["Player"] = {}
default = {
    "locale":"en-us",
    "job":"farmer", # TODO: no use now
    "balance":0,
}

class Player:

    """
    # IMPORTANT
    1. When a new player data key is registered, the following method should be synced
        - `__init__`
        - `sync_data_to_game`
        - `sync_data_to_save`
    2. When a config changes, the following should not be ignored
        1. The change should only be in the object's attribute
        2. The following method should be called
            - `save_data`
    3. Only call `reload_data` when necessary
    4. When a placeholder is added to the translation strings, register it in format_string
    """

    def __init__(self, interaction:Interaction, is_first_join:bool):
        self.uid:int = interaction.user.id
        self.data = {}
        self.dict = {}
        self.init_interaction = interaction # inherit the interaction to get user data

        # keys registration
        self.locale = ""
        self.job = ""
        self.balance = 0

        if is_first_join:
            with open(f"./userdatas/{self.uid}.json","w",encoding="UTF-8") as d:
                self.data = default
        else:
            self.load_data()
            self.fix_data()
            self.sync_data_to_game()
            self.load_translation()
        self.save_data()
        

    def reload_data(self):
        """
        # DANGEROUS
        do not call this if not necessary
        """
        self.load_data()
        self.fix_data()
        self.save_data()
        self.load_translation()

    def load_translation(self) -> dict:
        """
        # Load translation
        load translation for the user's locale
        """
        with open(f"./lang/{self.locale}.json","r",encoding="UTF-8") as translation:
            self.dict = json.load(translation)
    
    def load_data(self) -> dict:
        with open(f"./userdatas/{self.uid}.json","r",encoding="UTF-8") as d:
            self.data = json.load(d)
    
    def sync_data_to_game(self):
        """
        # Sync data to game
        sync data from dict(self.data) to object
        """
        self.locale = self.data["locale"]
        self.job = self.data["job"]
        self.balance = self.data["balance"]

    def sync_data_to_save(self):
        """
        # Sync data to save
        sync data from object to dict(self.data)
        """
        self.data["locale"] = self.locale
        self.data["job"] = self.job
        self.data["balance"] = self.balance

    def save_data(self):
        """
        # Save Data
        this includes
        - syncing object to dict
        - saving
        """
        self.sync_data_to_save()
        with open(f"./userdatas/{self.uid}.json","w",encoding="UTF-8") as d:
            json.dump(self.data,d,indent="\t")
        
    def fix_data(self):
        """
        # Fix data
        put missing keys onto the data using default value
        # Warning
        this doesn't save the data
        """
        for i in default:
            if i not in self.data:
                self.data[i] = default[i]

    def format_string(self,string:str) -> str:
        """
        # Format string
        dynamically format the string
        # IMPORTANT
        when a new placeholder is added, it should be registered here, 
        or it will be replaced with "?"
        """

        formatter = defaultdict(lambda:"?")
        formatter.update({
            "display_name":self.init_interaction.user.display_name,
            "uid":self.init_interaction.user.id,
            "job":self.job,
            })
        return string %formatter

    # pages

    def lang_page(self):
        embed = Embed(title="Please choose a language",description="請選擇語言",color=0x00ff00)
        return embed
    
    def lang_view(self):
        lang_select = Select(placeholder="Click to choose",options=[
            SelectOption(label="繁體中文",emoji="🇹🇼",value="zh-tw"),
            SelectOption(label="English(US)",emoji="🇺🇸",value="en-us"),
            SelectOption(label="English(UK)",emoji="🇬🇧",value="en-uk"),
        ])

        async def select_cb(inter:Interaction):
            if inter.user.id == self.uid:
                self.locale = lang_select.values[0]
                self.save_data()
                self.load_translation()
                embed = self.job_page()
                view = self.job_view()
                await inter.response.edit_message(embed=embed,view=view)
            else:
                await inter.response.send_message(embed=error.no_permission(players[str(inter.user.id)].dict["no_permission"] if str(inter.user.id) in players else "❌You don't have the permission to do that❌"),ephemeral=True)
        lang_select.callback = select_cb
        lang_view = View(timeout=0)
        lang_view.add_item(lang_select)
        return lang_view
    
    def job_page(self):
        embed = Embed(title=self.format_string(self.dict["choose_job"]),color=0x00ff00)
        return embed

    def job_view(self):
        job_select = Select(placeholder=self.dict["click_to_select"],options=[
            SelectOption(label=self.dict["farmer"],emoji="🌾",description=self.dict["farmer_des"],value="farmer")
        ])
        async def select_cb(inter:Interaction):
            if inter.user.id == self.uid:
                self.job = job_select.values[0]
                self.save_data()
                embed = self.home_page()
                view = self.home_view()
                await inter.response.edit_message(embed=embed,view=view)
            else:
                await inter.response.send_message(embed=error.no_permission(players[str(inter.user.id)].dict["no_permission"] if str(inter.user.id) in players else "❌You don't have the permission to do that❌"),ephemeral=True)
        job_select.callback = select_cb
        view = View(timeout=0)
        view.add_item(job_select)
        return view

    def home_page(self):
        embed = Embed(title=self.format_string(self.dict["home"]),color=0x00ff00)
        embed.add_field(name=f"<:pcoin:1011077640733589504>{self.format_string(self.dict['balance'])}",value=self.balance)
        embed.add_field(name=f"⛏️{self.dict['job']}",value=self.dict[self.job])
        # embed.add_field(name=f"")
        return embed

    def home_view(self):
        test = Button(label="Test",style=ButtonStyle.blurple)
        view = View(timeout=0)
        view.add_item(test)
        return view

class Game(Cog_Extension):

    @app_commands.command(name="play",description="play the game")
    async def play(self,interaction:Interaction):
        await interaction.response.send_message(embed=loading.get_loading())
        is_first_join = check_new.check(interaction.user.id)
        if str(interaction.user.id) not in players:
            now_player = players[str(interaction.user.id)] = Player(interaction,is_first_join)
        else:
            now_player = players[str(interaction.user.id)]
        if is_first_join:
            await interaction.edit_original_response(embed=now_player.lang_page(),view=now_player.lang_view())
        else:
            await interaction.edit_original_response(embed=now_player.home_page(),view=now_player.home_view())

        

async def setup(bot):
    await bot.add_cog(Game(bot))
            