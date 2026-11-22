/**
 * Latine Mayfair – website forms → Google Sheet + email   (version 2: spam protection)
 * Paste into Extensions > Apps Script on the "Latine Website Enquiries" sheet, replacing everything.
 * Then Deploy > Manage deployments > pencil icon > Version: New version > Deploy.
 * (Do NOT choose "New deployment": that would change the web address the site posts to.)
 */
const NOTIFY = 'contact@latinemayfair.com';          // who gets the enquiry emails (comma-separate for more)
const ENQ_COLS = ['Received', 'Form', 'Occasion', 'Name', 'Company', 'Email', 'Phone', 'Preferred date', 'Guests', 'Time', 'Space', 'Message', 'Page'];
const SUB_COLS = ['Received', 'Form', 'Email', 'Page'];
const SALT = 'latine-w1s';       // must match the website
const MIN_MS = 1500;             // a person cannot open the page and submit faster than this
const MAX_PER_EMAIL = 3;         // submissions allowed from one email address per hour

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

// same check code the website computes for every genuine submission
function sig(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(16); }

// things real enquiries almost never contain; these still come through, but the email subject is marked
function looksLikeSpam(p) {
  const text = [p.name, p.company, p.message].join(' ');
  return /https?:\/\/|www\.|\.(ru|cn|xyz|top|click|link)\b|\[url|<a\s/i.test(text) || /[Ѐ-ӿ]/.test(text);
}

function doPost(e) {
  const p = e.parameter || {};
  if (p.website || p.enquiry_ref) return out({ ok: true });                 // hidden trap field was filled in: a bot
  const email = String(p.email || '').trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return out({ ok: false, error: 'email' });

  // must come from the website itself: carries the right check code and was not submitted instantly
  const d = String(p.d || '');
  if (!p.k || p.k !== sig(email.toLowerCase() + '|' + d + '|' + SALT) || !(Number(d) >= MIN_MS)) return out({ ok: false, error: 'verify' });

  // one address cannot flood the sheet
  const cache = CacheService.getScriptCache(), key = 'n:' + email.toLowerCase();
  const n = Number(cache.get(key) || 0) + 1; cache.put(key, String(n), 3600);
  if (n > MAX_PER_EMAIL) return out({ ok: true });

  const lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    const ss = SpreadsheetApp.getActive();
    const form = p.form || 'Website form';
    const now = new Date();
    if (form === 'Events enquiry') {
      const row = [now, form, p.occasion, p.name, p.company, email, p.phone, p.date, p.guests, p.time, p.space, p.message, p.page];
      ss.getSheetByName('Enquiries').appendRow(row.map(v => v || ''));
      const body = ENQ_COLS.slice(2).map((c, i) => row[i + 2] ? c + ': ' + row[i + 2] : null).filter(Boolean).join('\n');
      try {
        MailApp.sendEmail({
          to: NOTIFY, replyTo: email, name: 'Latine Mayfair website',
          subject: (looksLikeSpam(p) ? '[Possible spam] ' : '') + (p.occasion || 'Enquiry') + ' – ' + (p.name || email) + (p.date ? ' – ' + p.date : ''),
          body: 'New enquiry from latinemayfair.com\n\n' + body + '\n\nAll enquiries: ' + ss.getUrl()
        });
      } catch (mailErr) { /* the enquiry is already saved in the sheet, so the guest still gets a thank-you */ }
    } else {
      ss.getSheetByName('Sign-ups').appendRow([now, form, email, p.page || '']);
    }
    return out({ ok: true });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  } finally { lock.releaseLock(); }
}

function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
