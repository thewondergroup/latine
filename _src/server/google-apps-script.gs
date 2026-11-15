/**
 * Latine Mayfair – website forms → Google Sheet + email
 * Paste into Extensions > Apps Script on the "Latine Website Enquiries" sheet.
 * Run setup() once, then Deploy > New deployment > Web app (Execute as: Me, Access: Anyone).
 */
const NOTIFY = 'contact@latinemayfair.com';          // who gets the enquiry emails (comma-separate for more)
const ENQ_COLS = ['Received', 'Form', 'Occasion', 'Name', 'Company', 'Email', 'Phone', 'Preferred date', 'Guests', 'Time', 'Space', 'Message', 'Page'];
const SUB_COLS = ['Received', 'Form', 'Email', 'Page'];

function setup() {
  const ss = SpreadsheetApp.getActive();
  [['Enquiries', ENQ_COLS], ['Sign-ups', SUB_COLS]].forEach(([name, cols]) => {
    const sh = ss.getSheetByName(name) || ss.insertSheet(name);
    sh.getRange(1, 1, 1, cols.length).setValues([cols]).setFontWeight('bold');
    sh.setFrozenRows(1);
  });
  const s1 = ss.getSheetByName('Sheet1'); if (s1 && ss.getSheets().length > 2) ss.deleteSheet(s1);
  MailApp.getRemainingDailyQuota();   // triggers the email permission prompt
}

function doPost(e) {
  const p = e.parameter || {};
  if (p.website) return out({ ok: true });                       // spam trap
  const email = String(p.email || '').trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return out({ ok: false, error: 'email' });

  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.getActive();
    const form = p.form || 'Website form';
    const now = new Date();
    if (form === 'Events enquiry') {
      const row = [now, form, p.occasion, p.name, p.company, email, p.phone, p.date, p.guests, p.time, p.space, p.message, p.page];
      ss.getSheetByName('Enquiries').appendRow(row.map(v => v || ''));
      const body = ENQ_COLS.slice(2).map((c, i) => row[i + 2] ? c + ': ' + row[i + 2] : null).filter(Boolean).join('\n');
      MailApp.sendEmail({
        to: NOTIFY, replyTo: email, name: 'Latine Mayfair website',
        subject: (p.occasion || 'Enquiry') + ' – ' + (p.name || email) + (p.date ? ' – ' + p.date : ''),
        body: 'New enquiry from latinemayfair.com\n\n' + body + '\n\nAll enquiries: ' + ss.getUrl()
      });
    } else {
      ss.getSheetByName('Sign-ups').appendRow([now, form, email, p.page || '']);
    }
    return out({ ok: true });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  } finally { lock.releaseLock(); }
}

function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
