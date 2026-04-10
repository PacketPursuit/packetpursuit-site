/* ===== PacketPursuit, vault.js =====
 * The flag is stored plainly as a readable JS constant.
 * Source-code discovery is an intentional alternate solve path.
 * Primary path is in robots.txt. Look where machines aren't meant to look.
 */

const VAULT_FLAG = 'PP{OfF_th3_cL0ck}';
const VAULT_STORAGE_KEY = 'vault_unlocked';

document.addEventListener('DOMContentLoaded', () => {
    const lockedEl = document.getElementById('vault-locked');
    const unlockedEl = document.getElementById('vault-unlocked');
    const form = document.getElementById('vault-form');
    const input = document.getElementById('vault-input');
    const denied = document.getElementById('vault-denied');

    // If session already unlocked, skip straight to unlocked state.
    if (sessionStorage.getItem(VAULT_STORAGE_KEY) === 'true') {
        revealUnlocked(lockedEl, unlockedEl, true);
        return;
    }

    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const value = (input.value || '').trim();

        if (value === VAULT_FLAG) {
            // Correct: terminal wipe animation, then reveal.
            if (denied) denied.classList.remove('visible');
            lockedEl.classList.add('vault-wipe');
            setTimeout(() => {
                sessionStorage.setItem(VAULT_STORAGE_KEY, 'true');
                revealUnlocked(lockedEl, unlockedEl, false);
            }, 750);
        } else {
            // Wrong: red flash + ACCESS DENIED message.
            if (denied) denied.classList.add('visible');
            lockedEl.classList.remove('flash-denied');
            // Force reflow so the animation can replay
            void lockedEl.offsetWidth;
            lockedEl.classList.add('flash-denied');
            input.select();
        }
    });
});

function revealUnlocked(lockedEl, unlockedEl, skipFade) {
    if (lockedEl) lockedEl.style.display = 'none';
    if (unlockedEl) {
        unlockedEl.style.display = 'block';
        if (!skipFade) {
            unlockedEl.classList.add('vault-reveal');
        }
    }
}

// ===== SECTION TOGGLE =====
function toggleVaultSection(header) {
    const section = header.closest('.vault-section');
    if (!section) return;
    section.classList.toggle('collapsed');
}
