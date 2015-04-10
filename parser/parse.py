#!/usr/bin/env python3
# TODO:
# 1. make it useful lol, flask app etc.
import os
import codecs
import re
import collections
from operator import itemgetter, attrgetter, methodcaller


class Guild:
    def __init__(self):
        self.name = ''
        self.points = 0
        self.kills = 0

class Character:
    def __init__(self):
        self.guild = ''
        self.name = ''
        self.points = 0
        self.kills = 0
        self.deaths = 0
        self.ratio = ''
        self.master = False
        self.defender = False
        self.victims = collections.defaultdict(list)
        self.killedby = collections.defaultdict(list)
        self.awards = []

    def kill(self, other):
        self.victims[self.deaths+1].append((other.guild, other.name))
        self.kills += 1
        other.killedby[other.deaths+1].append((self.guild, self.name))
        other.deaths += 1


def getResults(file):
    guilds = collections.defaultdict(Guild)
    characters = collections.defaultdict(Character)
    
    line1 = re.compile('\[(?P<guild>\w*)\] (?P<master>Guild Master)?' +
                       '(?P<defender>Defender)? (?P<character>\w+)' +
                       '\((?P<points>\d) grade\).*\[(?P<dedguild>\w*)\] ' +
                       '(?P<dedmaster>Guild Master)?(?P<dedfender>Defender)? ' +
                       '(?P<dedcharacter>\w+)')
    # line2 = re.compile('< (Basic Point \+(?P<basic>\d)),?' +
    #                    '( Guild Master Bonus \+(?P<master>\d))?,?' +
    #                    '( Defender Bonus \+(?P<defender>\d))?,?' +
    #                    '( Resurrecting Bonus \+(?P<ress>\d))? >')
    # timeline = {}

    #counter = 0
    with codecs.open(os.path.dirname(os.path.realpath(__file__)) +
                     '/logs/' + file, 'r', 'ascii', 'ignore') as f:
        for line in f:
            if not line.startswith('['):
                continue
            m = line1.match(line)

            guild = m.group('guild')
            if len(guild) < 1:
                guild = 'unnamed guild'            
            dedguild = m.group('dedguild')
            if len(dedguild) < 1:
                dedguild = 'unnamed guild'

            points = m.group('points')
            character = m.group('character')
            dedcharacter = m.group('dedcharacter')
            cg = guilds[guild]
            dg = guilds[dedguild]
            ch = characters[character]
            dh = characters[dedcharacter]

            if m.group('master'):
                ch.master = True
            if m.group('defender'):
                ch.defender = True

            if m.group('dedmaster'):
                dh.master = True
            if m.group('dedfender'):
                dh.defender = True

            # add shit to our results dict
            cg.name = guild
            cg.points += int(points)
            cg.kills += 1
            if not dg.name:
                dg.name = dedguild
            
            ch.guild = guild
            dh.guild = dedguild
            ch.name = character
            dh.name = dedcharacter
            ch.points += int(points)
            ch.kill(dh)
            # well, if i ever need it, it's right here
            # d = line2.match(next(f))
            # timeline[counter] = {
            #    'kchar': character,
            #    'kguild': guild,
            #    'dchar': dedcharacter,
            #    'dguild': dedguild,
            #    'bpoint': d.group('basic'),
            #    'bmaster': d.group('master'),
            #    'bdef': d.group('defender'),
            #    'bress': d.group('ress')
            # }
            #counter += 1
    getRatio(characters)
    sanitizeLists(characters)
    return guilds, characters

def getRatio(ch):
    for char in ch:
        if ch[char].deaths == 0:
            ch[char].ratio = str(round(ch[char].kills / 1.0 , 2))
        else:
            ch[char].ratio = str(round(ch[char].kills / ch[char].deaths, 2))
    return ch

def sanitizeLists(ch):
    for char in ch:
        if ch[char].deaths == 10:
            rangemax = 11
        else:
            rangemax = ch[char].deaths + 2
        for life in range(1,rangemax):
            ch[char].victims[life] = ch[char].victims[life]
            ch[char].killedby[life] = ch[char].killedby[life]
    

def sortedLists(res, ch):
    guildList = sorted(list(res.values()), key=lambda g: g.points, reverse=True)
    playerList = sorted(list(ch.values()), key=lambda p: p.points, reverse=True)
    awards(guildList, playerList, ch, res)
    return guildList, playerList

