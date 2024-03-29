import tkinter as tk
import tkinter.ttk as ttk

import webbrowser

import TradeParser

PAINT_MAP = {"Any": "0", "None": "N", "Painted": "A",
             "Burnt Sienna": "1", "Lime": "2", "Titanium White": "3", "Cobalt": "4", "Crimson": "5", "Forest Green": "6",
             "Grey": "7", "Orange": "8", "Pink": "9", "Purple": "10", "Saffron": "11", "Sky Blue": "12", "Black": "13"}

PAINTS = list(PAINT_MAP.keys())

ID_FILE = "./dat/ids.txt"

#Test dataset flag. If False, then we load test data instead of waiting for real requests.
LIVE = True


def update_ids(new_pair):
    with open(ID_FILE, "a+") as id_file:
        id_file.write(",".join(new_pair) + "\n")


class TradeGUI:
    def __init__(self, master, known_ids):
        self.master = master
        master.title("RL Trader")

        self.known_ids = known_ids

        self.name_label = ttk.Label(master, text="Item name:")
        self.id_label = ttk.Label(master, text="Item id:")
        self.paint_label = ttk.Label(master, text="Item paint:")

        self.name = tk.StringVar(master)
        self.id = tk.StringVar(master)
        self.paint = tk.StringVar(master)

        self.name.trace("w", lambda name, index, mode, sv=self.name: self.find_id(sv))

        self.paint.set(PAINTS[0])

        self.name_input = ttk.Entry(master, textvariable=self.name)
        self.id_input = ttk.Entry(master, textvariable=self.id)
        self.paint_select = ttk.OptionMenu(master, self.paint, PAINTS[0], *PAINTS)

        self.go_button = ttk.Button(master, text="Search", command=lambda: self.spawn_orders())

        self.name_label.grid(row=0, column=0)
        self.id_label.grid(row=1, column=0)
        self.paint_label.grid(row=2, column=0)

        self.name_input.grid(row=0, column=1)
        self.id_input.grid(row=1, column=1)
        self.paint_select.grid(row=2, column=1)

        self.go_button.grid(row=3, column=1)

    def spawn_orders(self):
        paint = self.paint.get()
        if paint == "Any" or paint == "None" or paint == "Painted":
            paint = "None"

        if LIVE:
            buy_orders = TradeParser.get_sorted_buy_orders(self.name.get(), self.id.get(), paint)
            sell_orders = TradeParser.get_sorted_sell_orders(self.name.get(), self.id.get(), paint)
        else:
            buy_orders = TradeParser.get_example_buy_orders()
            sell_orders = TradeParser.get_example_sell_orders()

        if len(buy_orders) > 0 and len(sell_orders) > 0:
            buy_orders = TradeParser.remove_outlying_trades(buy_orders, "buy")
            sell_orders = TradeParser.remove_outlying_trades(sell_orders, "sell")

            if self.name.get() not in self.known_ids:
                self.known_ids[self.name.get()] = self.id.get()
                update_ids([self.name.get(), self.id.get()])

            self.buy_orders_window = tk.Toplevel(self.master)
            self.sell_orders_window = tk.Toplevel(self.master)

            self.buy_orders = OrderView(self.buy_orders_window, buy_orders, "Buy Orders", self.name.get())
            self.sell_orders = OrderView(self.sell_orders_window, sell_orders, "Sell Orders", self.name.get())

    def find_id(self, sv: tk.StringVar):
        if sv.get() in self.known_ids:
            self.id_input.delete(0, tk.END)
            self.id_input.insert(0, self.known_ids[sv.get()])


class OrderView:
    def __init__(self, master, orders, order_type, name):
        self.master = master
        self.master.minsize(400, 400)

        self.orders = orders

        self.item_label = tk.Label(self.master, text=f"{order_type} for {name}")
        self.key_label = tk.Label(self.master, text="Key count")
        self.link_label = tk.Label(self.master, text="Link")

        self.key_list = tk.Listbox(self.master)
        self.link_list = tk.Listbox(self.master, selectmode="SINGLE")

        self.scroll = tk.Scrollbar(self.master, command=self.scroll_lists, orient=tk.VERTICAL)

        self.key_list.config(yscrollcommand=self.scroll_set)
        self.link_list.config(yscrollcommand=self.scroll_set)

        self.link_list.bind("<<ListboxSelect>>", self.open_trade)

        max_len = 0

        for order in self.orders:
            if order_type == "Buy Orders":
                keys = str(order.items_in[0].amount)
            else:
                keys = str(order.items_out[0].amount)

            if len(keys) > max_len:
                max_len = len(keys)

            self.key_list.insert(tk.END, keys)
            self.link_list.insert(tk.END, order.link)

        self.link_list.config(width=max_len)

        tk.Grid.columnconfigure(self.master, 1, weight=1)
        tk.Grid.columnconfigure(self.master, 2, weight=1)

        self.item_label.grid(row=0, column=0, sticky="nesw")
        self.key_label.grid(row=1, column=0, sticky="nesw")
        self.link_label.grid(row=1, column=1, sticky="nesw")

        self.scroll.grid(row=2, column=2, sticky="nsw")

        self.key_list.grid(row=2, column=0, sticky="nesw")
        self.link_list.grid(row=2, column=1, sticky="nesw")

    def scroll_lists(self, *args):
        self.link_list.yview(*args)
        self.key_list.yview(*args)

    def scroll_set(self, *args):
        self.scroll.set(args[0], last=args[1])

        self.link_list.yview('moveto', args[0])
        self.key_list.yview('moveto', args[0])

    def open_trade(self, event):
        link = self.link_list.get(self.link_list.curselection())
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open_new_tab("https://rocket-league.com" + link)


def parse_ids(id_file):
    pairs = {}

    with open(id_file, "r") as ids:
        for line in ids.readlines():
            pair = line.strip("\n").split(",")
            pairs[pair[0]] = pair[1]

    return pairs


if __name__ == "__main__":
    ids = parse_ids(ID_FILE)

    root = tk.Tk()
    trade_gui = TradeGUI(root, ids)
    root.mainloop()
