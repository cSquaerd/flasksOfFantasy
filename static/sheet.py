# IMPORTS
from browser import document, html, window
import browser.widgets.dialog as dialog
from common import *
from sheetDialog import *
import json

# GLOBAL VARS
data = {}
sheetName = document["sheetName"]["content"]

# CONSTANTS
bioCompoundFields = ("class", "height", "weight")
abilityTranslator = {
	"str": "strength",
	"dex": "dexterity",
	"con": "constitution",
	"int": "intelligence",
	"wis": "wisdom",
	"cha": "charisma"
}
coins = ("gold", "silver", "copper")
goldPieceSign = "\u20B2"
levelsAndEXPRequired = {
	1: 0,
	2: 300,
	3: 900,
	4: 2700,
	5: 6500,
	6: 14000,
	7: 23000,
	8: 34000,
	9: 48000,
	10: 64000,
	11: 85000,
	12: 100000,
	13: 120000,
	14: 140000,
	15: 165000,
	16: 195000,
	17: 225000,
	18: 265000,
	19: 305000,
	20: 355000,
	21: float("inf")
}

# BIOGRAPHY FUNCTIONS
def toggleEditing(event, group):
	for field in document.select("input." + group):
		#print(field)
		if group == "bio" and field.attrs["id"] in bioCompoundFields:
			continue
		elif group == "ac":
			if event.target.checked:
				document["armorClass`ShowBase"].checked = True
				document["armorClass`ShowBase"].attrs["disabled"] = ''
			else:
				del document["armorClass`ShowBase"].attrs["disabled"]

			#print("in toggleEditing, firing input event to Show Base AC checkbox...")
			document["armorClass`ShowBase"].dispatchEvent(
				window.Event.new("change")
			)
		if event.target.checked:
			del field.attrs["readonly"]
		else:
			field.attrs["readonly"] = ''
	#print(data["biography"])

def setBioData(event):
	#print(event.target.parentElement.parentElement.id, event.target.id)

	groupKey = event.target.parentElement.parentElement.id
	fieldKey = event.target.id
	data[groupKey][fieldKey] = document[fieldKey].value

document["biographyEdit"].bind("change", lambda e : toggleEditing(e, "bio"))
for field in document.select("input.bio"):
	if field.id not in bioCompoundFields:
		#print(field.id)
		document[field.id].bind("input", setBioData)

def levelSyncCheck():
	if data["experience"]["level"]["character"] != \
		sum(data["experience"]["level"]["classes"].values()):
		dialog.InfoDialog(
			"Level Inequality Notice",
			"The sum of your class level(s) is not equal to your character level. Please make sure to check this and resynchronize it manually."
		)

def adjustClass(event):
	editClassDialog = classEdit()
	editClassDialog.select("#classList")[0].value = ", ".join(
		data["biography"]["class"]
	)
	editClassDialog.select("#diceList")[0].value = ", ".join(
		[str(data["hit"]["dice"][c]["die"]) for c in data["biography"]["class"]]
	)
	editClassDialog.select("#levelList")[0].value = ", ".join(
		[
			str(data["experience"]["level"]["classes"][c])
			for c in data["biography"]["class"]
		]
	)
	if event.target.id == "classLevelsEdit":
		editClassDialog.select("#levelsCheck")[0].checked = True
		editClassDialog.select("#levelsCheck")[0].dispatchEvent(
			window.Event.new("change")
		)

	def okHandler(event):
		classListString = editClassDialog.select("#classList")[0].value
		diceListString = editClassDialog.select("#diceList")[0].value
		levelListString = editClassDialog.select("#levelList")[0].value

		classList = list(map(str.strip, classListString.split(',')))
		diceList = list(map(str.strip, diceListString.split(',')))
		levelList = list(map(str.strip, levelListString.split(',')))

		try:
			diceList = list(map(int, diceList))
		except ValueError:
			dialog.InfoDialog(
				"Value Error",
				"Dice entries must be integers!"
			)
			return
		
		try:
			levelList = list(map(int, levelList))
		except ValueError:
			dialog.InfoDialog(
				"Value Error",
				"Level entries must be integers!"
			)
			return

		if len(classList) != len(diceList):
			dialog.InfoDialog(
				"Mismatch Error",
				"Number of classes not equal to number of dice!"
			)
			return
		elif len(classList) != len(levelList):
			dialog.InfoDialog(
				"Mismatch Error",
				"Number of classes not equal to number of levels!"
			)
			return
		
		data["biography"]["class"] = sorted(classList)
		data["hit"]["dice"] = {
			c: {
				"die": diceList[classList.index(c)],
				"count": levelList[classList.index(c)]
			}
			for c in classList
		}
		data["experience"]["level"]["classes"] = {
			c: levelList[classList.index(c)]
			for c in classList
		}

		levelSyncCheck()
		editClassDialog.close()
		reloadValues()

	editClassDialog.ok_button.bind("click", okHandler)

