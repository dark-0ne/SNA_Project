import csv

from lxml import etree as ET

dblp_record_types_for_publications = ('article', 'inproceedings', 'proceedings', 'book', 'incollection',
    'phdthesis', 'masterthesis', 'www')

# read dtd
dtd = ET.DTD("dblp-2019-11-22.dtd") #pylint: disable=E1101

# get an iterable
context = ET.iterparse("dblp-2022-04-01.xml", events=('start', 'end'), load_dtd=True, #pylint: disable=E1101
    resolve_entities=True) 

# turn it into an iterator
context = iter(context)

# get the root element
event, root = next(context)

n_records_parsed = 0
n_records_authors = 0
n_records_schools = 0
with open('parsed2.csv', 'w') as f:
    writer = csv.writer(f,delimiter=";")

    for event, elem in context:
        if event == 'end' and elem.tag in dblp_record_types_for_publications:
            pub_year = None
            for year in elem.findall('year'):
                pub_year = year.text
            if pub_year is None:
                continue

            pub_title = None
            for title in elem.findall('title'):
                pub_title = title.text
            if pub_title is None:
                continue

            pub_authors = []
            for author in elem.findall('author'):
                if author.text is not None:
                    pub_authors.append(author.text.replace(":",","))
            if len(pub_authors) > 0:
                    n_records_authors += 1
            else:
                continue

            pub_schools = []
            for school in elem.findall('school'):
                if school.text is not None:
                    pub_schools.append(school.text.replace(":",","))
            if len(pub_schools) > 0:
                    n_records_schools += 1

            # print(pub_year)
            # print(pub_title)
            # print(pub_authors)
            # insert the publication, authors in sql tables
            writer.writerow([pub_title,pub_year,":".join(pub_authors),":".join(pub_schools)])

            elem.clear()
            root.clear()

            n_records_parsed += 1

elem.clear()
root.clear()
print("No. of records parsed: {}".format(n_records_parsed))
print("No. of records parsed: {}".format(n_records_authors))
print("No. of records parsed: {}".format(n_records_schools))
