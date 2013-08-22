def cmd(send, msg, args):
    """Does impressions of ahamilto, fwilson, creffett, pfoley, and skasturi.
       Syntax: !impressions <impression>
     """
    quotes = ['Sorry, I don't do that impression.']
    
    if msg = 'ahamilto':
      quotes = ['ic', '...', 'ic...']
      
    if msg = 'fwilson':
      quotes = ['ic', 'oic', '-_-']
      
    if msg = 'creffett':
      quotes = ['how nice', 'how nice.']
      
    if msg = 'pfoley':
      quotes = [':)']
    
    if msg = 'skasturi':
      quotes = ['hi zan', 'hey zan']
    
    send(choice(quotes))
    
