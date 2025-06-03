import math
import json
import io
import os
import sys
import platform
import time

from pathlib import Path
from time import monotonic

from textual import log, events
from textual.app import App, ComposeResult
from textual.content import Content
from textual.message import Message
from textual.containers import Middle, HorizontalGroup, VerticalGroup, VerticalScroll, Center, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Button, Rule, Digits, Footer, Header, Static, Label

appStateDir = ""
userHome = Path.home()
CANSAVE = False

if (platform.system() == "Windows"):
	USRAPPDATA = os.getenv('LOCALAPPDATA')
	appStateDir = f"{USRAPPDATA}/tuxbux"
elif (platform.system() == "Linux"):
	appStateDir = f"{userHome}/.local/state/tuxbux"
else:
	appStateDir = ""

if appStateDir and not ( os.access(appStateDir, os.F_OK) ):
	try:
		os.mkdir(appStateDir)
	except OSError:
		appStateDir = ""

if appStateDir:
	# try:
	# 	os.access(appStateDir, os.R_OK)
	SAVEPATH=f"{appStateDir}/savedata.json"
else:
	SAVEPATH = ""

if SAVEPATH and appStateDir:
	try:
		Path(SAVEPATH).touch()
	except OSError as error:
		print(error)

if SAVEPATH:
	try:
		with open(SAVEPATH, "r") as file:
			CANSAVE = True
	except OSError:
			CANSAVE = False

if SAVEPATH and CANSAVE:
	with open(SAVEPATH, "r") as openfile:
		try:
			LOADED_APP_SAVE_DATA = json.load(openfile)
		except json.decoder.JSONDecodeError:
			LOADED_APP_SAVE_DATA = {}
else:
	LOADED_APP_SAVE_DATA = {}

class Shop(VerticalScroll):
	"""The shop."""

	def compose(self) -> ComposeResult:
		"""Create child purchasables."""
		yield ShopEntry("Low-tier VPS", shopID=1, color="red", description="You scroll through lowendbox.com and decide to humor yourself. Surely, a gigabyte of ram should do the trick.", price=12, priceMod=1, cps=1, isVisible=True)
		yield ShopEntry("Mid-range VPS", shopID=2, color="orange", description="Hey, this one's got multiple cpu's!", price=250, priceMod=1, cps=8)
		yield ShopEntry("High-end VPS", shopID=3, color="yellow", description="Tux's penguin wings give this VM a few extra TeraFLOPS.", price=1000, priceMod=1, cps=72)
		yield ShopEntry("Dedicated Server Box", shopID=4, color="green", description="Nothing like a bare metal box to call home.", price=2500, priceMod=1, cps=256)
		yield ShopEntry("Herd of Linux Boxen", shopID=5, color="blue", description="After much contemplation, a scrupulous graybeard had found you worthy to inherit his commendable fleet. With a hefty right price, of course.", price=69420, priceMod=1, cps=1234)
		yield ShopEntry("Cloud Compute Cluster", shopID=6, color="indigo", description="Your data centers put Google and Amazon to shame.", price=250000, priceMod=1, cps=42069)
		yield ShopEntry("Hyperhypervisor", shopID=7, color="darkviolet", description="A 25th century chip with simulated reality bubble included. An entire universe finely tuned and programmed to one purpose: to synthesize and output more Tuxbux.", price=1234567, priceMod=1, cps=99999)

class TuxLogo(Static):
	class Clicked(Message):
		def __init__(self, int: int) -> None:
			self.int = int
			super().__init__()
	
	def on_click(self) -> None:
		self.post_message(self.Clicked(1))

class TuxbuxCounter(Digits):
	counter = reactive(0)

	def watch_tuxbux_counter(self, counter_value: int):
		self.value = "$" + str(counter_value)

# shop related stuffs
priceIncrease = 1.35
ShopEntries = {}
ShopEntriesOwned = {}
	
