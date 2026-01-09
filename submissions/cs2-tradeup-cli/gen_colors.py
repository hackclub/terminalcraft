def hex_to_rgb(in_hex):
    in_hex = in_hex.replace("#", "")
    out = list(int(in_hex[i:i+2], 16) for i in [0, 2, 4])

    for count, i in enumerate(out):
        out[count] = int(i*200/51)

    return out


def gen_colors(curses):
    colours = ["#1e1e2e", # 0: bg
               "#cdd6f4", # 1: text default
               "#000000", # 2: 
               "#BADA55", # 3: test\
               "#Fa0202", # 4 :red
               "#c0c0c0", # 5: grey
               "#00FF00" # 6: GREN
               ]

    colours = list(map(hex_to_rgb, colours))
    for count, i in enumerate(colours):
        curses.init_color(count, i[0], i[1], i[2])



