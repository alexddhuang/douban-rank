import json
import sys
import urllib.parse
import urllib.request

q = sys.argv[1]

items_limit = 0
if len(sys.argv) >= 3:
    items_limit = int(sys.argv[2])

api = "https://api.douban.com/v2/book/search"
apikey = "0df993c66c0c636e29ecbb5344252a4a"

books = []

def read_page(page, books):
    print("reading page "+str(page["start"]))
    for book in page['books']:
        numRaters = int(book['rating']['numRaters'])
        average = float(book['rating']['average'])
        if average > 0:
            books.append({
                'numRaters': numRaters,
                'average': average,
                'title': book['title'],
                'subtitle': book['subtitle'],
                'alt': book['alt'],
            })

url = api+'?apikey='+apikey+'&q='+urllib.parse.quote(q)
page = json.loads(urllib.request.urlopen(url).read(), encoding='utf8')
count = page['count']
if items_limit > 0:
    total = items_limit
else:
    total = page['total']
print("total items " + str(total))

read_page(page, books)
if count == 0:
    sys.exit()
for start in range(count, total, count):
    page = json.loads(urllib.request.urlopen(url+'&start='+str(start)).read(), encoding='utf8')
    read_page(page, books)

all_raters = 0
all_score = 0
for book in books:
    n = book['numRaters']
    all_raters = all_raters + n
    all_score = all_score + n * book['average']
C = all_raters / len(books)
m = all_score / all_raters
print("C: " + str(C))
print("m: " + str(m))

for book in books:
    n = book['numRaters']
    book['bayesian'] = (C * m + n * book['average']) / (C + n)

def sort_by_bayesian(a):
    return a['bayesian']

books.sort(key=sort_by_bayesian, reverse=True)

f = open('books/'+q+'.html', 'w')
f.write('<ul>\n')
for book in books:
    bayesian = book['bayesian']
    alt = book['alt']
    title = book['title']
    if len(book['subtitle']) > 0:
        title = title + ': ' + book['subtitle']

    f.write('<li>\n')
    f.write('<a href="'+alt+'">'+title+'</a> '+'('+str(bayesian)+')\n')
    f.write('</li>\n')
f.write('</ul>\n')
f.close()