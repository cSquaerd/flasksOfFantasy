from browser import document, window, html
import browser.widgets.dialog as dialog

def classEdit() -> dialog.Dialog:
	d = dialog.Dialog("Class(es)", ok_cancel = True, default_css = False)
	def toggleLevels(event):
		if event.target.checked:
			del d.select("#levelList")[0].attrs["readonly"]
		else:
			d.select("#levelList")[0].attrs["readonly"] = ''
	
	d.panel <= html.P("Enter one or more classes and corresponding hit dice, separating multiple entries by a comma (,).")

	d.panel <= html.LABEL("Class List:", For = "classList")
	d.panel <= html.INPUT(id = "classList")

	d.panel <= html.P("For the hit dice, write each entry as the number of sides of the associated die (ex. \"6\" for a d6).")

	d.panel <= html.LABEL("Dice List:", For = "diceList")
	d.panel <= html.INPUT(id = "diceList")

	d.panel <= html.P("If you need to edit class levels, enter them here like the dice.")
	d.panel <= html.LABEL("Edit Level(s)?", For = "levelsCheck")
	levelsCheck = html.INPUT(id = "levelsCheck", type = "checkbox")
	levelsCheck.bind("change", toggleLevels)
	d.panel <= levelsCheck
	d.panel <= html.BR()

	d.panel <= html.LABEL("Level List:", For = "levelList")
	d.panel <= html.INPUT(id = "levelList", readonly = '')

	return d

def wheightEdit(heightData, weightData) -> dialog.Dialog:
	d = dialog.Dialog("Edit Weight/Height", ok_cancel = True, default_css = False)

	def setMeasure(event):
		for r in d.select("input[name=\"measure\"]"):
			if r.checked:
				measure = r.value
				break

		if measure == "height":
			dataDict = heightData
		else:
			dataDict = weightData
			
		d.select("#measure")[0].value = dataDict["measure"]
		d.select("#unit")[0].value = dataDict["unit"]

	heightRadio = html.INPUT(
		id = "editHeight", type = "radio", name = "measure", value = "height"
	)
	heightRadio.bind("change", setMeasure)
	d.panel <= heightRadio
	d.panel <= html.LABEL("Height", For = "editHeight")

	weightRadio = html.INPUT(
		id = "editWeight", type = "radio", name = "measure", value = "weight"
	)
	weightRadio.bind("change", setMeasure)
	d.panel <= weightRadio
	d.panel <= html.LABEL("Weight", For = "editWeight")
	d.panel <= html.BR()

	d.panel <= html.LABEL("Measure:", For = "measure")
	d.panel <= html.INPUT(id = "measure", type = "number", min = 0, step = 0.01)
	d.panel <= html.BR()
	d.panel <= html.LABEL("Unit:", For = "unit")
	d.panel <= html.INPUT(id = "unit")

	return d;
	
def levelSet() -> dialog.Dialog:
	d = dialog.Dialog("Set Character Level", ok_cancel = True, default_css = False)

	d.panel <= html.LABEL("Enter your new Character Level (1 -> 20):", For = "newCharLevel")
	d.panel <= html.INPUT(id = "newCharLevel", type = "number", min = 1, max = 20)
	d.panel <= html.BR()

	d.panel <= html.B(
		"Please note that changing your level will set your experience to the minimum required to match."
	)

	return d

def experienceAdjust(method) -> dialog.Dialog:
	if method == "Edit":
		titleString = "Set Experience"
		labelString = "New Total Experience:"
	elif method == "Add":
		titleString = "Add Experience"
		labelString = "Amount of Experience to add:"
	
	d = dialog.Dialog(titleString, ok_cancel = True, default_css = False)

	d.panel <= html.LABEL(labelString, For = "xpAmount")
	d.panel <= html.INPUT(id = "xpAmount", type = "number", min = 0)

	if method == "Edit":
		d.panel <= html.BR()
		d.panel <= html.B(
			"Please note that changing your experience will set your character level to match."
		)

	return d

abilities = (
	"strength", "dexterity", "constitution",
	"intelligence", "wisdom", "charisma"
)

def skillEdit(skill : str) -> dialog.Dialog:
	d = dialog.Dialog(skill, ok_cancel = True, default_css = False)

	d.panel <= html.LABEL("Skill Name:", For = "name")
	d.panel <= html.INPUT(id = "name", Class = "dialogName")
	d.panel <= html.BR()

	for a in abilities:
		d.panel <= html.INPUT(
			id = a + "RB", name = "ability",
			value = a[:3], type = "radio"
		)
		d.panel <= html.LABEL(a.capitalize(), For = a + "RB")
		d.panel <= html.BR()

	return d