class ShopEntry(Static):
	def __init__(self, title, shopID=-1, color="white", description="", price=0, cps=0, priceMod=1, buyFunction=False, isVisible=False):
		global ShopEntries

		self.shopID = shopID
		
		self.price = reactive(0)
		self.color = color
		self.priceMod = priceMod
		self.title = title
		self.description = description
		if (buyFunction):
			self.buyFunction = buyFunction
		else:
			self.buyFunction = False
		self.basePrice = price
		self.baseCps = cps

		self.price = self.basePrice
		self.cps = self.baseCps
		self.cost = 0
		self.amount = 0
		self.isVisible = isVisible

		ShopEntries[self.title] = self
		ShopEntriesOwned.update({self.title : 0})

		if not (LOADED_APP_SAVE_DATA == {}) and not (LOADED_APP_SAVE_DATA[f"ENTRY_{shopID}_PRICE"] == -1):
			self.price = LOADED_APP_SAVE_DATA[f"ENTRY_{shopID}_PRICE"]
			self.basePrice = LOADED_APP_SAVE_DATA[f"ENTRY_{shopID}_PRICE"]
		super().__init__()

	# @property
	def getPrice(self):
		price = self.basePrice * (priceIncrease ** max(0, self.amount) * self.priceMod)
		return math.ceil(price)

	class Bought(Message):
		def __init__(self, cost: int, cps: int, entry: str) -> None:
			self.cost = cost
			self.entry = entry
			self.cps = cps
			super().__init__()
	class NewPrice(Message):
		def __init__(self, price: int, shopID: int) -> None:
			self.price = price
			self.shopID = shopID
			super().__init__()

	def buy(self, money):
		price = self.getPrice()
		if (money >= price):
			self.post_message(self.Bought(price, self.cps, self.title))
			self.amount += 1
			price = self.getPrice()
			self.price = price
			self.post_message(self.NewPrice(price, self.shopID))
			if (self.buyFunction): self.buyFunction()
	
	def on_mount(self):
		# def update_label(price : int):
		# 	self.query_one(Button).label = f"Buy (${price})"
		def make_visible(best):
			if (best >= self.basePrice):
				self.isVisible = True
				self.styles.visibility = "visible"
		
		self.styles.border = ("outer", self.color)
		self.classes=F"purchasable"
		self.border_title = self.title
		
		if (self.isVisible):
			self.styles.visibility = "visible"
		else:
			self.styles.visibility = "hidden"
		
		self.watch(app, "tuxbuxBestAmount", make_visible)
		self.query_one(Button).label = f"Buy (${self.price})"



	def compose(self) -> ComposeResult:
		with HorizontalGroup():
			yield Label(self.description, classes="label")
			yield Button("Buy", classes="button buy")

	def on_button_pressed(self, event: Button.Pressed) -> None:
		"""Event handler called when a button is pressed."""
		# button_id = event.button.id
		self.buy(app.tuxbuxAmount)
		self.query_one(Button).label = f"Buy (${self.price})"