document["classEdit"].bind("click", adjustClass)

# ABILITY SCORE FUNCTIONS
def calculateAbilityBonus(score : int) -> int:
	return (score - 10) // 2

def syncAbilityScore(ability : str, newValue : int):
	newBonus = calculateAbilityBonus(newValue)

	data["abilities"][ability]["score"] = newValue
	document[ability].value = newValue

	data["abilities"][ability]["bonus"] = newBonus
	document[ability + "Bonus"].value = newBonus

	refreshArmorDisplay()

def adjustAbilityScore(event):
	ability = event.target.id.split('`')[0]
	function = event.target.id.split('`')[1]
	oldValue = data["abilities"][ability]["score"]

	if function == "Increment":
		if oldValue + 1 <= 30:
			newValue = oldValue + 1
		else:
			return
	elif function == "Decrement":
		if oldValue - 1 > 0:
			newValue = oldValue - 1
		else:
			return
	elif function == "Set":
		newValueDialog = dialog.EntryDialog(
			"Set " + ability.capitalize(),
			"Enter a score value between 1 and 30 inclusive"
		)
		def entryHandler(e):
			newValue = newValueDialog.value
			newValueDialog.close()
			#print("In Set Handler")
			try:
				newValue = int(newValue)
				if newValue > 0 and newValue <= 30:
					syncAbilityScore(ability, newValue)
				else:
					dialog.InfoDialog(
						"Ability Set Error",
						"Value out of range of 1 to 30!"
					)
			except ValueError:
				dialog.InfoDialog(
					"Ability Set Error",
					"Could not parse value as integer!"
				)

		newValueDialog.bind("entry", entryHandler)
		return
	else:
		return

	syncAbilityScore(ability, newValue)

def toggleAbilityAdjustment(event):
	for button in document.select(".abilityButton"):
		if event.target.checked:
			del button.attrs["disabled"]
		else:
			button.attrs["disabled"] = ''
		#print(button)

document["abilitiesEdit"].bind("change", toggleAbilityAdjustment)

for button in document.select(".abilityButton"):
	#print(button)
	button.bind("click", adjustAbilityScore)

# DICE STRING FUNCTIONS
def makeDieDict(count : int, die : int) -> dict:
	return {"count": count, "die": die}

def makeDieString(count : int, die : int) -> str:
	return str(count) + 'd' + str(die)

def makeDiceString(dieDictionaries : list) -> str:
	return " + ".join([makeDieString(die["count"], die["die"]) for die in dieDictionaries])

# HIT POINT FUNCTIONS
def updateHitDiceDivs():
	for div in document.select("div.hitDiceDiv"):
		del document[div.id]
	for k in sorted(data["hit"]["dice"].keys()):
		inputID = k + "`HitDice"
		div = html.DIV(id = inputID + "Div", Class = "hitDiceDiv")
		div <= html.LABEL(k, For = inputID)
		div <= html.INPUT(
			id = inputID, value = makeDieString(
				data["hit"]["dice"][k]["count"],
				data["hit"]["dice"][k]["die"]
			), readonly = ''
		)
		document["hitDice"] <= div

def toggleHitAdjustment(event):
	for button in document.select(".hitButton"):
		if event.target.checked:
			del button.attrs["disabled"]
		else:
			button.attrs["disabled"] = ''

	if event.target.checked:
		del document["currentHit`Value"].attrs["readonly"]
	else:
		document["currentHit`Value"].attrs["readonly"] = ''

document["hitEdit"].bind("change", toggleHitAdjustment)

def refreshHitPointBounds():
	document["currentHit`Value"].min = -data["hit"]["max"]
	document["currentHit`Value"].max = data["hit"]["max"]

