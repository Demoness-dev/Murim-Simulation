from sect import Sect
from martial_artist_definition import MartialArtist
from battle_manager import manage_brackets
import uuid
from console_writer import log
class sect_battle:
    def __init__(self, sect1:Sect, sect2:Sect):
        self.Battle_id = uuid.uuid4() 
        self.sect1 = sect1
        self.sect2 = sect2
        self.duel_lists = {}
        self.battle_log = {}
    
    def choose_combatants(self):
        sect1_artists = self.sect1.sect_members
        sect2_artists = self.sect2.sect_members
        
        sect1_combatants = self.generate_combatants(sect1_artists, 20)
        sect2_combatants = self.generate_combatants(sect2_artists, 20)

        return sect1_combatants, sect2_combatants
    
    def generate_combatants(self, combatant_dict:dict, number:int):
        return dict(sorted(combatant_dict.items(), key=lambda item: item[1].qi, reverse=True)[:number])
    
    def create_brackets(self, s1_c:dict, s2_c:dict):
        for sect1_combatant, sect2_combatant in zip(s1_c.values(), s2_c.values()):
            self.duel_lists[sect1_combatant] = sect2_combatant
            temporary_dict = {
                sect1_combatant.name: sect1_combatant,
                sect2_combatant.name: sect2_combatant
            }
            battle = manage_brackets(temporary_dict, "Killing")
            self.write_battle_winner(battle)
            
            
    def write_battle_winner(self, battle_result:MartialArtist):
        self.battle_log[battle_result.name] = {"Sect Winner": battle_result.sect, "Artist": battle_result}
    
    def finish_battle(self):
        sect1_wins = 0
        sect2_wins = 0
        for battle in self.battle_log.values():
            if battle["Sect Winner"] == self.sect1.city_name:
                sect1_wins += 1
            elif battle["Sect Winner"] == self.sect2.city_name:
                sect2_wins += 1
        if sect1_wins == sect2_wins:
            return "Draw"
        return self.sect1 if sect1_wins > sect2_wins else self.sect2
    
    def battle(self):
        sect1_combatants, sect2_combatants = self.choose_combatants()
        self.create_brackets(sect1_combatants, sect2_combatants)
        winner = self.finish_battle()
        if winner == "Draw":
            log.info("The battle ended in a draw. No sect got any territory.")
            return
        log.info(f"The battle ended. The winner is {winner}.")
        #FIRST REWRITE THE MAP AND TRADE SYSTEM TO BE COMPATIBLE WITH THE SECT WAR SYSTEM.
        