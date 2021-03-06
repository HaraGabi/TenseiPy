import os, pickle
from time import sleep

import chapters.tensei_1 as tensei1
import characters as c

usrInpDebug = False

#                    ========== Game Input ==========
def RunFuncs(msg, actions, funcs, attackFail=None):
    if usrInpDebug: 
        usrInp = actions[0][0]
    else:
        # Adds () around actions, (*action)
        options = ', '.join('(' + i + ')' for i in msg)
        mimic = c.rimuru.mimicking
        try:
            targets, = ', '.join([(i.name if i.alive else f'{i.name}(Dead)') for i in c.rimuru.focusTargets]), 
        except: targets = None

        if targets:
            #print(f'\nTarget:', str(targets))
            print(f'\nTarget: {targets}\nActions:', options, f'| {mimic}, (stats, inv, help)')
        else:
            print("\nActions:", options, f'| {mimic}, (stats, inv, help)')
        usrInp = input("\n> ").lower()
        print()

    loop = True
    attacked = attackSuccess = skillSuccess = False
    # Get info on skills, times, etc
    splitInput = ' '.join(usrInp.split()[1:])
    gameActions = {
            'info': c.rimuru.ShowInfo,
            'stats': c.rimuru.ShowAttributes,
            'target': c.rimuru.SetTarget,
            'predate': c.rimuru.PredateTarget,
            'mimic': c.rimuru.CanMimic, 
            }

    for k, v in gameActions.items():
        if k in usrInp:
            v(splitInput)

    if 'use' in usrInp:
        skillSuccess = c.rimuru.UseSkill(splitInput)
    if 'attack' in usrInp:
        attacked, attackSuccess = c.rimuru.CanAttack(splitInput)
    try: pass
    except: pass

    # If action has *, continues story
    for i in range(len(funcs)):
        contAction = ''
        for j in actions[i]:
            try:
                contAction = msg[i][0]
            except: pass
           # Checks if valid command
            if usrInp.lower() == j.lower():
               # Checks if command continues story
                if contAction == '*':
                    funcs[i]()
                    loop = False
                    c.rimuru.lastCommand = usrInp
                    break
                else:
                    funcs[i]()
                    c.rimuru.lastCommand = usrInp
        if skillSuccess:
            funcs[0]()
            loop = False
        elif attacked and not attackSuccess:
            attackFail()
        elif attacked and attackSuccess:
            funcs[0]()
            loop = False

        if not loop: break
    else: 
        RunFuncs(msg, actions, funcs, attackFail)

def ActionMenu(msg, actions, funcs, attackFail=None):
    actions.extend([['help'], ['inv'], ['exit']])
    funcs.extend([ShowHelp, c.rimuru.ShowInventory, ExitGame])
    RunFuncs(msg, actions, funcs, attackFail)

def ShowHelp():
    print("""
    Commands:
        target TARGET(s)            -- Target commands and abilities. E.g. 'target tempest serpent'
        attack <TARGET> with SKILL  -- Attack target(s) (if not already targeting) with skill(s). E.g. 'attack with water blade', 'attack tempest serpent with water blade'
          - Multiple targets and/or attacks separated by comma. E.g. 'attack tempest serpent, black spider with water blade, poisonous breath'
        use SKILL(s)                -- Use skill/items. E.g. 'use sense heat source'
        stats                       -- Show yours skills and resistances. 
          - stats TARGET            -- Stats for monsters you have predated. E.g. 'stats tempest serpent'
        inv                         -- Show inventory.
        info                        -- Show info on skill, item or character. E.g. 'info great sage, 'info hipokte grass', 'info tempest serpent'
                                       NOTE: To get info on skills from a monster, have to be mimicking corresponding monster. E.g. 'info sense heat source'
        help                        -- Show this help page.
        exit                        -- Exit game.

    Abilities:
        mimic ___                   -- Mimics appearance of of predated. E.g. 'mimic tempest serpent'
          - info mimic              -- Shows available mimicries.
          - mimic reset             -- Resets mimic (Back to slime)
        predate                     -- Predate target(s). Can only be used while you have target(s) command. E.g. 'predate'
        
    Game Dialogue:
        ~Message~                   -- Telepathy
        *Message*                   -- Story progression
        <Message>                   -- Acquired item, information, etc
        <<Message>>                 -- Great Sage (Raphael, Ciel)
        <<<Message>>>               -- Voice of the World

    HUD:
        Target: Currently Focused Target(s)
        Actions: (ACTION(s)) | MIMIC, (Extra Actions)
      E.g.
        Target: Giant Bat, Black Spider
        Actions: (*Attack), (*Move on) | Tempest Serpent, (stats, inv, help)

    Level/Ranking:
       Level      Rank         Risk
        11.     Special S   Catastrophe
        10.     S           Disaster
        9.      Special A   Calamity
        8.      A+          Tragedy
        7.      A           Hazard
        6.      A-          Danger
        5.      B           Pro
        4.      C           Advance
        3.      D           Intermediate
        2.      E           Beginner
        1.      F           Novice
    """)

