document.addEventListener('DOMContentLoaded', function() {
  const button = document.querySelector('.save-contact-btn');
  if (button) {
    button.addEventListener('click', function() {
      const name = button.dataset.name || 'Contact';
      const phone = button.dataset.phone || '';
      const email = button.dataset.email || '';
      const url = button.dataset.website || '';
      const address = button.dataset.address || '';
      const org = button.dataset.org || '';
      const vcf = `BEGIN:VCARD
VERSION:3.0
FN:${name}
ORG:${org}
TEL;TYPE=CELL:${phone}
EMAIL:${email}
URL:${url}
ADR;TYPE=WORK:${address}
END:VCARD`;
      const blob = new Blob([vcf], { type: 'text/vcard;charset=utf-8' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${name.toLowerCase().replace(/\s+/g, '-')}.vcf`;
      link.click();
      URL.revokeObjectURL(link.href);
    });
  }
});
