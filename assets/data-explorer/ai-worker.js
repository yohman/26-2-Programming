// Inference stays in this worker. User text is never sent to an inference API.
const model='Xenova/distilbert-base-multilingual-cased-sentiments-student';
let classifier;
self.onmessage=async event=>{
  if(event.data.type!=='analyze')return;
  try {
    if(!classifier) {
      const {pipeline,env}=await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.2/dist/transformers.min.js');
      env.allowLocalModels=false;
      env.backends.onnx.wasm.numThreads=1;
      env.backends.onnx.wasm.proxy=false;
      classifier=await pipeline('text-classification',model,{
        device:'wasm',dtype:'q8',
        progress_callback:progress=>{
          if(progress.status==='progress')self.postMessage({type:'progress',file:progress.file,progress:Math.round(progress.progress||0)});
          else if(progress.status==='ready')self.postMessage({type:'ready'});
        }
      });
    }
    self.postMessage({type:'running'});
    const output=await classifier(event.data.text,{top_k:null,truncation:true,max_length:256});
    self.postMessage({type:'result',model,input:event.data.text,output});
  }catch(error){classifier=null;self.postMessage({type:'error',message:String(error.message||error)});}
};
