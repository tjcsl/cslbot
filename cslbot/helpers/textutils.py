# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import json
import re
import string
from html import escape, unescape
from random import choice, randint, random, randrange

from lxml import etree, html  # type: ignore

from pkg_resources import Requirement, resource_string  # type: ignore

from requests import get, post

from .tokens import token_cache

slogan_cache = []  # type: List[str]


def gen_removevowels(msg):
    return re.sub('[aeiouy]', '', msg, flags=re.I)


def gen_word():
    return get('http://randomword.setgetgo.com/get.php').text.strip()


def gen_hashtag(msg):
    msg = "".join([x.strip() for x in msg.split()])
    return '#' + msg.translate(dict.fromkeys(map(ord, string.punctuation)))


def gen_yoda(msg):
    req = post("http://www.yodaspeak.co.uk/index.php", data={'YodaMe': msg})
    return html.fromstring(req.content.decode(errors='ignore')).findtext('.//textarea[@readonly]').strip()


def gen_gizoogle(msg):
    req = post("http://www.gizoogle.net/textilizer.php", data={'translatetext': escape(msg).encode('utf-7')})  # type: ignore
    # This mess is needed because gizoogle has a malformed textarea, so the text isn't within the tag
    response = unescape(html.tostring(html.fromstring(req.text).find('.//textarea')).decode('utf-7')).strip()
    response = re.sub(".*</textarea>", '', response)
    return unescape(response)


def gen_shakespeare(msg):
    # Originally from http://www.shmoop.com/shakespeare-translator/
    table = json.loads(resource_string(Requirement.parse('CslBot'), 'cslbot/static/shakespeare-dictionary.json').decode())
    replist = reversed(sorted(table.keys(), key=len))
    pattern = re.compile(r'\b(' + '|'.join(replist) + r')\b', re.I)
    # Normalize text to hopefully match more words.
    result = pattern.sub(lambda x: table[x.group().lower()], transform_text(msg))
    return result


def gen_praise(msg):
    praise = get_praise()
    while not praise:
        praise = get_praise()
    return '%s: %s' % (msg, praise)


def get_praise():
    doc = html.fromstring(get('http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG').text)
    return doc.find('body/center/h2').text.replace('\n', ' ').strip()


def gen_fwilson(x, mode=None):
    if x.lower().startswith('fwil'):
        mode = 'w'
    if mode is None:
        mode = 'w' if random() < 0.5 else 'f'
    if mode == 'w':
        output = "wh%s %s" % ('e' * randrange(3, 20), x)
        return output.upper()
    else:
        output = ['fwil%s' % q for q in x.split()]
        output = ' '.join(output)
        return output.lower()


def gen_creffett(msg):
    return '\x02\x038,04%s!!!' % msg.upper()


def gen_slogan(msg):
    # Originally from sloganizer.com
    if not slogan_cache:
        slogan_cache.extend(resource_string(Requirement.parse('CslBot'), 'cslbot/static/slogans').decode().splitlines())
    return re.sub('%s', msg, choice(slogan_cache))


def gen_morse(msg):
    morse_codes = {"a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.",
                   "g": "--.", "h": "....", "i": "..", "j": ".---", "k": "-.-", "l": ".-..",
                   "m": "--", "n": "-.", "o": "---", "p": ".--.", "q": "--.-", "r": ".-.",
                   "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
                   "y": "-.--", "z": "--..", "1": ".----", "2": "..---", "3": "...--",
                   "4": "....-", "5": ".....", "6": "-....", "7": "--...", "8": "---..",
                   "9": "----.", "0": "-----", " ": "  ", ".": ".-.-.-", ",": "--..--",
                   "?": "..--..", "'": ".----.", "!": "-.-.--", "/": "-..-.", "(": "-.--.",
                   ")": "-.--.-", "&": ".-...", ":": "---...", ";": "-.-.-.", "=": "-...-",
                   "+": ".-.-.", "-": "-....-", "_": "..--.-", '"': ".-..-.", "$": "...-..-", "@": ".--.-."}
    morse = ""
    for i in msg.lower():
        if i in morse_codes:
            morse += morse_codes[i] + " "
        else:
            morse += "? "
    return morse


def gen_insult(user):
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
    msg = '%s is a %s %s of %s.' % (user, choice(adj), choice(amt), choice(noun))
    return msg


def char_to_bin(c):
    i = ord(c)
    n = 8
    # We need to be able to handle wchars
    if i > 1 << 8:
        n = 16
    if i > 1 << 16:
        n = 32
    ret = ""
    for _ in range(n):
        ret += str(i & 1)
        i >>= 1
    return ret[::-1]


def gen_binary(text):
    return "".join(map(char_to_bin, text))