def syncHitPoints(field, newValue):
	if field == "currentHit":
		field = "currentHit`Value"
	document[field].value = newValue
	field = field.split("Hit")[0]
	data["hit"][field] = newValue

	if field == "max":
		refreshHitPointBounds()
		newCurrent = min(data["hit"]["max"], data["hit"]["current"])
		document["currentHit`Value"].value = newCurrent
		data["hit"]["current"] = newCurrent

def adjustHitPoints(event):
	field = event.target.id.split('`')[0]
	method = event.target.id.split('`')[1]
	fieldKeyword = field.split("Hit")[0]
	oldValue = data["hit"][fieldKeyword]

	if method == "Increment":
		if field == "maxHit" or field == "currentHit" \
			and oldValue + 1 <= data["hit"]["max"]:
			newValue = oldValue + 1
		else:
			newValue = oldValue
	elif method == "Decrement":
		if field == "maxHit" or field == "currentHit" \
			and oldValue - 1 >= -data["hit"]["max"]:
			newValue = oldValue - 1
		else:
			newValue = oldValue
	elif method == "Value":
		try:
			newValue = int(event.target.value)
			data["hit"]["current"] = newValue
			return
		except ValueError:
			dialog.InfoDialog(
				"Hit Point Error",
				"Please only enter integers in the current hit points field."
			)
			event.target.value = data["hit"]["current"]
			return
	elif method == "Set":	
		newValueDialog = dialog.EntryDialog(
			"Set " + fieldKeyword.capitalize() + " Hit Points",
			"Enter a new " + fieldKeyword + " hit points value"
		)
		def entryHandler(e):
			newValue = newValueDialog.value
			try:
				newValue = int(newValue)
				if newValue < 1 and field == "maxHit":
					dialog.InfoDialog(
						"Hit Points Set Error",
						"Max Hit Points Must Be Positive & Non-Zero!"
					)
				elif newValue < -data["hit"]["max"]:
					dialog.InfoDialog(
						"Hit Point Set Error",
						"Current Hit Points Cannot Fall That Far!"
					)
				elif field == "maxHit" or field == "currentHit" \
					and newValue <= data["hit"]["max"]:
					newValueDialog.close()
					syncHitPoints(field, newValue)
				else:
					dialog.InfoDialog(
						"Hit Points Set Error",
						"Current Hit Points Cannot Exceed Maximum!"
					)
			except ValueError:
				dialog.InfoDialog(
					"Hit Points Set Error",
					"Could not parse value as integer!"
				)

		newValueDialog.bind("entry", entryHandler)
		return
	else:
		newValue = oldValue
	syncHitPoints(field, newValue)

for button in document.select(".hitButton"):
	button.bind("click", adjustHitPoints)

document["currentHit`Value"].bind("input", adjustHitPoints)

def processDeathSaves(event):
	kind = event.target.id.split('`')[0]
	count = int(event.target.id.split('`')[1])

	#print(kind + str(count), "disabled" in document[kind + '`' + str(count)].attrs)

	if count < 3:
		if event.target.checked:
			try:
				del document[kind + '`' + str(count + 1)].attrs["disabled"]
			except KeyError:
				pass

		else:
			document[kind + '`' + str(count + 1)].attrs["disabled"] = ''
			for box in range(count + 1, 4):
				document[kind + '`' + str(box)].checked = False
			count -= 1
	elif not event.target.checked:
			count -= 1
	
	if kind == "success":
		kind += "es"
	else:
		kind += 's'

	data["hit"]["deathSaves"][kind] = count
	#print(data["hit"]["deathSaves"])

for box in document.select(".deathSaveCheckbox"):
	box.bind("change", processDeathSaves)

# EXPERIENCE FUNCTIONS
def determineLevel() -> int:
	level = 0
	while data["experience"]["total"] >= levelsAndEXPRequired[level + 1]:
		level += 1
	return level

def setLevel(event):
	levelSetDialog = levelSet()

	def okHandler(event):
		try:
			newCharacterLevel = int(levelSetDialog.select("#newCharLevel")[0].value)
			if newCharacterLevel < 1 or newCharacterLevel > 20:
				dialog.InfoDialog("Value Error", "Please enter a number from 1 to 20.")
				return
			data["experience"]["level"]["character"] = newCharacterLevel
			data["experience"]["total"] = levelsAndEXPRequired[
				newCharacterLevel
			]
			data["experience"]["next"] = levelsAndEXPRequired[
				newCharacterLevel + 1
			]
			levelSyncCheck()
			levelSetDialog.close()
			reloadValues()
		except ValueError:
			dialog.InfoDialog("Value Error", "Please enter an integer number.")
	
	levelSetDialog.ok_button.bind("click", okHandler)

