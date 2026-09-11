const menuButton = document.querySelector('.menu-button');
const menu = document.querySelector('#primary-nav');
function closeMenu() { menu.classList.remove('open'); menuButton.setAttribute('aria-expanded', 'false'); }
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open)); menu.classList.toggle('open', open);
});
document.addEventListener('keydown', event => { if (event.key === 'Escape' && menu.classList.contains('open')) { closeMenu(); menuButton.focus(); } });
menu?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('click', event => { if (!event.target.closest('.site-header')) closeMenu(); });

document.querySelectorAll('.play-demo').forEach(button => button.addEventListener('click', async () => {
  const host = button.closest('[data-movie]');
  const status = host.querySelector('.player-status');
  button.disabled = true; status.textContent = 'Loading demonstration…';
  try {
    window.RufflePlayer = window.RufflePlayer || {};
    window.RufflePlayer.config = {autoplay:'off',unmuteOverlay:'hidden',allowScriptAccess:false,backgroundColor:'#ffffff',letterbox:'on',warnOnUnsupportedContent:true};
    if (!window.RufflePlayer.newest) await new Promise((resolve,reject) => {
      const script = document.createElement('script'); script.src = '/assets/ruffle/ruffle.js';
      script.onload = resolve; script.onerror = reject; document.head.appendChild(script);
    });
    const player = window.RufflePlayer.newest().createPlayer();
    player.setAttribute('title', host.getAttribute('aria-label'));
    host.appendChild(player);
    await player.ruffle().load({url:host.dataset.movie,autoplay:'on',allowScriptAccess:false});
    button.remove(); status.remove();
  } catch (error) {
    host.querySelector('ruffle-player')?.remove();
    status.textContent = 'The demonstration could not load. Try again, or download the original file below.';
    button.disabled = false;
  }
}));
