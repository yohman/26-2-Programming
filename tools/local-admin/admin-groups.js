/* Match the private submissions to the gallery's canonical project groups. */
(function(root){
  const keyFor=(record,week=record.week)=>JSON.stringify([Number(week),record.student,record.file||'']);
  async function publicID(week,student,file,cryptoAPI=root.crypto){
    // Python json.dumps uses ASCII escapes and spaces between array items.
    const literal='['+[Number(week),String(student),file||''].map(value=>JSON.stringify(value).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'))).join(', ')+']';
    const digest=await cryptoAPI.subtle.digest('SHA-256',new TextEncoder().encode(literal));
    return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('').slice(0,20);
  }
  const heartKeys=(record,week=record.week)=>record.heart_keys||[keyFor(record,week)];
  const isSelected=(record,hearts,week=record.week)=>heartKeys(record,week).some(key=>hearts.has(key));
  function changesFor(record,hearts,week=record.week){
    const keys=heartKeys(record,week),enabled=!isSelected(record,hearts,week);
    return Object.fromEntries((enabled?keys.slice(0,1):keys).map(key=>[key,enabled]));
  }
  async function build(manifest,gallery,cryptoAPI=root.crypto){
    const mapped=await Promise.all(manifest.weeks.flatMap(week=>week.submissions.map(async source=>({
      ...source,week:week.week,public_id:await publicID(week.week,source.student,source.file,cryptoAPI),heart_key:keyFor(source,week.week)
    }))));
    const byPublic=new Map(mapped.map(source=>[source.public_id,source]));
    return {weeks:manifest.weeks.map(week=>{
      const covered=new Set();
      const groups=(gallery.submissions||[]).filter(group=>group.week===week.week).map(project=>{
        const sources=[...new Map((project.submission_ids||[project.id]).map(id=>byPublic.get(id)).filter(Boolean).map(source=>[source.id,source])).values()];
        if(!sources.length)return null;
        sources.forEach(source=>covered.add(source.id));
        const primaryPublic=project.notebook_path?.match(/\/([a-f0-9]{20})\.ipynb$/)?.[1];
        const primary=sources.find(source=>source.public_id===primaryPublic)||sources[0];
        const variants=(project.variants||[]).map(version=>{
          const source=byPublic.get(version.id);if(!source)return null;
          const names=new Set(version.submitters.map(person=>person.name));
          return {...version,id:source.id,public_id:version.id,source_ids:sources.filter(item=>names.has(item.student_name)).map(item=>item.id)};
        }).filter(Boolean);
        const members=project.members||project.submitters||[{name:project.student_name,reading:project.student_reading}];
        return {...project,week:week.week,members,student_name:members.map(person=>person.name).join(' / '),
          sources,source_ids:sources.map(source=>source.id),primary_id:primary.id,variants,
          heart_keys:[primary.heart_key,...sources.filter(source=>source.id!==primary.id).map(source=>source.heart_key)],submission_count:sources.length};
      }).filter(Boolean);
      // Newly imported, not-yet-exported notebooks stay available for private review.
      mapped.filter(source=>source.week===week.week&&!covered.has(source.id)).forEach(source=>groups.push({
        ...source,id:source.public_id,title:source.title,members:[{name:source.student_name,reading:source.student_reading}],
        sources:[source],source_ids:[source.id],primary_id:source.id,variants:[],heart_keys:[source.heart_key],submission_count:1,unpublished:true
      }));
      return {week:week.week,students:week.students,submissions:week.submissions.length,groups};
    })};
  }
  const api={publicID,keyFor,heartKeys,isSelected,changesFor,build};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.AdminGroups=api;
})(typeof globalThis==='undefined'?this:globalThis);