document["characterLevelSet"].bind("click", setLevel)
document["classLevelsEdit"].bind("click", adjustClass)

def adjustExperience(event):
	method = event.target.id.split('`')[1]

	addExperienceDialog = experienceAdjust(method)

	def okHandler(event):
		try:
			newXP = int(addExperienceDialog.select("#xpAmount")[0].value)
			if newXP < 0:
				dialog.InfoDialog("Value Error", "Experience must be non-negative!")
				return
			if method == "Add":
				data["experience"]["total"] += newXP
			elif method == "Edit":
				data["experience"]["total"] = newXP

			data["experience"]["level"]["character"] = determineLevel()
			data["experience"]["next"] = levelsAndEXPRequired[
				data["experience"]["level"]["character"] + 1
			]

			levelSyncCheck()
			addExperienceDialog.close()
			reloadValues()
		except ValueError:
			dialog.InfoDialog("Value Error", "Please enter an integer.")

	addExperienceDialog.ok_button.bind("click", okHandler)

document["experience`Add"].bind("click", adjustExperience)
document["experience`Edit"].bind("click", adjustExperience)

def updateClassLevelDivs():
	for div in document.select("div.classLevelDiv"):
		del document[div.id]
	for k in sorted(data["experience"]["level"]["classes"].keys()):
		inputID = k + "`ClassLevel"
		div = html.DIV(id = inputID + "Div", Class = "classLevelDiv")
		div <= html.LABEL(k, For = inputID)
		div <= html.INPUT(
			id = inputID,
			value = data["experience"]["level"]["classes"][k],
			readonly = ''
		)
		document["classLevels"] <= div

# ARMOR CLASS FUNCTIONS
def refreshArmorDisplay():
	if data["armorType"] == "light" or data["armorType"] == "unarmored":
		document["armorClass`Value"].value = data["armorClass"] + ( \
			data["abilities"]["dexterity"]["bonus"] \
			if not document["armorClass`ShowBase"].checked \
			else 0
		)
	elif data["armorType"] == "medium":
		document["armorClass`Value"].value = data["armorClass"] + ( \
			min(data["abilities"]["dexterity"]["bonus"], 2) \
			if not document["armorClass`ShowBase"].checked \
			else 0
		)
	elif data["armorType"] == "heavy":
		document["armorClass`Value"].value = data["armorClass"]
	elif data["armorType"] == "unarmoredB":
		document["armorClass`Value"].value = data["armorClass"] + ( \
			data["abilities"]["dexterity"]["bonus"] \
			+ data["abilities"]["constitution"]["bonus"] \
			if not document["armorClass`ShowBase"].checked \
			else 0
		)
	elif data["armorType"] == "unarmoredM":
		document["armorClass`Value"].value = data["armorClass"] + ( \
			data["abilities"]["dexterity"]["bonus"] \
			+ data["abilities"]["wisdom"]["bonus"] \
			if not document["armorClass`ShowBase"].checked \
			else 0
		)
	#elif data["armorType"] == "mage":
	#	document["armorClass`Value"].value = (
	#		13 + data["abilities"]["dexterity"]["bonus"] \
	#		if not document["armorClass`ShowBase"].checked \
	#		else data["armorClass"]
	#	)
	else:
		print("Uh oh, something's wrong with the AC subroutines...")

def updateArmor(event):
	method = event.target.id.split('`')[1]

	if method == "Type":
		data["armorType"] = event.target.id.split('`')[0]
	elif method == "Value":
		try:
			data["armorClass"] = int(event.target.value)
		except ValueError:
			dialog.InfoDialog(
				"Armor Class Error",
				"Please only enter integers in the AC field."
			)

	refreshArmorDisplay()

document["armorClass`Value"].bind("input", updateArmor)
document["armorClass`Edit"].bind("change", lambda e : toggleEditing(e, "ac"))
document["armorClass`ShowBase"].bind("change", lambda e : refreshArmorDisplay())

for r in document.select("input[name=\"armor\"]"):
	r.bind("input", updateArmor)

# CURRENCY FUNCTIONS
document["currencyEdit"].bind("change", lambda e : toggleEditing(e, "currency"))

