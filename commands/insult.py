from random import choice

args = ['channels', 'target', 'nick', 'config']


def cmd(send, msg, args):
    adj = [
        "acidic", "antique", "contemptible", "culturally-unsound",
        "despicable", "evil", "fermented", "festering", "foul", "fulminating",
        "humid", "impure", "inept", "inferior", "industrial", "left-over",
        "low-quality", "malodorous", "off-color", "penguin-molesting",
        "petrified", "pointy-nosed", "salty", "sausage-snorfling", "tastless",
        "tempestuous", "tepid", "tofu-nibbling", "unintelligent", "unoriginal",
        "uninspiring", "weasel-smelling", "wretched", "spam-sucking",
        "egg-sucking", "decayed", "halfbaked", "infected", "squishy", "porous",
        "pickled", "coughed-up", "thick", "vapid", "hacked-up", "unmuzzleld",
        "bawdy", "vain", "lumpish", "churlish", "fobbing", "rank", "craven",
        "puking", "jarring", "fly-bitten", "pox-marked", "fen-sucked",
        "spongy", "droning", "gleeking", "warped", "currish", "milk-livered",
        "surly", "mammering", "ill-borne", "beef-witted", "tickle-brained",
        "half-faced", "headless", "wayward", "rump-fed", "onion-eyed",
        "beslubbering", "villainous", "lewd-minded", "cockered", "full-gorged",
        "rude-snouted", "crook-pated", "pribbling", "dread-bolted",
        "fool-born", "puny", "fawning", "sheep-biting", "dankish", "goatish",
        "weather-bitten", "knotty-pated", "malt-wormy", "saucyspleened",
        "motley-mind", "it-fowling", "vassal-willed", "loggerheaded",
        "clapper-clawed", "frothy", "ruttish", "clouted", "common-kissing",
        "pignutted", "folly-fallen", "plume-plucked", "flap-mouthed",
        "swag-bellied", "dizzy-eyed", "gorbellied", "weedy", "reeky",
        "measled", "spur-galled", "mangled", "impertinent", "bootless",
        "toad-spotted", "hasty-witted", "horn-beat", "yeasty", "boil-brained",
        "tottering", "hedge-born", "hugger-muggered", "elf-skinned"]
    amt = [
        "accumulation", "bucket", "coagulation", "enema-bucketful", "gob",
        "half-mouthful", "heap", "mass", "mound", "petrification", "pile",
        "puddle", "stack", "thimbleful", "tongueful", "ooze", "quart", "bag",
        "plate", "ass-full", "assload"]
    noun = [
        "bat toenails", "bug spit", "cat hair", "chicken piss", "dog vomit",
        "dung", "fat-woman's stomach-bile", "fish heads", "guano", "gunk",
        "pond scum", "rat retch", "red dye number-9", "Sun IPC manuals",
        "waffle-house grits", "yoo-hoo", "dog balls", "seagull puke",
        "cat bladders", "pus", "urine samples", "squirrel guts",
        "snake assholes", "snake bait", "buzzard gizzards", "cat-hair-balls",
        "rat-farts", "pods", "armadillo snouts", "entrails", "snake snot",
        "eel ooze", "slurpee-backwash", "toxic waste", "Stimpy-drool", "poopy",
        "poop", "craptacular carpet droppings", "jizzum", "cold sores",
        "anal warts"]
    if not msg:
        users = (list(args['channels'][args['target']].users())
                 if args['target'] != 'private' else ['you'])
        user = choice(users)
    else:
        user = msg
    msg = '%s is a %s of %s.' % user, choice(adj), choice(amt), choice(noun)
    send(msg)
