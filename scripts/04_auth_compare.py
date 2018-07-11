import pickle


def invert(dic):
    inv = {}
    for k,v in dic.iteritems():
        if v not in inv: inv[v] = set()
        inv[v].add(k)
    return inv

def compare_synonyms(a):
    print "\n    For name", a
    a_s = synonyms(a,audris,inv_audris)
    were = "were"
    if len(a_s) > 20:
        were = "included"
    print "    Audris ", len(a_s), "synonyms " + were + ":"
    for aa in list(a_s)[:20]:
        print "           ", aa
    b_s = synonyms(a,bogdan,inv_bogdan)
    were = "were"
    if len(b_s) > 20:
        were = "included"
    print "    Bogdan ", len(b_s), "synonyms " + were + ":"
    for bb in list(b_s)[:20]:
        print "           ", bb


print "Testing"
q = invert({"a":"b", "c":"b", "d":"e"})
print q

print "Reading"
bogdan = pickle.load(open("data/aliasMap.dict", "rb"))
print "Reading"
audris = pickle.load(open("data/audrisAuthMap.dict", "rb"))

 
print "Inverting"
inv_bogdan = invert(bogdan)
print "Inverting"
inv_audris = invert(audris)


print "Bogdan: ", len(bogdan), "mappings to", len(set(bogdan.values())), "distinct values"
print "Audris: ", len(audris), "mappings to", len(set(audris.values())), "distinct values"

def test_synonyms(e1, e2, mapping, inv_mapping):
    if e1 == e2: return True
    if mapping.get(e1,e1) == mapping.get(e2,e2): return True
    return False

def synonyms(email, mapping, inv_mapping):
    if email not in mapping: 
        return set([])
    common = mapping[email]
    syn = inv_mapping[common]
    return syn

print "Pepakriz: Bogdan:", len(synonyms("Josef Kriz <pepakriz@gmail.com>",bogdan,inv_bogdan)) 
print "          Audris:", len(synonyms("Josef Kriz <pepakriz@gmail.com>",audris,inv_audris) )

print "Running stats a->b"
syns_num = 0
syns_den = 0
exceptions = []
for a in audris:
    if a!=audris[a]:
        syns_den += 1
        if test_synonyms(a,audris[a],bogdan,inv_bogdan):
            syns_num += 1
        elif a != audris[a]:
            exceptions.append(a)
print "Bogdan matches",syns_num,"/",syns_den,"of Audris' matches"
print "Some exceptions:"
for a in exceptions[:10]:
    compare_synonyms(a)

print "Running stats b->a"
syns_num = 0
syns_den = 0
exceptions = []
for a in bogdan:
    if a!=bogdan[a]:
        syns_den += 1
        if test_synonyms(a,bogdan[a],audris,inv_audris):
            syns_num += 1
        elif a != bogdan[a]:
            exceptions.append(a)
print "Audris matches",syns_num,"/",syns_den,"of Bogdan' matches"
print "Some exceptions:"
for a in exceptions[:10]:
    compare_synonyms(a)

