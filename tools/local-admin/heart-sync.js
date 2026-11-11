/* Optimistic selections with a serial, coalescing save queue. */
(function(root){
  function create({initial=[],pending={},send,persist=()=>{},onChange=()=>{},onStatus=()=>{},delay=120,retry=1000,timers=root}){
    let saved=new Set(initial),changes={...pending},values=new Set(),running=false,timer=null,stopped=false;
    const rebuild=()=>{const next=new Set(saved);for(const [key,on] of Object.entries(changes))on?next.add(key):next.delete(key);const different=values.size!==next.size||[...values].some(key=>!next.has(key));values=next;persist([...values],{...changes});if(different)onChange(new Set(values));};
    function schedule(wait=delay){if(stopped)return;timers.clearTimeout(timer);timer=timers.setTimeout(flush,wait);}
    async function flush(){
      if(stopped||running||!Object.keys(changes).length)return;
      timers.clearTimeout(timer);timer=null;running=true;
      const sent={...changes};let failed=false,report={saving:false};
      onStatus({saving:true});
      try{
        const result=await send(sent);
        saved=new Set(result.hearts);
        for(const [key,on] of Object.entries(sent))if(changes[key]===on)delete changes[key];
        rebuild();report={saving:!!Object.keys(changes).length,sync:result.sync};
      }catch(error){failed=true;report={error,saving:false};}
      finally{running=false;onStatus(report);if(Object.keys(changes).length)schedule(failed?retry:delay);}
    }
    rebuild();if(Object.keys(changes).length)schedule();
    return {
      toggle(key){changes[key]=!values.has(key);rebuild();onStatus({saving:true});schedule();},
      accept(hearts){saved=new Set(hearts);rebuild();},
      get values(){return new Set(values);},get pending(){return {...changes};},
      get busy(){return running||!!Object.keys(changes).length;},flush,
      stop(){stopped=true;timers.clearTimeout(timer);}
    };
  }
  const api={create};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.HeartSync=api;
})(typeof globalThis==='undefined'?this:globalThis);
