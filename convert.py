
# Reads the CSV exported from Google Docs and turns it into the format
# expected by the Google App.

import sys, csv

(ID, TITLE, TAGS, AUTHOR, ACCEPTED, DESCRIPTION) = (-1, 0, 3, 4, 7, 10)
(ID, TITLE, TAGS, AUTHOR, ACCEPTED, DESCRIPTION) = (0, 1, 2, 3, -1, 4)

def get(row, field_ix):
    if field_ix == -1:
        return None
    return row[field_ix]

def is_accepted(row):
    return ACCEPTED == -1 or row[ACCEPTED].strip() == "1"

inf = open(sys.argv[1])
reader = csv.reader(inf)

row = reader.next() # skip header row

# for verifying column mappings
print "Tittel:", get(row, TITLE)
print "Tags:", get(row, TAGS)
print "Author:", get(row, AUTHOR)
print "Accepted:", get(row, ACCEPTED)
print "Description:", get(row, DESCRIPTION)

outf = open(sys.argv[2], "w")
ix = 1
for row in reader:
    # padding to avoid index errors below
    row = row + ([""] * 10)

    # include only accepted talks
    if (not is_accepted(row)) or (not row[TITLE].strip()):
        continue

    # map it
    id = get(row, ID) or str(ix)
    fields = map(lambda v: v.replace("\n", " "),
                 [id, 
                  row[TITLE], row[TAGS], row[AUTHOR], row[DESCRIPTION]])
    outf.write("|".join(fields) + "\n")
    ix += 1

outf.close()
