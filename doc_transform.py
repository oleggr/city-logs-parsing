from os import listdir
from os.path import isfile, join

import docx2txt
import json
import re


onlyfiles = [f for f in listdir('./') if isfile(join('./', f)) and f[-4:] == 'docx']

events = {}

curr_date = '123'

for file in onlyfiles:
    data = docx2txt.process(file)
    for line in data.split('\n'):
        result = re.match(r'[0-9]*\.[0-9]*\.[0-9]*', line)
        if result:
            curr_date = line.split(' ')[0].strip()
        
        events[curr_date] = events.get(curr_date, '') + line

print(events)

