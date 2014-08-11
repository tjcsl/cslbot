from random import choice

@Command(['compare', 'comparatron'])
def cmd(send, msg, args):
    """Compares something.
    Syntax: !compare (thing)"""
    
    comparisons = ["nastier", "whiter", "dumber", "pastier", "crustier", "uglier", "stinkier", "more disgusting", "blacker", "crappier"]
    superlatives = ["nastiest", "whitest", "dumbest", "pastiest", "crustiest", "ugliest", "stinkiest", "most disgusting", "blackest", "crappiest"]
    people = ["Maya Angelou", "me", "your momma", "Hillary Clinton", "Thor", "my grandmomma", "you", "the Reverend Martin Luther King, Jr", "the Pope", "Danny Devito", "Sarah Palin"]
    posessivepeople = ["Maya Angelou's", "my", "yo momma's", "Hillary Clinton's", "Thor's", "my grandmomma's", "your", "the Reverend Martin Luther King, Jr.'s", "the Pope's", "Danny Devito's", "Sarah Palin's"]
    things = ["vag", "libido", "dingdong", "legs", "sex life", "butt", "body", "torso", "entire extended family", "stupid dumbass face"]
    
    mode = random.randint(0, 2)
    sentence = None
    
    if msg == "":
        users = list(args['handler'].channels[args['target']].users()) if args['target'] != 'private' else ['you']
        msg = choice(users)

    if mode == 0:
        sentence = msg + " is " + random.choice(comparisons) + " than " + random.choice(posessivepeople) + " " + random.choice(things) + "."
    elif mode == 1:
        sentence = msg + " is " + random.choice(comparisons) + " than " + random.choice(people) + "."
    elif mode == 2:
        sentence = msg + " is the " + random.choice(superlatives) + " damn thing."
    
    send(sentence)