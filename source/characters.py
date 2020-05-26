import skills

def ssprint(Msg):
    print(f'    {Msg}\n')

class Character:
    def __init__(self):
        self.name = 'N/A'
        self.familyName = ''
        self.title = 'N/A'
        self.species = 'N/A'
        self.rank = 'N/A'
        self.level = 1
        self.divineProtection = 'N/A'
        self.info = 'N/A'
        self.appearance = 'N/A'
        self.status = 'N/A'

        self.inventoryCapacity = 0

        # Game variables
        self.storyProgress = [None]
        self.savePath = ''
        self.textDelay = True
        self.lastCommand = ''

        # For predator
        self.amount = 0
        self.addAmount = 1
        self.capacityUse = 0

        self.attributes = {
            'Ultimate Skill' : {},
            'Unique Skill' : {},
            'Special Skill' : {},
            'Extra Skill' : {},
            'Intrinsic Skill' : {},
            'Common Skill' : {},
            'Daily Skill' : {},
            'Composite Skill' : {},
            'Resistance' : {},
            'Attribute' : {},
            'Manas' : {},
            }

        self.inventory = {
            'Items' : {},
            'Material' : {},
            'Potions' : {},
            'Misc' : {},
        }

    # ========== Info
    def SetName(self, inpName, character):
        character.name = inpName

    def StartState(self):
        for i in self.startState:
            self.AddAttribute(i, output=False)

    def UpdateInfo(self):
        self.info = f"""
    Name: {self.name} {self.familyName}
    Title: {self.title}
    Species: {self.species}
    Rank: {self.rank}
    Status: {self.status}
    Divine Protection: {self.divineProtection}

    Appearance:
        {self.appearance}
        """

        # Sets ranking according to level
        ranking = ['Special S', 'S', 'Special A' ,'A+', 'A', 'A-', 'B', 'C', 'D', 'E', 'F']
        self.rank = ranking[self.level-1]

    def ShowInfo(self, usrInp, character=None):
        generators = [*self.AttributesGenerator(), *self.InventoryGenerator(), *self.MimicGenerator()]
        # Adds mimicked monster abilities 
        if rimuru.mimicObject:
            generators.extend(self.AttributesGenerator(rimuru.mimicObject))

        try:
            for i in generators:
                if i.name.lower() == usrInp.lower():
                    print(i.info)
        except: pass

    def UpdateRanking(self, level):
        self.level = level
        self.UpdateInfo()
        ssprint(f"<Leveled up to rank {self.rank}>")

    # ========== Attack
    def CheckResistance(self, checkResist, character=None):
        # Checks if character has resistance attribute
        for resistName, resistObject in character.attributes['Resistance'].items():
            for resist in resistObject.resistTypes:
                if resist.lower() == checkResist.lower():
                    return True
                    break

    def CanAttack(self, attack, target=None):
        attacked = attackSuccess = False
        if attack == '':
            return False, False
        generators = [*self.AttributesGenerator(self.mimicObject)]
        if rimuru.mimicObject:
            generators.extend(self.AttributesGenerator(rimuru.mimicObject))

        for i in generators:
            if attack == i.name.lower():
                if not self.CheckResistance(i.damageType, target):
                    if target.level <= i.damageLevel:
                        attackSuccess = attacked = True
                        break
                    else:
                        ssprint("<Target is too high of a level for that attack.>")
                        attacked = True
                        break
                else:
                    ssprint(f'<<Note, target has resistance to {i.damageType}.>>')
                    attacked = True
                    break
        return attacked, attackSuccess


    # ========== Predator Functions
    def MimicGenerator(self):
        for lvl, lvlList in self.attributes['Unique Skill']['Mimic'].mimics.items():
            for name in lvlList:
                yield name

    def AddMimicry(self, character):
        self.attributes['Unique Skill']['Mimic'].mimics[character.rank].append(character)
        ssprint(f'<<Note, new mimicry available: {character.name}.>>')

    def CanMimic(self, character):
        if character == 'reset':
            self.mimic = 'Slime'
            self.mimicObject = None
            self.attributes['Unique Skill']['Mimic'].active = False
            ssprint("<Mimicry Reset>")
        else:
            for i in self.MimicGenerator():
                if character == i.name.lower():
                    self.mimic = i.name
                    self.mimicObject = i
                    self.attributes['Unique Skill']['Mimic'].active = True
                    ssprint(f'<Now Mimicking: {i.name}>')
                    break


    # ========== Attribute Functions
    def AttributesGenerator(self, target=None, output=False):
        character = self.attributes
        if target:
            character = target.attributes

        for skillType, skills in character.items():
            # Only shows yields skill type if skill list is not empty
            if output and skills:
                yield(f'{skillType}:')

            for skillName, skillObject in skills.items():
                if output: 
                    if skillObject.active:
                        yield(f'\t{skillName} (Active)')
                    elif skillObject.passive:
                        yield(f'\t{skillName} (Passive)')
                    else:
                        yield(f'\t{skillName}')
                else: 
                    yield(skillObject)

    def ShowAttributes(self, character=None):
        if not character:
            character = rimuru
            showMimic = True
        else:
            showMimic = False
            # Get stats for other monsters
            for i in self.MimicGenerator():
                if i.name.lower() == character.lower():
                    character = i

        print(f"""
-----Attributes/Skills-----
Name: {character.name} {character.familyName}
""")
        for i in self.AttributesGenerator(character, output=True):
            print(i)

        # Only shows mimicry info when not looking at stats of other monsters or in mimicry
        if self.mimicObject and showMimic:
            print("\n-----Mimicry-----")
            print(f"Mimicking: {self.mimic}\n")
            for j in self.AttributesGenerator(self.mimicObject, True):
                print(j)


    def AddAttribute(self, item, output=True):
        try:
            self.attributes[item.skillLevel][item.name]
        except:
            self.attributes[item.skillLevel][item.name] = item
            if output:
                try: 
                    ssprint(item.acquiredMsg)
                except: pass

    def RemoveAttribute(self, skill):
        try:
            del self.attributes[skill.skillLevel][skill.name]
        except:
            print("ERROR Deleting attribute. If you're seeing this message, please let developer know")

    def SkillUpgrade(self, skillFrom, skillTo):
        self.RemoveAttribute(skillFrom)
        ssprint(f'<<{skillFrom.skillLevel} [{skillFrom}] evolving to {skillTo.skillLevel} [{skillTo}]...>>')
        self.AddAttribute(skillTo)


    # ========== Inventory Functions
    def InventoryGenerator(self, output=False):
        for itemType, items in self.inventory.items():
            if output and items:
                yield(f'{itemType}:')
            for itemName, itemObject in items.items():
                if output:
                    yield(f'\t{self.inventory[itemType][itemName].amount}x {itemObject.name}')
                else: 
                    yield(itemObject)

    def ShowInventory(self):
        print('\n-----Inventory-----')
        print(f'Capacity: {self.inventoryCapacity}%\n')
        for i in self.InventoryGenerator(True):
            print(i)

    def AddInventory(self, item):
        try:
            self.inventory[item.itemType][item.name].amount += item.addAmount
        except:
            self.inventory[item.itemType][item.name] = item
            self.inventory[item.itemType][item.name].amount += item.addAmount
        self.inventoryCapacity += item.capacityUse
        ssprint(item.AcquiredMsg() + f' | Total: {self.inventory[item.itemType][item.name].amount}>')
        ssprint(f'<Inventory Capacity: {self.inventoryCapacity:.2f}%>')

    def RemoveInventory(self, item):
        try:
            self.inventory[item.itemType].remove(item)
        except:
            ssprint(f'<Error deleting {item.name} from inventory>')