def makeCoinString(coinDict : dict) -> str:
	return '.'.join(
		[
			goldPieceSign + str(coinDict["gold"]),
			str(coinDict["silver"]) + str(coinDict["copper"])
		]
	)

def refreshCurrencyTotal():
	document["currencyTotal"].value = makeCoinString(data["currency"])

def exchangeCoins(event):
	try:
		amount = int(event.target.value)
	except ValueError:
		dialog.InfoDialog(
			"Currency Error", "Please only enter integers in the currency fields."
		)
		event.target.value = data["currency"][event.target.id]
		return

	data["currency"][event.target.id] = int(event.target.value)

	if event.target.id == "gold" or amount < 10:
		refreshCurrencyTotal()
		return
	else:
		event.target.value = 0

	if event.target.id == "silver":
		data["currency"]["silver"] = 0
		data["currency"]["gold"] += 1
	elif event.target.id == "copper":
		data["currency"]["copper"] = 0
		data["currency"]["silver"] += 1
		if data["currency"]["silver"] == 10:
			data["currency"]["silver"] = 0
			data["currency"]["gold"] += 1
	
	reloadValues()

document["gold"].bind("input", exchangeCoins)
document["silver"].bind("input", exchangeCoins)
document["copper"].bind("input", exchangeCoins)

# PROFICIENCIES FUNCTIONS
def calculateProficiencyBonus(level : int) -> int:
	return (level - 1) // 4 + 2

def adjustSkill(event):
	skill = event.target.id.split('`')[0]
	method = event.target.id.split('`')[2]
	creatingSkill = False

	if method == "New":
		creatingSkill = True
		method = "Edit"

	if method == "Delete":
		deleteSkillDialog = listEntryDelete(skill, "skill")

		def deleteHandler(event):
			del data["proficiency"]["skills"][skill]
			deleteSkillDialog.close()
			updateSkillsTable()

		deleteSkillDialog.ok_button.bind("click", deleteHandler)

	elif method == "Edit":
		editSkillDialog = skillEdit(skill)

		if not creatingSkill:
			editSkillDialog.select("#name")[0].value = skill
			editSkillDialog.select(
				"#" + abilityTranslator[data["proficiency"]["skills"][skill]] + "RB"
			)[0].checked = True
		else:
			editSkillDialog.select("#strengthRB")[0].checked = True

		def okHandler(event):
			newSkillName = editSkillDialog.select("#name")[0].value
			newSkillAbility = ''
			for r in editSkillDialog.select("input[name=\"ability\"]"):
				if r.checked:
					newSkillAbility = r.value
					break

			if newSkillAbility == '':
				dialog.InfoDialog(
					"Radio Button Error",
					"Couldn't detect an ability, this shoulnd't be happening!"
				)
				return

			if newSkillName != skill \
				and newSkillName in data["proficiency"]["skills"].keys():
				dialog.InfoDialog(
					"Name Error",
					"A skill already exists with that name, please enter another one."
				)
				return

			data["proficiency"]["skills"][newSkillName] = newSkillAbility
			if newSkillName != skill and not creatingSkill:
				del data["proficiency"]["skills"][skill]

			editSkillDialog.close()
			updateSkillsTable()

		editSkillDialog.ok_button.bind("click", okHandler)

document["Create Skill``New"].bind("click", adjustSkill)

def updateSkillsTable():
	proficiencyBonus = calculateProficiencyBonus(
		data["experience"]["level"]["character"]
	)
	for row in document.select("tr.skillRow"):
		del document[row.id]
	for k in sorted(data["proficiency"]["skills"]):
		inputID = k + "`Skill"
		ability = data["proficiency"]["skills"][k]
		row = html.TR(id = inputID + "`Row", Class = "skillRow")

		row <= html.TD(k)

		skillData = html.TD()
		skillBold = html.B(ability.upper())
		skillData <= skillBold
		row <= skillData

		skillData = html.TD()
		skillValue = html.INPUT(
			id = inputID + "`Value",
			value = data["abilities"][abilityTranslator[ability]]["bonus"] \
				+ proficiencyBonus,
			Type = "number", readonly = ''
		)
		skillData <= skillValue
		row <= skillData

		skillSettings = html.TD()

		skillEditButton = html.INPUT(
			id = inputID + "`Edit", Class = "skillButton",
			type = "button", value = "Edit"
		)
		skillEditButton.bind("click", adjustSkill)
		skillSettings <= skillEditButton
		skillDeleteButton = html.INPUT(
			id = inputID + "`Delete", Class = "skillButton",
			type = "button", value = "Delete"
		)
		skillDeleteButton.bind("click", adjustSkill)
		skillSettings <= skillDeleteButton

		row <= skillSettings

		document["skills"] <= row