class TuxbuxIdleGameApp(App):

	app_save_data = {}
	start_time = reactive(monotonic)
	current_time = reactive(0.0)
	current_day_time = 0.0
	last_open_time = 0.0

	# see Cookie Clicker
	tuxbuxAmount = reactive(0)
	tuxbuxBestAmount = reactive(0) # highest amt of tuxbux Ever
	tuxbuxEarned = reactive(0) # all tuxbux earned during gameplay

	tuxbuxDisplay : int # tuxbux display
	tuxbuxPerSecond : int = 0 # recalculate w/ every new purchase
	tuxbuxPerSecondRaw : int # this doesn't do anything atm
	tuxbuxClicks : int = 0 # +1 for each click
	
	ENTRY_1_PRICE = -1
	ENTRY_2_PRICE = -1
	ENTRY_3_PRICE = -1
	ENTRY_4_PRICE = -1
	ENTRY_5_PRICE = -1
	ENTRY_6_PRICE = -1
	ENTRY_7_PRICE = -1

	#main.js:3331 compute cookies earned while game was closed
	CSS_PATH = "tuxbux.tcss"
	TITLE = "Tuxbux"
	SUB_TITLE = "An idle game in your terminal"
	WELCOME = """
╻ ╻┏━╸╻  ┏━╸┏━┓┏┳┓┏━╸     ╻ ╻┏━┓┏━╸┏━┓
┃╻┃┣╸ ┃  ┃  ┃ ┃┃┃┃┣╸      ┃ ┃┗━┓┣╸ ┣┳┛
┗┻┛┗━╸┗━╸┗━╸┗━┛╹ ╹┗━╸ ┛   ┗━┛┗━┛┗━╸╹┗╸
"""
	SHOPHEADER = """
█▀        ▄▄▄▄  ▄    ▄  ▄▄▄▄  ▄▄▄▄▄        ▀█
█        █▀   ▀ █    █ ▄▀  ▀▄ █   ▀█        █
█        ▀█▄▄▄  █▄▄▄▄█ █    █ █▄▄▄█▀        █
█   ▀▀▀      ▀█ █    █ █    █ █       ▀▀▀   █
█        ▀▄▄▄█▀ █    █  █▄▄█  █             █
▀▀                                         ▀▀
"""
# credits to https://www.asciiart.eu/computers/computers
	COMPUTER_ASCII = """
|-----------------------------------------|
|  _____________________________________  |
| |  CD-ROM   16X                       | |
| |______________________________.______| |
|       .oO                         ^     |
|   O  =====                {O} {#######} |
|--+--+---------------------+---+---------|
|  |  |####"""""""""""""####|   |   __    |
|  |  |#"                 "#|   | .' _`.  |
|  |   'q                 p'    | |=(_)|  |  Removable
|  |    'q_______________p'     | `.__.'  |  Hard Drive
|  |                            |         |
|  |----------------------------|    O    |
|--+------------------------+---+---------|
| ______,----------,______  |    Power    |
||______            ______| |   ,''''',   |  Floppy Disk
|       |__________|        |  d ~~~~~ b  |        Power Switch
|  {#}                ####  |  q ~~~~~ p  |
|---------------------------|   "wwwww"   |
|                           |             |
|                           |             |  Blank 3.5" Bay
|                           |    Reset    |
|                           |   ,''''',   |  Reset Button
|---------------------------+  d~~~~~~~b  |
| +-----+                      q~~~~~~~p  |
| | P   |             ON   O    "wwwww"   |       On Light
| |   C |                          |      |
| +-----+             HDD  O       |      |      Hard Disk Light
|                                  |      |
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }  CASE PATTERN
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |   }
|  o   o   o   o   o   o   o       |      |   }
|                                  |      |
|_________________________________________|
   [CA]                            [CA]       FEET
"""
	# credits to Mik & ascii-art.de; http://www.ascii-art.de/ascii/jkl/linux.txt
	TUX_ASCII = """
                 .88888888:.
                88888888.88888.
              .8888888888888888.
              888888888888888888
              88' _`88'_  `88888
              88 88 88 88  88888
              88_88_::_88_:88888
              88:::,::,:::::8888
              88`:::::::::'`8888
             .88  `::::'    8:88.
            8888            `8:888.
          .8888'             `888888.
         .8888:..  .::.  ...:'8888888:.
        .8888.'     :'     `'::`88:88888
       .8888        '         `.888:8888.
      888:8         .           888:88888
    .888:88        .:           888:88888:
    8888888.       ::           88:888888
    `.::.888.      ::          .88888888
   .::::::.888.    ::         :::`8888'.:.
  ::::::::::.888   '         .::::::::::::
  ::::::::::::.8    '      .:8::::::::::::.
 .::::::::::::::.        .:888:::::::::::::
 :::::::::::::::88:.__..:88888:::::::::::'
  `'.:::::::::::88888888888.88:::::::::'
        `':::_:' -- '' -'-' `':_::::'`
                  Click me!        
"""
	BINDINGS = [
		("d", "toggle_dark", "Toggle dark mode"),
		("w", "add_purchasable", "Write save"),
	]

	def compose(self) -> ComposeResult:
		"""Create child widgets for the app."""
		yield Header()
		yield Footer()
		with VerticalGroup(classes="box counterpane"):
			yield Label(self.WELCOME, classes="welcome label") # TODO this should be a randomly generated name I think, like Hacker Dwarf's Machine
			yield Rule(line_style="thick", classes="welcome rule")
			yield TuxbuxCounter("$999,999", classes="counter digits", id="tuxbux_counter") # turn into millions when you get there
			yield Rule(line_style="dashed", classes="counter rule")
			with Container(classes="welcome", id="icons"):
				yield TuxLogo(self.TUX_ASCII, id="tux_icon")
		yield Static(self.COMPUTER_ASCII, classes="box display")
		with VerticalGroup(classes="box shop"):
			yield Label(self.SHOPHEADER, id="label")
			yield Rule(line_style="thick", id="rule")
			yield Shop(id="shop")

	def tuxbux_calculate_gains(self) -> None:
		self.tuxbuxPerSecond = 0

	def action_add_purchasable(self) -> None:
		app.write_save()

	def on_mount(self):
		if not CANSAVE:
			app.notify(f"Failed to access {SAVEPATH}.", title="Failed Load Save", severity="warning", timeout=12)

		def update_counter(counter_value : int):
			counter_value_fmt = "$" + str(counter_value)
			self.query_one(TuxbuxCounter).update(value=counter_value_fmt)

		def track_tuxbux_amount(tuxbuxAmount):
			if tuxbuxAmount > app.tuxbuxBestAmount:
				app.tuxbuxBestAmount = tuxbuxAmount


		self.watch(self, "tuxbuxAmount", update_counter)
		self.watch(self, "tuxbuxAmount", track_tuxbux_amount)

		self.set_interval(1, self.handle_cps)
		self.set_interval(60, app.write_save) # let's try to write a save every minute

	def on_load(self):
		if not (LOADED_APP_SAVE_DATA == {}):
			app.tuxbuxAmount = LOADED_APP_SAVE_DATA["TUXBUX_AMOUNT"]
			app.tuxbuxBestAmount = LOADED_APP_SAVE_DATA["TUXBUX_BEST_AMOUNT"]
			app.tuxbuxPerSecond = LOADED_APP_SAVE_DATA["TUXBUX_PER_SECOND"]
			timeDiff = int(time.time()) - LOADED_APP_SAVE_DATA["TIME_LAST_OPEN"]
			app.tuxbuxAmount += int( max(0, ((timeDiff / 10) * app.tuxbuxPerSecond)) )
			self.log(LOADED_APP_SAVE_DATA)
			for i in range(1,8):
				if (f"ENTRY_{i}_PRICE" in LOADED_APP_SAVE_DATA): 
					self.log(LOADED_APP_SAVE_DATA[f"ENTRY_{i}_PRICE"])
				else:
					LOADED_APP_SAVE_DATA[f"ENTRY_{i}_PRICE"] = -1
				# self.log(LOADED_APP_SAVE_DATA[f"ENTRY_{i}_PRICE"])

	def write_save(self) -> None:
		if SAVEPATH and CANSAVE:
			app.current_day_time = time.time()

			app.app_save_data.update({"TIME_LAST_OPEN" : int(app.current_day_time)})
			app.app_save_data.update({"TUXBUX_AMOUNT" : int(app.tuxbuxAmount)})
			app.app_save_data.update({"TUXBUX_BEST_AMOUNT" : int(app.tuxbuxBestAmount)})
			app.app_save_data.update({"TUXBUX_CLICKS" : int(app.tuxbuxClicks)})
			app.app_save_data.update({"TUXBUX_PER_SECOND" : int(self.tuxbuxPerSecond)})

			for i in range(1,8):
				if (f"ENTRY_{i}_PRICE" in LOADED_APP_SAVE_DATA): 
					app.app_save_data.update({f"ENTRY_{i}_PRICE" : LOADED_APP_SAVE_DATA[f"ENTRY_{i}_PRICE"]})

			app_save_data_json = json.dumps(app.app_save_data, indent=4)

			with open(SAVEPATH, "w") as outfile:
				outfile.write(app_save_data_json)
			pass

			app.notify(f"Succesfully saved to {SAVEPATH}", title="Save succeeded", severity="information", timeout=3)
		else:
			app.notify(f"Failed to write to {SAVEPATH}", title="Failed Write Save", severity="warning", timeout=12)

	def handle_cps(self) -> None:
		app.tuxbuxAmount += app.tuxbuxPerSecond
		self.current_time = monotonic() - self.start_time
		# self.log(app.tuxbuxPerSecond) 
		# self.log(self.current_time) 
		# self.query_one

	def on_tux_logo_clicked(self, message: TuxLogo.Clicked) -> None:
		self.tuxbuxAmount += 1
		self.tuxbuxClicks += 1

	def on_shop_entry_bought(self, message: ShopEntry.Bought) -> None:
		self.tuxbuxAmount -= max(0, message.cost)
		# self.log(ShopEntries)
		ShopEntriesOwned[message.entry] += 1
		app.tuxbuxPerSecond += message.cps

	def on_shop_entry_new_price(self, message:ShopEntry.NewPrice) -> None:
		app.app_save_data.update({f"ENTRY_{message.shopID}_PRICE" : message.price})

if __name__ == "__main__":
	app = TuxbuxIdleGameApp()
	app.run()
