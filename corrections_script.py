#!/usr/bin/env python3
import json, pathlib

path = pathlib.Path("images/gallery-data.json")
data = json.loads(path.read_text())

RENAMES = {
    1: "Hummingbird and a Mexican Sunflower (Tithonia rotundifolia 'Red Torch')",
    2: "Organic Gourds and Pumpkins on a Chair",
    3: "Turban Pumpkin in the Grass",
    5: "The Kalugeritsa Pepper — a Rare Heirloom Chili from North Macedonia, John's Personal Favorite",
    7: "Prepping the Rows for the Starts",
    10: "Charlotte Planting the Starts She Grew from Seed",
    12: "Amazing Heirlooms",
    13: "The Start of the Season",
    15: "Organic Peppers and Plaid",
    18: "Hummingbird Taking a Drink",
    21: "The Start of Our 2026 Season (and John's New Tiller)",
    22: "Me Tying Back Our Organic Produce, Grown from My Personal Seed Collection Acclimated to Our Desert Climate",
    25: "Morning Glories Enjoying the Light",
    26: "Me Working the Rows",
    28: "Our 2024 Arch — the Morning Glories Found a Perfect Place to Hang",
    29: "Our Organic Cayenne Long Slim Pepper — a Hot, Slender Heirloom Chili for Drying and Hot Sauce",
    35: "Our Organic Brad's Atomic Grape — an Award-Winning Tomato Bred by Brad Gates of Wild Boar Farms",
    42: "Dad's Sunset — a Glowing Golden-Orange Heirloom Tomato with a Sweet, Fruity Flavor",
    53: "Charlotte's Garden Welcomes You",
    55: "When You're Fighting to Keep Your Garden Alive, and All You Have Are Bee's Grocery Bags (It Worked)",
    57: "This Was a Fun Harvest, I Love the Colors and Shapes",
    60: "Me Tending the Stand",
    65: "Oink Oink... Our Security Guard, Posted 24/7",
    70: "We Grow Big Fruit — This Beauty Is an Orange Accordion",
    74: "Our Organic Heirloom Black Beauty Tomatoes — a Striking Indigo Variety Bred by Brad Gates in Napa, California",
    76: "That's a Regular-Sized Cherry Tomato",
    78: "A Monarch Gently Lands on a Mexican Red Torch Sunflower",
    79: "An Array of Organic Heirloom Tomatoes",
    82: "John Finished Building the Produce Stand, I Painted It",
    92: "Charlotte's Garden After Tilling — This Sign Was a Gift from Beth Lock, My Mother-in-Law",
    96: "Our Produce Soaking Up the Sun and Getting Established",
    98: "Me and My Sign",
    100: "Can You Guess the Name of This Pumpkin? Email Me Your Answer — Correct Guesses Win a Prize at My Stand",
    103: "Organic Heirloom Cherry Tomatoes",
    104: "The Orange Accordion — a Massive, Deeply Ribbed Heirloom Tomato with Bright Orange Skin, Sweet Fruity Flavor, and Hollow Seed Cavities",
    112: "Carrot Bloom with a Bee",
    113: "Young Cherokee Purple Tomatoes",
    119: "Our 2024 Garden Loaded with Fresh, Organic Produce",
    121: "Go Big or Go Home — This Heirloom Isn't Even Ripe Yet!",
    123: "A Slow Day at the End of the Season",
    126: "John Reaching for a Titan Sunflower, a 9-10 Foot Monster",
    132: "Our Organic Tomatoes Pop!",
    133: "Orange Accordion at Its Breaker Stage",
    136: "Our Organic Sart Roloise Tomato — an Ivory-White Beefsteak Heirloom with Deep Indigo-Purple Brushstrokes",
    137: "Our Organic Habanero Peppers — a Very Hot, Lantern-Shaped Chili with a Fruity Flavor",
    141: "A Good Harvest Day",
    143: "Do You Like Sunflower Seeds?",
    147: "A Happy Day at Our Old Location",
    148: "Happy Tomatoes Growing",
}

PRUNE = {80,81,4,83,6,84,85,8,86,87,88,89,90,91,93,16,94,17,95,19,97,20,99,23,
         101,24,102,105,27,106,107,108,109,30,110,31,111,32,33,114,34,116,36,
         117,37,118,38,39,120,40,41,122,43,124,44,125,45,127,47,128,48,50,51,
         134,54,135,56,138,58,139,59,140,61,62,63,144,64,145,66,146,67,150,69,
         151,71,152,72,153,73,154,75,155,77}

by_n = {item["n"]: item for item in data}

for n, title in RENAMES.items():
    if n in by_n:
        by_n[n]["title"] = title
        print(f"OK rename: {n}")
    else:
        print(f"NO MATCH rename: {n}")

for n in PRUNE:
    if n in by_n:
        by_n[n]["keep"] = False
        print(f"OK prune: {n}")
    else:
        print(f"NO MATCH prune: {n}")

path.write_text(json.dumps(data, indent=2))
print("done")
