class KaAnshin extends HTMLElement{
  static get observedAttributes(){return ['sent'];}
  attributeChangedCallback(n,o,v){ if(n!=='sent'||!this.shadowRoot) return; this._sending=false;
    const R=this.shadowRoot,msg=R.getElementById('sent'),btn=R.querySelector('#inq button[type=submit]'); if(!msg) return;
    if(String(v).startsWith('ok')){msg.textContent='送信しました。2営業日以内にご連絡します。';R.getElementById('inq').reset&&R.getElementById('inq').reset();}
    else if(String(v).startsWith('ng')){msg.textContent='送信できませんでした。お手数ですが contact@ak-analytics.jp までご連絡ください。';}
    msg.hidden=false; if(btn) btn.disabled=false; }
  connectedCallback(){
    if(this._done) return; this._done=true;
    if(!window.document.querySelector('link[data-ka-font]')){const l=window.document.createElement('link');l.rel='stylesheet';l.href=FONT;l.setAttribute('data-ka-font','');window.document.head.appendChild(l);}
    const R=this.attachShadow({mode:'open'});
    R.innerHTML='<style>'+CSS+'</style><div class="kroot">'+HTML+'</div>';
    const root=R.querySelector('.kroot');
    const D=window.document;
    const shim={
      querySelector:s=>R.querySelector(s), querySelectorAll:s=>R.querySelectorAll(s),
      getElementById:id=>R.getElementById(id), createElement:n=>D.createElement(n),
      addEventListener:(t,f,o)=>R.addEventListener(t,f,o),
      get activeElement(){return R.activeElement;},
      body:{appendChild:n=>root.appendChild(n), classList:root.classList},
      documentElement:{style:{setProperty:(k,v)=>root.style.setProperty(k,v)}}
    };
    run(shim,R);
    const fit=()=>{const h=root.scrollHeight; if(h&&this._h!==h){this._h=h;this.style.height=h+'px';}};
    new ResizeObserver(fit).observe(root); fit();
  }
}
if(!customElements.get('ka-anshin')) customElements.define('ka-anshin',KaAnshin);
})();
