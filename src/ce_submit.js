$('#inq').addEventListener('submit',e=>{e.preventDefault();
  const v=id=>(R.getElementById(id)||{}).value||'';
  const pick=sel=>[...R.querySelectorAll(sel)].map(i=>i.value);
  const d={area:(R.querySelector('input[name="area"]:checked')||{}).value||'',role:(R.querySelector('input[name="role"]:checked')||{}).value||'',
    issues:pick('#qIssues input:checked'),interests:pick('#qInterest input:checked'),
    company:v('f-company').trim(),name:v('f-name').trim(),email:v('f-mail').trim(),tel:v('f-tel').trim(),message:v('f-msg').trim(),
    source:($('#fromId')||{}).textContent||''};
  const msg=$('#sent');
  if(!d.company||!d.name||!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(d.email)){msg.textContent='会社名・お名前・メールアドレスを入力してください。';msg.hidden=false;return;}
  const btn=R.querySelector('#inq button[type=submit]');btn.disabled=true;msg.textContent='送信しています…';msg.hidden=false;
  R.host._sending=true;
  R.host.dispatchEvent(new CustomEvent('ka-submit',{detail:d,bubbles:true,composed:true}));
  setTimeout(()=>{if(R.host._sending){btn.disabled=false;msg.textContent='送信できませんでした。お手数ですが contact@ak-analytics.jp までご連絡ください。';}},15000);
});