# FEATURE FUNCTIONS
def adjustFeature(event):
	feature = event.target.id.split('`')[0]
	method = event.target.id.split('`')[2]
	creatingFeature = False

	if method == "New":
		creatingFeature = True
		method = "Edit"

	if method in ("Decrement", "Increment"):
		if method == "Decrement":
			changeValue = -1
		elif method == "Increment":
			changeValue = 1
		
		data["features"][feature]["value"] += changeValue
		document[feature + "`Feature`Value"].value = data["features"][feature]["value"]

	elif method == "Value":
		try:
			data["features"][feature]["value"] = int(
				document[feature + "`Feature`Value"].value
			)
		except ValueError:
			dialog.InfoDialog(
				"Feature Value Error",
				"Please only enter integers in the feature value fields."
			)
			document[feature + "`Feature`Value"].value = data["features"][feature]["value"]

	elif method == "Delete":
		deleteFeatDialog = listEntryDelete(feature, "feature")

		def deleteHandler(event):
			del data["features"][feature]
			deleteFeatDialog.close()
			updateFeaturesTable()

		deleteFeatDialog.ok_button.bind("click", deleteHandler)
		
	elif method == "Edit":
		editFeatDialog = featureEdit(feature)
		if not creatingFeature:
			editFeatDialog.select("#name")[0].value = feature
			editFeatDialog.select(
				"#description"
			)[0].value = data["features"][feature]["description"]

			if data["features"][feature]["type"] == "numeric":
				editFeatDialog.select("#numericCheck")[0].checked = True
				del editFeatDialog.select("#value")[0].attrs["readonly"]
				editFeatDialog.select(
					"#value"
				)[0].value = data["features"][feature]["value"]

		def okHandler(event):
			newFeatureName = editFeatDialog.select("#name")[0].value
			if newFeatureName != feature \
				and newFeatureName in data["features"].keys():
				dialog.InfoDialog(
					"Name Error",
					"A feature already exists with that name, please choose another one."
				)
				return
			#print("Everything checks out.")

			newFeatureDescription = editFeatDialog.select(
				"#description"
			)[0].value
			newFeatureType = editFeatDialog.select("#numericCheck")[0].checked
			if newFeatureType:
				newFeatureValue = editFeatDialog.select("#value")[0].value
				try:
					newFeatureValue = int(newFeatureValue)
				except ValueError:
					dialog.InfoDialog(
						"Value Error",
						"The feature's value must be an integer number. Please correct it."
					)
					return

				newFeature = {
					"description": newFeatureDescription,
					"type": "numeric",
					"value": newFeatureValue
				}
			else:
				newFeature = {
					"description": newFeatureDescription,
					"type": "written"
				}

			data["features"][newFeatureName] = newFeature
			if newFeatureName != feature and not creatingFeature:
				del data["features"][feature]
			editFeatDialog.close()
			updateFeaturesTable()

		editFeatDialog.ok_button.bind("click", okHandler)

document["Create Feature``New"].bind("click", adjustFeature)
document["featuresEdit"].bind("change", lambda e : toggleEditing(e, "featureValue"))