# If have attribute or inventory item
def CheckHas(item):
    if c.rimuru.Generators(item):
        return True

# Checks if mob is alive
def CheckStatus(target):
    try:
        for i in c.rimuru.currentMobs:
            if target.lower() in i.GetName():
                return True
    except: pass

# Add mob(s) to game
def AddMob(mob):
    if type(mob) == list:
        for i in mob:
            mob = c.rimuru.Generators(i, new=True)
            if mob:
                c.rimuru.currentMobs.append(mob)
    else:
        c.rimuru.currentMobs.append(c.rimuru.Generators(mob, new=True))

def NewName(name, character):
    c.rimuru.SetName(name, character)


#                    ========== Extra ==========
def ExitGame():
    exit()

def TBC():
    print("---TO BE CONTINUED---")
    input("Press Enter to exit > ")


#                    ========== Game Saves ==========
def LoadGame(path):
    global rimuru
    try:
        rimuru = pickle.load(open(path, 'rb'))
        print("Loaded Player Save\n")
    except: 
        rimuru = c.Rimuru_Tempest()
    return rimuru

def SaveGame(rimuru):
    pickle.dump(rimuru, open(c.rimuru.savePath, 'wb'))
    print("Game Saved To: player_save.p")

def DeleteGame(rimuru):
    try:
        os.remove(rimuru.savePath)
        print("Resetting Game. Deleted player_save.p")
    except: pass

def ContinueStory(rimuru, nextChapter):
    print("Continue to next chapter?")
    usrInp = input("Y/N > ")
    c.rimuru.storyProgress.append(nextChapter)
    SaveGame(rimuru)
    if usrInp.lower() == 'y':
        nextChapter(rimuru)
    else: exit()

#                    ========== Game Functions ==========
def StartBanner():
    print("\n----------Tensei Shitara Slime Datta Ken (That Time I Got Reincarnated as a Slime)----------\n")
    instructions = """
    NOTE: 
    - Set window size for ASCII art accordingly (Fullscreen recommended)
    - Access help, inventory and skills with help, inv and stats
    - * actions continues story (do NOT actually input *, or ()). Try the other actions first maybe, see what happens
    - Delete player_save.p to reset game progress (includes player inventory and skills)
    """
    print(instructions)
    c.rimuru.ShowAttributes()
    c.rimuru.ShowInventory()
    print()

# ========== Printing
def sprint(Msg):
    msgLen = len(str(Msg))
    if c.rimuru.textDelay:
        if msgLen > 100:
            sTime = 1
        elif msgLen > 70 and msgLen > 80:
            sTime = 4
        elif msgLen > 50 and msgLen > 40:
            sTime = 3
        elif msgLen > 40 and msgLen > 20:
            sTime = 2
        elif msgLen < 10:
            sTime = 2
        elif msgLen < 5:
            sTime = 1
        else: sTime = 1
    else:
        sTime = 0

    print(Msg, '\n')
    sleep(sTime)

def ssprint(Msg):
    sprint(f'    {Msg}')

if __name__ == '__main__':
    # Get file path depending on Windows or not
    savePath = os.path.dirname(os.path.abspath(__file__)) + '/player_save.p'

    rimuru = c.UpdateCharacter(LoadGame(savePath))
    rimuru.savePath = savePath
    StartBanner()

    print("\nDisable text delay? (Recommend leaving enabled for easier reading)")
    setSleep = str(input("(Y)es/(N)o > "))
    if setSleep.lower() in ['yes', 'y']:
        print("Text Delay: DISABLED")
        rimuru.textDelay = False
    else:
        print("Text Delay: ENABLED")
    sleep(1)
    print("\n\n")

    rimuru.storyProgress[0] = tensei1.Chapter1
    rimuru.storyProgress[-1](rimuru)