def awards(guildlist, playerlist, characterdict, guilddict):
    for player in playerlist:
        ch = player
        hunted = []
        if ch.ratio == '1.0':
            ch.awards.append('Balanced')
        if ch.ratio == '0.0':
            ch.awards.append('Pacifist')
        if ch.ratio in ('0.9', '1.1'):
            ch.awards.append('Off Center')
        if any(x in ch.ratio for x in ['.67', '.33']):
            ch.awards.append('Irrational')
        if float(ch.ratio) >= 5.0:
            ch.awards.append('Farmer')
        if float(ch.ratio) == 3.14:
            ch.awards.append('Mmm, pie')
        if ch.kills == 0 and ch.deaths == 10:
            ch.awards.append('Tasty Snack')
        if ch.kills >= 25:
            ch.awards.append('Hoarder')
        if ch.kills >= 50:
            ch.awards.append('Hacker')
        if ch.kills == 1:
            ch.awards.append('One Trick Pony')
        if ch.points == 69:
            ch.awards.append('Hentai')
        if ch.points == 88:
            ch.awards.append('Neo-Nazi')
        if ch.points >= 100:
            ch.awards.append('Triple Digit')
        if 14 <= ch.points <= 17:
            ch.awards.append('Jailbait')
        if ch.deaths < 10 and guildlist[0].name != ch.guild:
            ch.awards.append('Quitter')
            
        for life in ch.victims:
            for vguild, victim in ch.victims[life]:
                if characterdict[victim].master:
                    if not 'Kingslayer' in ch.awards:
                        ch.awards.append('Kingslayer')
                if playerlist[0].name in victim:
                    if not 'Captured the Flag!' in ch.awards:
                        ch.awards.append('Captured the Flag!')
                        
        for life in ch.killedby:
            for hguild, hunter in ch.killedby[life]:
                hunted.append(hguild)
                
        uHunted = set(hunted)
        
        if len(uHunted) == 1 and ch.deaths > 2:
            ch.awards.append('Teamed')
        if ch.points == guilddict[ch.guild].points and ch.kills > 0:
            ch.awards.append('Soloist')
        if ch.defender and ch.deaths == 0:
            ch.awards.append('Steadfast Defender')
        if ch.defender  and ch.kills >= 1:
            ch.awards.append('Offender')
        if ch.deaths == 0:
            ch.awards.append('Steadfast')
        if player == playerlist[0].name:
            ch.awards.append('Most Valuable Player')
        if ch.kills >= 8 and ch.deaths >= 3:
            if len(ch.victims[1]) / ch.kills >= 0.5:
                ch.awards.append('Early Riser')
            if ch.deaths == 10:
                pointer = 10
            else:
                pointer = ch.deaths+1
            if len(ch.victims[pointer]) / int(ch.kills) >= 0.5:
                ch.awards.append('Late Bloomer')

        hunters = collections.defaultdict(lambda: collections.Counter())
        for life in ch.victims:
            for kguild, kchar in ch.victims[life]:
                hunters[kguild][kchar] += 1
                
        for hguild in hunters:
            for hunter in hunters[hguild]:
                hunter2 = hunters[hguild][hunter]
                if hunter2 == 10 and 'Arch Nemesis' not in ch.awards:
                    ch.awards.append('Arch Nemesis')
                    continue
                if hunter2 >= 7 and 'Focused' not in ch.awards:
                    ch.awards.append('Focused')
                    
        if len(ch.awards) >= 5:
            ch.awards.append('Glory Hunter')
            
def confidence(res, ch):
    cRating = 0
    for guild in res:
        if guild in ['Harabas', 'Cosmos', 'ATeam', 'Fusion', 'Exzessiv',
                     'Envy', 'Galaxy', 'Glare', 'MAFIA', 'GentlemanClub',
                     'Invincible', 'Sunlight', 'Judgement', 'BarangayTanod',
                     'Cookies', 'HangOutCrew', 'Nastrand']:
            cRating += 2
        for char in ch:
            if char in ['Gintoki', 'Senpai', 'Filipp', 'Undisputed',
                        'Lippin', 'Franziska', 'koffin', 'LadyLemonade',
                        'Iskander', 'Beardman', 'Dirgantara', 'Igneus',
                        'Falcon', 'Yetti', 'Rapid', 'Lytozz', 'Rampage',
                        'QuizArt', 'PotatoFries', 'poypoy', 'Europe',
                        'kIba', 'PuPpY', 'JuveLeo', 'Alestair', 'Moose',
                        'Amalu', 'lSerenadel', 'Evanz', 'KrystallNatt', 'Duty']:
                cRating += 1
    return cRating
