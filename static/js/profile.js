document.addEventListener('DOMContentLoaded', function() {
  const status = document.querySelector('.action-status');
  const setStatus = (message) => {
    if (status) status.textContent = message;
  };

  const btn = document.querySelector('.save-contact-btn');
  if (btn) {
    btn.addEventListener('click', () => {
      const name = btn.dataset.name || 'Contact';
      const phone = btn.dataset.phone || '';
      const email = btn.dataset.email || '';
      const org = btn.dataset.org || 'Organization';
      const website = btn.dataset.website || '';
      const address = btn.dataset.address || '';
      const escapeVCardValue = (value) => value
        .replace(/\\/g, '\\\\')
        .replace(/\r\n|\r|\n/g, '\\n')
        .replace(/([,;])/g, '\\$1');
      const vcard = [
        'BEGIN:VCARD',
        'VERSION:3.0',
        `FN:${escapeVCardValue(name)}`,
        `ORG:${escapeVCardValue(org)}`,
        phone ? `TEL;TYPE=CELL:${escapeVCardValue(phone)}` : '',
        email ? `EMAIL:${escapeVCardValue(email)}` : '',
        website ? `URL:${escapeVCardValue(website)}` : '',
        address ? `ADR;TYPE=WORK:;;${escapeVCardValue(address)}` : '',
        'END:VCARD',
      ].filter(Boolean).join('\r\n');
      const blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${name.replace(/\s+/g, '-').toLowerCase()}.vcf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setStatus('Contact download started');
    });
  }

  const copyLink = async () => {
    const link = window.location.href;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(link);
      } else {
        throw new Error('Clipboard API unavailable');
      }
      setStatus('Link copied');
    } catch {
      const input = document.createElement('textarea');
      input.value = link;
      input.setAttribute('readonly', '');
      input.style.position = 'fixed';
      input.style.opacity = '0';
      document.body.appendChild(input);
      input.select();
      let copied = false;
      try {
        copied = document.execCommand('copy');
      } catch {
        copied = false;
      }
      document.body.removeChild(input);
      setStatus(copied ? 'Link copied' : 'Could not copy the link. Copy it from the address bar.');
    }
  };

  const copyButton = document.querySelector('.copy-link-btn');
  if (copyButton) copyButton.addEventListener('click', copyLink);

  const shareButton = document.querySelector('.share-profile-btn');
  if (shareButton) {
    shareButton.addEventListener('click', async () => {
      if (navigator.share) {
        try {
          await navigator.share({ title: document.title, url: window.location.href });
        } catch (error) {
          if (error.name !== 'AbortError') setStatus('Sharing was not available');
        }
      } else {
        await copyLink();
      }
    });
  }

  const whatsappShare = document.querySelector('.whatsapp-share-btn');
  if (whatsappShare) {
    whatsappShare.addEventListener('click', async (event) => {
      if (!navigator.share || !navigator.canShare || typeof File === 'undefined') return;

      event.preventDefault();
      try {
        const response = await fetch(whatsappShare.dataset.shareImage);
        if (!response.ok) throw new Error('Share image could not be loaded');
        const image = new File(
          [await response.blob()],
          `${whatsappShare.dataset.profileName || 'profile'}-card.png`,
          { type: 'image/png' },
        );
        const shareData = {
          title: document.title,
          text: `View ${whatsappShare.dataset.profileName}'s digital profile: ${whatsappShare.dataset.profileUrl}`,
          url: whatsappShare.dataset.profileUrl,
          files: [image],
        };
        if (navigator.canShare({ files: [image] })) {
          await navigator.share(shareData);
        } else {
          window.location.href = whatsappShare.href;
        }
      } catch (error) {
        if (error.name !== 'AbortError') window.location.href = whatsappShare.href;
      }
    });
  }
});