def gen_xkcd_sub(msg, hook=False):
    # http://xkcd.com/1288/
    substitutions = {'witnesses': 'these dudes I know',
                     'allegedly': 'kinda probably', 'new study': 'tumblr post',
                     'rebuild': 'avenge', 'space': 'SPAAAAAACCCEEEEE',
                     'google glass': 'virtual boy', 'smartphone': 'pokedex',
                     'electric': 'atomic', 'senator': 'elf-lord', 'car': 'cat',
                     'election': 'eating contest', 'congressional leaders':
                     'river spirits', 'homeland security': 'homestar runner',
                     'could not be reached for comment':
                     'is guilty and everyone knows it'}
    # http://xkcd.com/1031/
    substitutions['keyboard'] = 'leopard'
    # http://xkcd.com/1418/
    substitutions['force'] = 'horse'
    output = msg
    if not hook or random() < 0.001 or True:
        for text, replacement in substitutions.items():
            if text in output:
                output = re.sub(r"\b%s\b" % text, replacement, output)

    output = re.sub(r'(.*)(?:-ass )(.*)', r'\1 ass-\2', output)
    if msg == output:
        return None if hook else msg
    else:
        return output


def reverse(msg):
    return msg[::-1]


def gen_lenny(msg):
    return "%s ( ͡° ͜ʖ ͡°)" % msg


def gen_shibe(msg):
    topics = msg.split() if msg else [gen_word()]

    reaction = 'wow'
    adverbs = ['so', 'such', 'very', 'much', 'many']
    for i in topics:
        reaction += ' %s %s' % (choice(adverbs), i)

    quotes = ['omg', 'amaze', 'nice', 'clap', 'cool', 'doge', 'shibe', 'ooh']
    for i in range(randint(1, 2)):
        reaction += ' %s' % choice(quotes)
    reaction += ' wow'
    return reaction


def gen_underscore(msg):
    return msg.replace(' ', '_').lower()


def transform_text(msg):
    # Don't die if no api key
    if token_cache['translate'] == 'invalid':
        return msg
    headers = {'Authorization': 'Bearer %s' % token_cache['translate']}
    data = get('http://api.microsofttranslator.com/V3/json/TransformText', params={'language': 'en', 'sentence': msg}, headers=headers).json()
    return data['sentence'] if data['ec'] == 0 else data['em']


def gen_translate(msg, outputlang='en'):
    # Don't die if no api key
    if token_cache['translate'] == 'invalid':
        return msg
    headers = {'Authorization': 'Bearer %s' % token_cache['translate']}
    req = get('http://api.microsofttranslator.com/V2/Http.svc/Translate', params={'text': transform_text(msg), 'to': outputlang}, headers=headers)
    xml = etree.fromstring(req.content)
    if xml.tag == 'html':
        doc = ' '.join(xml.itertext())
        doc = ' '.join(doc.splitlines())
        return "An error occurred: %s" % doc
    return xml.text


def gen_random_translate(msg):
    # Don't die if no api key
    if token_cache['translate'] == 'invalid':
        return msg
    headers = {'Authorization': 'Bearer %s' % token_cache['translate'], 'Content-Type': 'text/xml'}
    langs = get('http://api.microsofttranslator.com/V2/Http.svc/GetLanguagesForTranslate', headers=headers)
    names = post('http://api.microsofttranslator.com/V2/Http.svc/GetLanguageNames', params={'locale': 'en'}, data=langs.text, headers=headers)
    langs_xml = etree.fromstring(langs.content)
    names_xml = etree.fromstring(names.content)
    langs = {langs_xml[x].text: names_xml[x].text for x in range(len(langs_xml))}
    # No point in english->english
    del langs['en']
    # This Klingon variant seems to royally screw-up terminals.
    del langs['tlh-Qaak']
    outputlang = choice(list(langs.keys()))
    translation = gen_translate(msg, outputlang)
    return "%s (%s)" % (translation, langs[outputlang])


def append_filters(filters):
    filter_list = []
    for next_filter in filter(None, filters.split(',')):
        if next_filter in output_filters.keys():
            filter_list.append(output_filters[next_filter])
        else:
            return None, "Invalid filter %s." % next_filter
    return filter_list, "Okay!"


def gen_randfilter(msg):
    randfilter = choice(list(output_filters.values()))
    return randfilter(msg)

output_filters = {
    "passthrough": lambda x: x,
    "hashtag": gen_hashtag,
    "fwilson": gen_fwilson,
    "creffett": gen_creffett,
    "slogan": gen_slogan,
    "insult": gen_insult,
    "morse": gen_morse,
    "removevowels": gen_removevowels,
    "binary": gen_binary,
    "xkcd": gen_xkcd_sub,
    "praise": gen_praise,
    "reverse": reverse,
    "lenny": gen_lenny,
    "yoda": gen_yoda,
    "gizoogle": gen_gizoogle,
    "shakespeare": gen_shakespeare,
    "bard": gen_shakespeare,
    "shibe": gen_shibe,
    "underscore": gen_underscore,
    "translate": gen_translate,
    "randtrans": gen_random_translate,
    "randfilter": gen_randfilter
}
