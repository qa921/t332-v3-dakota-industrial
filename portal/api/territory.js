const crypto=require('node:crypto');
module.exports=(req,res)=>{
res.setHeader('Cache-Control','no-store'); res.setHeader('X-Content-Type-Options','nosniff');
const raw=req.headers.authorization||''; let supplied='';
try { supplied=raw.startsWith('Basic ')?Buffer.from(raw.slice(6),'base64').toString('utf8'):'';} catch {}
const expected='contributor:'+process.env.ACCESS_TOKEN;
const same=process.env.ACCESS_TOKEN && crypto.timingSafeEqual(crypto.createHash('sha256').update(supplied).digest(),crypto.createHash('sha256').update(expected).digest());
if(!same){res.setHeader('WWW-Authenticate','Basic realm="Contributor prerequisite", charset="UTF-8"'); return res.status(401).json({error:'unauthorized'});}
return res.status(503).json({available:false,reason:'Nearby portal integration is not implemented in this baseline'});
};
