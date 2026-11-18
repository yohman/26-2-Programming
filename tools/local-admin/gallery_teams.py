"""Resolve declared Week 7 authors against the roster, without fuzzy title matching."""
import re
import unicodedata


def normalize(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    text = ''.join(chr(ord(c)-0x60) if 'ァ' <= c <= 'ヶ' else c for c in text)
    text = text.translate(str.maketrans({'齋':'斎', '塲':'場'}))
    text = re.sub(r'([aeiou])\1+', r'\1', text)
    return ''.join(c for c in text if c.isalnum())


def author_blocks(notebook):
    result = []
    for cell in (notebook or {}).get('cells', []):
        text = cell.get('source', '')
        text = ''.join(text) if isinstance(text, list) else text
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if cell['cell_type'] != 'markdown' and not line.lstrip().startswith('#'):
                continue
            if not re.search(r'メンバー|氏名|名前|作成者|作者|\bauthors?\b|\bmembers?\b|\bteam\b', line, re.I):
                continue
            block = [line]
            for following in lines[i+1:i+9]:
                if not following.strip():
                    if len(block)>1: break
                    continue
                if re.match(r'^\s*(?:[-*・]|氏名|名前)', following):
                    block.append(following)
                else:
                    break
            result.extend(block)
    return '\n'.join(dict.fromkeys(result))


def declared_members(notebook, roster, aliases=None):
    text = author_blocks(notebook)
    joined = normalize(text)
    found = set()
    alias_map = {}
    for student, person in roster.items():
        candidates = [person['name'], person.get('reading',''), person.get('kana','')]
        for value in candidates:
            if not value: continue
            alias_map.setdefault(normalize(value), set()).add(student)
            if re.fullmatch(r'[A-Za-z -]+', value):
                parts = value.split()
                if len(parts)==2: alias_map.setdefault(normalize(' '.join(reversed(parts))),set()).add(student)
    for spelling, actual in (aliases or {}).items():
        matches = [sid for sid, person in roster.items() if normalize(person['name'])==normalize(actual)]
        if len(matches)==1:alias_map[normalize(spelling)]={matches[0]}
    for alias, students in alias_map.items():
        if alias and len(students)==1 and alias in joined:found.update(students)
    # First names are accepted only as unique, separate kana tokens in an author block.
    first_names = {}
    for student, person in roster.items():
        parts = re.split(r'\s+', person.get('kana','').strip())
        if len(parts)>=2:first_names.setdefault(normalize(parts[-1]),set()).add(student)
    tokens = {normalize(value) for value in re.findall(r'[ぁ-ゖァ-ヶー]+', text)}
    for token in tokens:
        if token in first_names and len(first_names[token])==1:found.update(first_names[token])
    return found


def people(entries, context, roster):
    ids = set()
    for entry in entries:
        details = context[entry['id']]
        ids.add(details['student'])
        ids.update(details['authors'])
    return [dict(name=roster[s]['name'],reading=roster[s].get('reading',''))
            for s in sorted(ids) if s in roster]


def group_projects(entries, context, roster, previous, strict_fingerprint, group_weeks=(7,)):
    """Use explicit author sets; preserve distinct submissions as notebook versions."""
    parent = list(range(len(entries)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(a,b):
        x,y=find(a),find(b)
        if x!=y:parent[y]=x
    # Earlier weeks keep the exact-content behavior.
    fingerprints = {}
    for i, entry in enumerate(entries):
        key=(entry['week'],strict_fingerprint(entry))
        if key in fingerprints:union(i,fingerprints[key])
        fingerprints[key]=i
    prior_by_member = {}
    for project in previous:
        if project['week'] not in group_weeks:continue
        names={normalize(p['name']) for p in project.get('members',[])}
        member_ids={sid for sid,p in roster.items() if normalize(p['name']) in names}
        if len(member_ids)>=2:
            for sid in member_ids:prior_by_member.setdefault((project['week'],sid),[]).append(member_ids)
    for i,entry in enumerate(entries):
        if entry['week'] not in group_weeks:continue
        current=context[entry['id']]
        if not current['authors']:
            known=prior_by_member.get((entry['week'],current['student']),[])
            if len(known)==1:current['authors']=set(known[0])
    # Named authors may have submitted a different revision or omitted their own header.
    for i,a in enumerate(entries):
        if a['week'] not in group_weeks:continue
        ca=context[a['id']];team=ca['authors']|{ca['student']}
        if len(team)<2:continue
        for j,b in enumerate(entries):
            if i==j or b['week']!=a['week']:continue
            cb=context[b['id']];other=cb['authors']|{cb['student']}
            if cb['student'] in team and (len(other)==1 or other<=team or team<=other):union(i,j)
    components={}
    for i,entry in enumerate(entries):components.setdefault(find(i),[]).append(entry)
    projects=[]
    for sources in components.values():
        week=sources[0]['week'];current_ids={e['id'] for e in sources}
        members=people(sources,context,roster) if week in group_weeks else []
        member_names={normalize(p['name']) for p in members}
        old=[]
        for prior in previous:
            if prior['week']!=week:continue
            aliases=set(prior.get('submission_ids',[prior['id']]))
            old_names={normalize(p['name']) for p in prior.get('members',prior.get('submitters',[]))}
            if aliases & current_ids or (member_names and member_names==old_names):old.append(prior)
        # Prefer the most complete documented version; saved errors are not hidden.
        def quality(entry):
            cells=entry['notebook']['cells']
            md=sum(len(''.join(c.get('source',''))) for c in cells if c['cell_type']=='markdown')
            output=sum(bool(c.get('outputs')) for c in cells)
            return (md>0,output,md)
        primary=max(sources,key=quality)
        project=dict(primary)
        project['id']=old[0]['id'] if old else sources[0]['id']
        aliases=list(dict.fromkeys([e['id'] for e in sources]+[sid for e in old for sid in e.get('submission_ids',[e['id']])]))
        project['submission_ids']=aliases
        project['submission_count']=len(sources)
        submitters=[]
        for entry in sources:
            person={'name':entry['student_name'],'reading':entry['student_reading']}
            if person not in submitters:submitters.append(person)
        project['submitters']=submitters
        project['members']=members or submitters
        project['featured']=any(e['featured'] for e in sources)
        project['_primary_id']=primary['id']
        project['_sources']=sources
        project['_previous']=old
        projects.append(project)
    return projects
