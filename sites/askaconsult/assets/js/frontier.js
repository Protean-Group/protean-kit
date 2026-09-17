/* The existing ASKA terminal remains the functional core. */
(()=>{const root=document.getElementById('askterm');if(!root||!window.ASKA_Terminal)return;const terminal=ASKA_Terminal({root,api:'/api/ask',autoFocus:false});document.querySelectorAll('[data-command]').forEach(button=>button.addEventListener('click',()=>terminal.respond(button.dataset.command)));})();