def featureEdit(feature : str) -> dialog.Dialog:
	d = dialog.Dialog(feature, ok_cancel = True, default_css = False)
	def toggleNumeric(event):
		if event.target.checked:
			del d.select("#value")[0].attrs["readonly"]
			del d.select("#abilityModCheck")[0].attrs["disabled"]
		else:
			d.select("#value")[0].attrs["readonly"] = ''
			d.select("#abilityModCheck")[0].attrs["disabled"] = ''
			d.select("#abilityModCheck")[0].checked = False
			d.select("#abilityModCheck")[0].dispatchEvent(window.Event.new("change"))

	def toggleAbility(event):
		for a in abilities:
			if event.target.checked:
				del d.select('#' + a + "RB")[0].attrs["disabled"]
			else:
				d.select('#' + a + "RB")[0].attrs["disabled"] = ''
		
		if True not in [r.checked for r in d.select("input[name=\"ability\"]")]:
			d.select("#strengthRB")[0].checked = True
	
	d.panel <= html.LABEL("Feature Name:", For = "name")
	d.panel <= html.INPUT(id = "name", Class = "dialogName")
	d.panel <= html.BR()
	d.panel <= html.LABEL("Feature Description:", For = "desc")
	d.panel <= html.INPUT(id = "description")
	d.panel <= html.BR()

	d.panel <= html.LABEL("Is Numeric?", For = "numericCheck")
	numericCheck = html.INPUT(id = "numericCheck", type = "checkbox")
	numericCheck.bind("change", toggleNumeric)
	d.panel <= numericCheck
	d.panel <= html.LABEL("Modifies Ability Score?", For = "abilityModCheck")
	abilityModCheck  = html.INPUT(id = "abilityModCheck", type = "checkbox", disabled = '')
	abilityModCheck.bind("change", toggleAbility)
	d.panel <= abilityModCheck
	d.panel <= html.BR()

	d.panel <= html.LABEL("Feature Value:", For = "value")
	d.panel <= html.INPUT(id = "value", Type = "number", readonly = '')
	d.panel <= html.BR()

	for a in abilities:
		d.panel <= html.INPUT(
			id = a + "RB", name = "ability",
			value = a[:3], type = "radio", disabled = ''
		)
		d.panel <= html.LABEL(a.capitalize(), For = a + "RB")
		d.panel <= html.BR()

	return d