def updateFeaturesTable():
	for row in document.select("tr.featureRow"):
		del document[row.id]
	for k in sorted(data["features"].keys()):
		inputID = k + "`Feature"
		row = html.TR(id = inputID + "`Row", Class = "featureRow")
		row <= html.TD(k)
		row <= html.TD(data["features"][k]["description"])

		numericCell = html.TD()
		if data["features"][k]["type"] == "numeric":
		#	decrementButton = html.INPUT(
		#		id = inputID + "`Decrement", Class = "featureButton",
		#		type = "button", value = "-"
		#	)
		#	decrementButton.bind("click", adjustFeature)
		#	numericCell <= decrementButton

			numericCell <= html.INPUT(
				id = inputID + "`Value", Class = "featureValue",
				value = data["features"][k]["value"],
				type = "number", readonly = ''
			)
			numericCell.bind("input", adjustFeature)

		#	incrementButton = html.INPUT(
		#		id = inputID + "`Increment", Class = "featureButton",
		#		type = "button", value = "+"
		#	)
		#	incrementButton.bind("click", adjustFeature)
		#	numericCell <= incrementButton

		row <= numericCell

		featSettings = html.TD()

		featEditButton = html.INPUT(
			id = inputID + "`Edit", Class = "featureButton",
			type = "button", value = "Edit"
		)
		featEditButton.bind("click", adjustFeature)
		featSettings <= featEditButton
		featDeleteButton = html.INPUT(
			id = inputID + "`Delete", Class = "featureButton",
			type = "button", value = "Delete"
		)
		featDeleteButton.bind("click", adjustFeature)
		featSettings <= featDeleteButton

		row <= featSettings

		document["features"] <= row

# INVENTORY FUNCTIONS
def adjustItem(event):
	item = event.target.id.split('`')[0]
	method = event.target.id.split('`')[2]
	creatingItem = False

	if method == "New":
		creatingItem = True
		method = "Edit"

	if method == "Edit":
		weaponTypeTranslator = {
			"simpleMelee": "SM",
			"simpleRanged": "SR",
			"martialMelee": "MM",
			"martialRanged": "MR"
		}
		editItemDialog = itemEdit(item)
		if not creatingItem:
			editItemDialog.select("#name")[0].value = item
			for k in ("description", "count", "weight"):
				editItemDialog.select('#' + k)[0].value = data["inventory"][item][k]
			for coin in coins:
				editItemDialog.select('#' + coin)[0].value = \
					data["inventory"][item]["value"][coin]
			if "weapon" in data["inventory"][item].keys() \
				and data["inventory"][item]["weapon"]["kind"] != "none":
				editItemDialog.select("#weaponCheck")[0].checked = True
				editItemDialog.select("#weaponCheck")[0].dispatchEvent(
					window.Event.new("change")
				)
				editItemDialog.select(
					"#weaponType" + weaponTypeTranslator[
						data["inventory"][item]["weapon"]["kind"]
					]
				)[0].checked = True
				editItemDialog.select(
					"#damageType" + \
						data["inventory"][item]["weapon"]["damage"]["type"][0].upper()
				)[0].checked = True
				for k in ("count", "value", "bonus"):
					editItemDialog.select("#dmg" + k.capitalize())[0].value = \
						data["inventory"][item]["weapon"]["damage"][k]				
		else:
			for k in ("count", "weight"):
				editItemDialog.select('#' + k)[0].value = 0
			for coin in coins:
				editItemDialog.select('#' + coin)[0].value = 0
			editItemDialog.select("#weaponTypeSM")[0].checked = True
			editItemDialog.select("#damageTypeB")[0].checked = True
			for i in ("#dmgDiceCount", "#dmgDiceValue", "#dmgBonus"):
				editItemDialog.select(i)[0].value = 0

		def okHandler(event):
			print("Foo")

		editItemDialog.ok_button.bind("click", okHandler)

document["Create Item``New"].bind("click", adjustItem)

def makeDamageString(damageDict : dict) -> str:
	return str(damageDict["count"]) + 'd' + str(damageDict["die"]) \
		+ " + " + str(damageDict["bonus"]) + ' ' + damageDict["type"] \
		+ " (" + str(damageDict["count"] + damageDict["bonus"]) + '-' \
		+ str(damageDict["count"] * damageDict["die"] + damageDict["bonus"]) + ')'

