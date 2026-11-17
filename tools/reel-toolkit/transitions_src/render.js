const {chromium}=require('playwright');const fs=require('fs'),path=require('path');
const TR=__dirname;
const T={navy_wipe:18,gold_light_sweep:15,whip_blur_mask:12,circle_iris_gold:18,split_bars:21,particle_dissolve:24};
(async()=>{
  const only=process.argv.slice(2);
  const b=await chromium.launch();
  for(const [name,N] of Object.entries(T)){
    if(only.length&&!only.includes(name))continue;
    const dir=path.join(TR,name);fs.rmSync(dir,{recursive:true,force:true});fs.mkdirSync(dir,{recursive:true});
    const pg=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
    await pg.goto('file://'+path.join(TR,'src',name+'.html'));
    await pg.waitForFunction('window.ready===true');
    for(let i=0;i<N;i++){
      await pg.evaluate(t=>window.seek(t),i/30);
      await pg.screenshot({path:path.join(dir,String(i+1).padStart(4,'0')+'.png'),omitBackground:true});
    }
    await pg.close();console.log(name,N);
  }
  await b.close();
})();
