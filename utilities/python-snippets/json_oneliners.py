text = '{ "work": "\u201cfun\u201c", "foo": ["bar", "baz"] }'
remove_chars = ['u201c', 'b', 'f']
new_text = ''.join([ch for ch in text if ch not in remove_chars])

subs = {
  '\u201c': "'",
  'z': 't'
}
text = '{ "work": "\u201cfun\u201c", "foo": ["bar", "baz"] }'
letter_list = [(subs[ch] if ch in subs else ch)  for ch in text]
new_text = ''.join(letter_list)

#------------------------------------------------------------

# If you have only 1 or 2 characters to remove I suggest that you use the string .replace() method:
# An example can be on the quote_text key

your_dict['quote_text'].replace('\u201c','')

#------------------------------------------------------------
# If you wish to apply your function to the entire dictionnary values you can use dict comprehensions:
d2 = dict((k, f(v)) for k, v in d1.items())

# d1 being your original dictionnary and f your function.