def updateItemsTable():
	for row in document.select("tr.itemRow"):
		del document[row.id]
	for k in sorted(data["inventory"].keys()):
		inputID = k + "`Item"
		row = html.TR(id = inputID + "`Row", Class = "itemRow")
		row <= html.TD(k)
		row <= html.TD(data["inventory"][k]["description"])

		itemCountCell = html.TD()
		itemCountCell <= html.INPUT(
			id = inputID + "`Count", Class = "itemNumericCell",
			value = data["inventory"][k]["count"],
			type = "number", min = 0, readonly = ''
		)
		row <= itemCountCell

		itemWeightCell = html.TD()
		itemWeightCell <= html.INPUT(
			id = inputID + "`Weight", Class = "itemNumericCell",
			value = data["inventory"][k]["weight"],
			type = "number", min = 0, step = 0.01, readonly = ''
		)
		row <= itemWeightCell

		itemValueCell = html.TD()
		itemValueCell <= html.INPUT(
			id = inputID + "`Value", readonly = '',
			value = makeCoinString(data["inventory"][k]["value"]),
		)
		row <= itemValueCell

		if "weapon" in data["inventory"][k].keys():
			row <= html.TD(data["inventory"][k]["weapon"]["kind"])
			row <= html.TD(
				makeDamageString(data["inventory"][k]["weapon"]["damage"])
			)
		else:
			row <= html.TD(colspan = 2)

		itemSettingsCell = html.TD()

		itemEditButton = html.INPUT(
			id = inputID + "`Edit", Class = "itemButton",
			type = "button", value = "Edit",
		)
		itemEditButton.bind("click", adjustItem)
		itemSettingsCell <= itemEditButton
		
		itemDeleteButton = html.INPUT(
			id = inputID + "`Delete", Class = "itemButton",
			type = "button", value = "Delete",
		)
		itemDeleteButton.bind("click", adjustItem)
		itemSettingsCell <= itemDeleteButton

		row <= itemSettingsCell

		document["items"] <= row

# GENERAL/NETWORK/OTHER FUNCTIONS
def reloadValues():
	global data
	for k in data["biography"].keys():
		#print(k, data["biography"][k], sep = ": ")
		if k not in ("class", "height", "weight"):
			document[k].value = data["biography"][k]
			#print("(regular)")
		elif k == "class":
			document[k].value = ", ".join(data["biography"][k])
			#print("(class)")
		else:
			document[k].value = str(data["biography"][k]["measure"]) \
				+ ' ' + data["biography"][k]["unit"]
			#print("(height/weight)")

	#print(data["hit"]["deathSaves"])

	for k in data["abilities"].keys():
		document[k].value = data["abilities"][k]["score"]
		document[k + "Bonus"].value = data["abilities"][k]["bonus"]

	document["currentHit`Value"].value = data["hit"]["current"]
	document["maxHit"].value = data["hit"]["max"]
	refreshHitPointBounds()

	updateHitDiceDivs()

	try:
		del document["success`1"].attrs["disabled"]
	except KeyError:
		pass
	for box in range(1, data["hit"]["deathSaves"]["successes"] + 1):
		if document["success`" + str(box)].checked:
			break
		document["success`" + str(box)].checked = True
		if box < 3:
			del document["success`" + str(box + 1)].attrs["disabled"]

	try:
		del document["failure`1"].attrs["disabled"]
	except KeyError:
		pass
	for box in range(1, data["hit"]["deathSaves"]["failures"] + 1):
		if document["failure`" + str(box)].checked:
			break
		document["failure`" + str(box)].checked = True
		if box < 3:
			del document["failure`" + str(box + 1)].attrs["disabled"]

	document["characterLevel"].value = data["experience"]["level"]["character"]
	document["currentExperience"].value = data["experience"]["total"]
	document["nextExperience"].value = data["experience"]["next"]
	updateClassLevelDivs()

	#document["armorClass`Value"].value = data["armorClass"]
	for r in document.select("input[name=\"armor\"]"):
		if r.id.split('`')[0] == data["armorType"]:
			r.checked = True
			r.dispatchEvent(window.InputEvent.new("input"))
			break
	#refreshArmorDisplay()

	refreshCurrencyTotal()
	for coin in coins:
		document[coin].value = data["currency"][coin]

	data["proficiency"]["bonus"] = calculateProficiencyBonus(
		data["experience"]["level"]["character"]
	)
	document["proficiency"].value = data["proficiency"]["bonus"]
	updateSkillsTable()

	updateFeaturesTable()

	updateItemsTable()

def jsonHandler(response):
	global data
	if response.status == 200:
		data = ajaxParseJSON(response)
		reloadValues()
	else:
		dialogShowHTTPError(response)

def saveSheet(event):
	ajaxPostJSON(
		"save/", data,
		lambda r : sheetReplyGeneric(
			r, {
				"noErrorTitle": "Sheet Saved",
				"noErrorBody": "Your sheet was saved successfully.",
				"errorTitle": "E R R O R"
			},
			()
		)
	)

document["save"].bind("click", saveSheet)

# INITIAL FETCH OF SHEET DATA
downloadSheetRequest(PseudoEvent(" `" + sheetName), jsonHandler)