#                    ========== Characters ==========
class Rimuru_Tempest(Character):
    def __init__(self):
        Character.__init__(self)
        self.name = 'Slime'
        self.mimic = 'Slime'
        self.level = 7
        self.mimicObject = None
        self.startState = [skills.Predator_Mimicry_Skill(), skills.Self_Regeneration(), skills.Absorb_Dissolve(), 
                    skills.Resist_Pain(), skills.Resist_Melee(), skills.Resist_Electricity(), skills.Resist_Temperature()]
        self.UpdateInfo()


class Veldora_Tempest(Character):
    def __init__(self):
        Character.__init__(self)
        self.name = "Veldora"
        self.title = 'Storm Dragon'
        self.species = 'True Dragon'
        self.status = 'Alive'
        self.level = 11
        self.itemType = 'Misc'
        self.capacityUse = 10
        self.UpdateInfo()

    def AcquiredMsg(self):
        self.UpdateInfo()
        return(f"<<Acquired Veldora {self.familyName}>>")

# ========== Low Level
class Tempest_Serpent(Character):
    def __init__(self):
        Character.__init__(self)
        self.name = 'Tempest Serpent'
        self.Species = 'Tempest Serpent'
        self.level = 6
        self.appearance = 'The snake has a large, jet-black body with thorned scales and tough skin.'
        
        self.startState = [skills.Sense_Heat_Source(), skills.Poisonous_Breath()]
        self.StartState()
        self.UpdateInfo()


# ========== Rimuru
rimuru = None
def UpdateCharacter(character):
    global rimuru
    rimuru = character
    return rimuru
veldora = Veldora_Tempest()