def itemEdit(item : str) -> dialog.Dialog:
	d = dialog.Dialog(item, ok_cancel = True, default_css = False)
	def toggleWeapon(event):
		for i in d.select(".weapon"):
			if i.type == "radio" or i.type == "checkbox":
				if event.target.checked:
					del i.attrs["disabled"]
				else:
					i.attrs["disabled"] = ''
			elif i.type == "number":
				if event.target.checked:
					del i.attrs["readonly"]
				else:
					i.attrs["readonly"] = ''

	d.panel <= html.LABEL("Item Name:", For = "name")
	d.panel <= html.INPUT(id = "name", Class = "dialogName")
	d.panel <= html.BR()
	d.panel <= html.LABEL("Item Description:", For = "desc")
	d.panel <= html.INPUT(id = "description")
	d.panel <= html.BR()
	d.panel <= html.LABEL("Item Count:", For = "count")
	d.panel <= html.INPUT(id = "count", type = "number", min = 0)
	d.panel <= html.LABEL("Item Weight:", For = "weight")
	d.panel <= html.INPUT(id = "weight", type = "number", min = 0, step = 0.01)
	d.panel <= html.BR()

	d.panel <= html.P("Value")
	d.panel <= html.LABEL("Gold:", For = "gold")
	d.panel <= html.INPUT(id = "gold", type = "number", min = 0)
	d.panel <= html.LABEL("Silver:", For = "silver")
	d.panel <= html.INPUT(id = "silver", type = "number", min = 0, max = 10)
	d.panel <= html.LABEL("Copper:", For = "copper")
	d.panel <= html.INPUT(id = "copper", type = "number", min = 0, max = 10)
	d.panel <= html.BR()

	weaponTitleTag = html.P("Weapon")
	weaponCheck = html.INPUT(id = "weaponCheck", type = "checkbox")
	weaponCheck.bind("change", toggleWeapon)
	weaponTitleTag <= weaponCheck
	weaponTitleTag <= html.LABEL("Is Weapon?", For = "weaponCheck")
	d.panel <= weaponTitleTag

	d.panel <= html.P("Kind")
	d.panel <= html.INPUT(
		id = "weaponTypeSM", Class = "weapon", type = "radio",
		name = "kind", value = "simpleMelee", disabled = ''
	)
	d.panel <= html.LABEL("Simple Melee", For = "weaponTypeSM")
	d.panel <= html.INPUT(
		id = "weaponTypeSR", Class = "weapon", type = "radio",
		name = "kind", value = "simpleRanged", disabled = ''
	)
	d.panel <= html.LABEL("Simple Ranged", For = "weaponTypeSR")
	d.panel <= html.INPUT(
		id = "weaponTypeMM", Class = "weapon", type = "radio",
		name = "kind", value = "martialMelee", disabled = ''
	)
	d.panel <= html.LABEL("Martial Melee", For = "weaponTypeMM")
	d.panel <= html.INPUT(
		id = "weaponTypeMR", Class = "weapon", type = "radio",
		name = "kind", value = "martialRanged", disabled = ''
	)
	d.panel <= html.LABEL("Martial Ranged", For = "weaponTypeMR")
	d.panel <= html.BR()

	d.panel <= html.P("Damage Type")
	d.panel <= html.INPUT(
		id = "damageTypeB", Class = "weapon", type = "radio",
		name = "type", value = "bludgeoning", disabled = ''
	)
	d.panel <= html.LABEL("Bludgeoning", For = "damageTypeB")
	d.panel <= html.INPUT(
		id = "damageTypeP", Class = "weapon", type = "radio",
		name = "type", value = "piercing", disabled = ''
	)
	d.panel <= html.LABEL("Piercing", For = "damageTypeP")
	d.panel <= html.INPUT(
		id = "damageTypeS", Class = "weapon", type = "radio",
		name = "type", value = "slashing", disabled = ''
	)
	d.panel <= html.LABEL("Slashing", For = "damageTypeS")
	d.panel <= html.BR()
	d.panel <= html.INPUT(
		id = "isProficient", Class = "weapon",
		type = "checkbox", disabled = ''
	)
	d.panel <= html.LABEL("Proficient?", For = "isProficient")
	d.panel <= html.INPUT(
		id = "bonusFromSTR", Class = "weapon", type = "radio",
		name = "ability", value = "str", disabled = ''
	)
	d.panel <= html.LABEL("Strength (Melee*)", For = "bonusFromSTR")
	d.panel <= html.INPUT(
		id = "bonusFromDEX", Class = "weapon", type = "radio",
		name = "ability", value = "dex", disabled = ''
	)
	d.panel <= html.LABEL("Dexterity (Ranged*)", For = "bonusFromDEX")
	d.panel <= html.BR()

	d.panel <= html.P("* Finesse weapons can derive from either ability per player choice")

	d.panel <= html.P("Damage Values")
	d.panel <= html.LABEL("Damage Dice Count:", For = "dmgCount")
	d.panel <= html.INPUT(
		id = "dmgCount", Class = "weapon",
		type = "number", min = 0, readonly = ''
	)
	d.panel <= html.LABEL("Damage Dice Value:", For = "dmgDie")
	d.panel <= html.INPUT(
		id = "dmgDie", Class = "weapon",
		type = "number", min = 0, readonly = ''
	)
	d.panel <= html.BR()
	d.panel <= html.LABEL("Damage Bonus:", For = "dmgBonus")
	d.panel <= html.INPUT(
		id = "dmgBonus", Class = "weapon",
		type = "number", min = 0, readonly = ''
	)

	return d
	
def listEntryDelete(item : str, itemType : str) -> dialog.Dialog:
	d = dialog.Dialog("Confirm Deletion", ok_cancel = ("Yes", "No"), default_css = False)

	d.panel <= html.B(
		"Are you sure you want to delete the \"" + item + "\" " + itemType + "?"
	)
	
	return d

def spellTableCreate() -> dialog.Dialog:
	d = dialog.Dialog("Create Spell Table", ok_cancel = True, default_css = False)
	d.panel <= html.P("Select an ability to be the source of magical power:")
	for a in ("intelligence", "wisdom", "charisma"):
		d.panel <= html.INPUT(
			id = a + "`spellTableAbilityRadio", name = "ability", value = a,
			type = "radio"
		)
		d.panel <= html.LABEL(a.capitalize(), For = a + "`spellTableAbilityRadio")
		d.panel <= html.BR()
	
	d.panel <= html.P("Select a class that does not yet have a spell table:")

	return d
