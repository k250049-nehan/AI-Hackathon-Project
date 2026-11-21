/* Last Mile prototype UI - low literacy, voice first, offline tolerant.
   All icons are drawn inline SVG; no emoji are used anywhere in this interface. */
'use strict';

const ICONS = {
  check: '<path d="m5 12 4 4L19 6"/>',
  cross: '<path d="M6 6 18 18"/><path d="M18 6 6 18"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  clipboard: '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2h6v2"/><path d="M9 10h6M9 14h6"/>',
  doc: '<path d="M6 3h8l4 4v14H6V3Z"/><path d="M14 3v4h4"/>'
};

function svgIcon(name, className = 'icon') {
  return '<svg class="' + className + '" viewBox="0 0 24 24" aria-hidden="true">' +
    (ICONS[name] || ICONS.doc) + '</svg>';
}

const I18N = {
  en: {
    appName: 'Last Mile', loginSub: 'Relief payment help — prototype', email: 'Email',
    password: 'Password', signIn: 'Sign in', demoRoles: 'Demo roles',
    showPassword: 'Show password', hidePassword: 'Hide password',
    demoHint: 'Demo password: Demo@123. Every record is fake.',
    yourProgress: 'Your progress', loading: 'Loading…', speakRequest: 'Speak your request',
    stopRecording: 'Stop recording',
    micHint: 'Tap the microphone and say what you need.', send: 'Send', refresh: 'Refresh',
    myCases: 'My cases', help: 'Help / Ask a question', ask: 'Ask', home: 'Home', cases: 'Cases',
    helpShort: 'Help', typeHere: 'Or type here',
    typePlaceholder: 'My name is Muhammad Ahmed, CNIC 12345-6789012-3. I am unemployed in Lahore. My monthly income is 18000. I need 5000. This is my claim for relief.',
    claimDetailsTitle: 'Claim details',
    claimDetailsHint: 'The microphone fills these as you speak and asks for anything missing. Check them before sending. Fields marked * are required.',
    claimFillNote: 'Filled from your words — check them.',
    fullNameLabel: 'Full name', cnicLabel: 'CNIC', districtLabel: 'District',
    categoryLabel: 'Category', incomeLabel: 'Monthly income (PKR)',
    amountLabel: 'Claim amount (PKR)', dependentsLabel: 'Dependents (optional)',
    fullNamePlaceholder: 'Muhammad Ahmed', cnicPlaceholder: '12345-6789012-3',
    districtPlaceholder: 'Lahore', incomePlaceholder: '18000', amountPlaceholder: '5000',
    dependentsPlaceholder: '0', chooseCategory: 'Choose category',
    categoryWidow: 'Widow', categoryDisabled: 'Disabled',
    categoryUnemployed: 'Unemployed', categoryLowIncome: 'Low income',
    requestLabel: 'Your request',
    fieldRequired: name => name + ' is required.',
    invalidCnic: 'CNIC must contain 13 digits.',
    invalidNumber: 'Enter a whole number.',
    amountTooHigh: 'Claim amount is too high for this income.',
    fixFields: 'Please check the highlighted claim details.',
    voiceAsk: {
      full_name: 'Please tell me your full name.',
      cnic: 'Please tell me your CNIC number.',
      district: 'Please tell me your district.',
      category: 'Please tell me your category: widow, disabled, unemployed, or low income.',
      monthly_income: 'Please tell me your monthly income in rupees.',
      claim_amount: 'Please tell me how much money you need.'
    },
    voiceAskGeneric: field => 'Please tell me your ' + field + '.',
    voiceAwaiting: field => 'Listening for: ' + field + '.',
    voiceFieldSaved: field => 'Added: ' + field + '.',
    voiceFieldMissed: field => 'I did not catch the ' + field + '. Please try again.',
    voiceAllDone: 'All details are ready. Check them, then press Send.',
    askPlaceholder: 'What is the income limit?',
    statusNone: 'No cases yet. Speak your request to begin.',
    statusSome: c => 'Case ' + c.case_number + ': ' + statusLabel(c.status) + '. ' + statusReason(c),
    confidence: 'Confidence',
    statusLabels: {
      new: 'New', assigned: 'Assigned', needs_info: 'Needs information', human_review: 'Human review',
      pending_officer: 'Waiting for officer', approved: 'Approved', rejected: 'Rejected',
      blocked: 'Blocked', auto_block: 'Blocked as scam', escalated: 'Sent to senior officer'
    },
    prototypeNotice: 'PROTOTYPE — NOT AN OFFICIAL SERVICE — ALL DATA MOCKED',
    online: 'Online', offlineSaved: 'Offline — saved on device',
    citizen: 'Citizen', helperRole: 'Helper', officer: 'Officer', admin: 'Admin', auditor: 'Auditor',
    roleCitizenTitle: 'Citizen workspace',
    roleCitizenIntro: 'Speak or type a relief request, then track your case. Nothing is shared unless you grant consent.',
    roleHelperTitle: 'Helper workspace',
    roleHelperIntro: 'One phone for 40 mock families. Each family needs its own consent before you act for them.',
    roleOfficerTitle: 'Officer workspace',
    roleOfficerIntro: 'Review pending cases. AI never releases payment; your decision is the approval gate.',
    roleAdminTitle: 'Admin workspace',
    roleAdminIntro: 'Publish rule versions and inspect mock services. Old cases keep the rule version they used.',
    roleAuditorTitle: 'Auditor workspace',
    roleAuditorIntro: 'Read-only audit trail, consent events, and AI decision traces. No case data is edited here.',
    roleServerCheck: 'Permissions are checked on the server, not only in this screen.',
    helperFamilies: 'Families on this shared phone',
    officerQueue: 'Review queue',
    adminRules: 'Rules and mock services',
    auditorTrail: 'Recent audit activity',
    nothingHere: 'Nothing to show right now.',
    mockNotice: 'All records are mock.',
    yes: 'Yes', no: 'No',
    approve: 'Approve', reject: 'Reject', askInfo: 'Ask for info',
    reviewSaved: 'Review saved.',
    ruleActive: 'Active rule', ruleVersions: 'rule versions', ruleRequiresOfficer: 'Officer approval required',
    auditAction: 'action',
    changeLanguage: 'Change language', syncSaved: 'Sync saved requests', signOut: 'Sign out',
    readStatus: 'Read status aloud', mainNav: 'Main navigation', progress: 'Progress',
    checkEmail: 'Please enter a valid email address.', checkPassword: 'Please enter your password.',
    badCredentials: 'That email and password do not match. Please try again.',
    roleLoadFailed: 'Could not load this workspace. Try again.', retry: 'Retry',
    enterRequest: 'Please speak or type your request.',
    networkFailed: 'No connection. Please try again.',
    serverFailed: 'The service is not responding. Please try again shortly.',
    requestFailed: 'That did not work. Please try again.',
    sessionExpired: 'Your session ended. Please sign in again.',
    savedCase: c => 'Saved: ' + c,
    noSignalSaved: 'No signal. Your request is saved on this phone. Tap sync when online.',
    offlineVoiceSaved: 'Saved. Sync when the network returns.',
    micBusy: 'The microphone is busy. Please try again.',
    micFailed: 'Voice recognition stopped. Please try again or type your request.',
    micNetwork: () => navigator.onLine
      ? (state.lang === 'ur'
        ? 'Urdu voice recognition is not working in this browser right now. Your internet is online. Type your request, or switch the app language to English and speak.'
        : 'The voice recognition service is not available right now, even though you are online. Please type your request and try again later.')
      : 'Voice recognition needs an internet connection. Please type your request instead.',
    micTryingLocale: locale => 'Trying another Urdu recognition setting (' + locale + ')…',
    micNoDevice: 'No microphone was found. Check your device, or type your request.',
    micLangUnsupported: () => state.lang === 'ur'
      ? 'Urdu dictation is not supported by this browser. Type your request, or switch the app language to English and speak.'
      : 'This dictation language is not supported by your browser. Please type your request.',
    micPermission: 'Microphone access was blocked. Allow it in your browser, or type instead.',
    micUnsupported: 'Voice input is not supported in this browser. Please type your request.',
    transcriptReady: 'Words added below. Check them, edit if needed, then press Send.',
    noAudio: 'No voice was picked up. Check your microphone, then try again or type your request.',
    noTranscript: () => state.lang === 'ur'
      ? 'Your voice was picked up, but this browser did not recognise Urdu speech. Type your request, or switch to English and speak.'
      : 'Your voice was picked up, but this browser did not turn it into words. Please try again or type your request.',
    micOnQuiet: 'Microphone is on — speak now.',
    micHearing: 'Your voice is coming through.',
    nothingToSync: 'Nothing to sync right now.',
    synced: (processed, duplicates) => 'Synced ' + processed + ' saved request(s). Duplicates skipped: ' + duplicates + '.',
    syncFailed: detail => 'Saved on this phone. Will retry: ' + detail,
    askQuestion: 'Please type a question first.',
    statusLoadFailed: 'Could not load your status. Tap Refresh.',
    storageFull: 'No space on this phone. Sync saved requests first.',
    welcome: 'Welcome. Speak your request.',
    voiceSaved: 'We saved your request. A human will check it before any payment.',
    voiceSavedMissing: list => 'We saved your request. We still need: ' + list + '. Please answer by voice.',
    urduVoiceMissing: 'No Urdu voice is available in this browser. The words are shown on screen and you can still type. On Windows, open this demo in Microsoft Edge — it provides online Urdu voices with no settings changes — then reload.',
    refreshCases: 'Refresh cases', voiceSetup: 'Voice setup',
    voiceHelp: 'Urdu speech works in Microsoft Edge on Windows. Chrome reads only voices installed on your device. Check below, or type instead.',
    checkVoices: 'Check voices', testUrdu: 'Test Urdu',
    voicesFound: n => 'Voices available on this device: ' + n + '.',
    urduVoiceReady: names => 'Urdu voice ready: ' + names + '. Urdu speech will work.',
    urduVoiceMissingShort: 'No Urdu voice is available here. On Windows, open this demo in Microsoft Edge — it provides online Urdu voices without any Windows Settings changes — then check again. Typing always works.',
    testUrduText: 'آپ کی درخواست محفوظ ہو گئی۔ ایک انسان اسے چیک کرے گا۔',
    ttsUnsupported: 'This browser cannot read text aloud. The words are shown on screen.',
    fieldNames: {
      full_name: 'full name', cnic: 'CNIC', monthly_income: 'monthly income',
      claim_amount: 'claim amount', district: 'district',
      category: 'category', dependents: 'dependents'
    }
  },
  ur: {
    appName: 'آخری میل', loginSub: 'ریلیف ادائیگی میں مدد — پروٹو ٹائپ', email: 'ای میل',
    password: 'پاس ورڈ', signIn: 'سائن اِن', demoRoles: 'ڈیمو کردار',
    showPassword: 'پاس ورڈ دکھائیں', hidePassword: 'پاس ورڈ چھپائیں',
    demoHint: 'ڈیمو پاس ورڈ: Demo@123۔ ہر ریکارڈ جعلی ہے۔',
    yourProgress: 'آپ کی پیش رفت', loading: 'لوڈ ہو رہا ہے…', speakRequest: 'اپنی بات کہیں',
    stopRecording: 'ریکارنگ بند کریں',
    micHint: 'مائیکروفون دبائیں اور بتائیں کہ آپ کو کیا چاہیے۔', send: 'بھیجیں', refresh: 'تازہ کاری',
    myCases: 'میرے کیسز', help: 'مدد / سوال پوچھیں', ask: 'پوچھیں', home: 'ہوم', cases: 'کیسز',
    helpShort: 'مدد', typeHere: 'یا یہاں لکھیں',
    typePlaceholder: 'میرا نام Aisha Khatoon ہے۔ شناختی نمبر 11111-2222233-3۔ میں کم آمدنی والی ہوں اور میری رہائش Hyderabad میں ہے۔ میری ماہانہ آمدنی 9000 روپے ہے۔ مجھے 3000 روپے چاہیے۔ یہ میری رلیف ادائیگی کی درخواست ہے۔',
    claimDetailsTitle: 'دعویٰ کی تفصیلات',
    claimDetailsHint: 'مائیکروفون بولتے ہی یہ خانے بھرتا ہے اور جو باقی رہے وہ پوچھتا ہے۔ بھیجنے سے پہلے انہیں چیک کریں۔ * والے خانے ضروری ہیں۔',
    claimFillNote: 'آپ کی بات سے بھرا گیا — چیک کریں۔',
    fullNameLabel: 'مکمل نام', cnicLabel: 'شناختی نمبر', districtLabel: 'ضلع',
    categoryLabel: 'زمرہ', incomeLabel: 'ماہانہ آمدنی (روپے)',
    amountLabel: 'دعویٰ کی رقم (روپے)', dependentsLabel: 'زیرِ کفالت (اختیاری)',
    fullNamePlaceholder: 'Aisha Khatoon', cnicPlaceholder: '11111-2222233-3',
    districtPlaceholder: 'Hyderabad', incomePlaceholder: '9000', amountPlaceholder: '3000',
    dependentsPlaceholder: '0', chooseCategory: 'زمرہ منتخب کریں',
    categoryWidow: 'بیوہ', categoryDisabled: 'معذور',
    categoryUnemployed: 'بے روزگار', categoryLowIncome: 'کم آمدنی',
    requestLabel: 'آپ کی درخواست',
    fieldRequired: name => name + ' ضروری ہے۔',
    invalidCnic: 'شناختی نمبر میں 13 ہندسے ہونے چاہیں۔',
    invalidNumber: 'پورا نمبر لکھیں۔',
    amountTooHigh: 'اس آمدنی کے لیے دعویٰ کی رقم بہت زیادہ ہے۔',
    fixFields: 'براہِ کرم نمایاں دعویٰ کی تفصیلات چیک کریں۔',
    voiceAsk: {
      full_name: 'براہِ کرم اپنا مکمل نام بتائیں۔',
      cnic: 'براہِ کرم اپنا شناختی نمبر بتائیں۔',
      district: 'براہِ کرم اپنا ضلع بتائیں۔',
      category: 'براہِ کرم اپنا زمرہ بتائیں: بیوہ، معذور، بے روزگار، یا کم آمدنی۔',
      monthly_income: 'براہِ کرم اپنی ماہانہ آمدنی روپوں میں بتائیں۔',
      claim_amount: 'براہِ کرم بتائیں کہ آپ کو کتنی رقم چاہیے۔'
    },
    voiceAskGeneric: field => 'براہِ کرم اپنا ' + field + ' بتائیں۔',
    voiceAwaiting: field => field + ' سننے کے لیے تیار ہیں۔',
    voiceFieldSaved: field => field + ' شامل ہو گیا۔',
    voiceFieldMissed: field => field + ' نہیں سمجھ آیا۔ دوبارہ کوشش کریں۔',
    voiceAllDone: 'تمام تفصیلات تیار ہیں۔ انہیں چیک کریں اور بھیجیں دبائیں۔',
    askPlaceholder: 'آمدنی کی حد کیا ہے؟',
    statusNone: 'ابھی کوئی کیس نہیں۔ شروع کرنے کے لیے اپنی بات کہیں۔',
    statusSome: c => 'کیس ' + c.case_number + ': ' + statusLabel(c.status) + '.',
    confidence: 'اعتماد',
    statusLabels: {
      new: 'نیا', assigned: 'تفویض شدہ', needs_info: 'مزید معلومات درکار', human_review: 'انسانی جائزہ',
      pending_officer: 'افسر کے انتظار میں', approved: 'منظور', rejected: 'مسترد',
      blocked: 'بند', auto_block: 'دھوکا دہی کے طور پر بند', escalated: 'سینئر افسر کو بھیجا گیا'
    },
    prototypeNotice: 'پروٹو ٹائپ — کوئی سرکاری خدمہ نہیں — تمام ڈیٹا جعلی ہے',
    online: 'آن لائن', offlineSaved: 'آف لائن — ڈیوائس پر محفوظ',
    citizen: 'شہری', helperRole: 'مددگار', officer: 'افسر', admin: 'منتظم', auditor: 'آڈیٹر',
    roleCitizenTitle: 'شہری کا کام کی جگہ',
    roleCitizenIntro: 'ریلیف کی درخواست بول کر یا لکھ کر دیں، پھر اپنا کیس دیکھیں۔ آپ کی اجازت کے بغیر کوئی ڈیٹا شیئر نہیں ہوتا۔',
    roleHelperTitle: 'مددگار کا کام کی جگہ',
    roleHelperIntro: 'ایک فون 40 جعلی خاندانوں کے لیے۔ ہر خاندان کے لیے الگ اجازت ضروری ہے۔',
    roleOfficerTitle: 'افسر کا کام کی جگہ',
    roleOfficerIntro: 'زیرِ جائزہ کیس دیکھیں۔ AI ادائیگی نہیں کرتا؛ فیصلہ آپ کی منظوری کے بغیر نہیں ہوتا۔',
    roleAdminTitle: 'منتظم کا کام کی جگہ',
    roleAdminIntro: 'قواعد کے نئے ورژن شائع کریں اور جعلی سروسز دیکھیں۔ پرانے کیس اپنا پرانا ورژن دکھاتے رہتے ہیں۔',
    roleAuditorTitle: 'آڈیٹر کا کام کی جگہ',
    roleAuditorIntro: 'صرف پڑھنے کے لیے آڈیٹ لاگ، اجازت کے واقعات، اور AI فیصلوں کے traces۔ یہاں ڈیٹا تبدیل نہیں ہوتا۔',
    roleServerCheck: 'اجازت صرف اس اسکرین میں نہیں، سرور پر بھی چیک کی جاتی ہے۔',
    helperFamilies: 'اس مشترکہ فون پر خاندان',
    officerQueue: 'جائزہ قطار',
    adminRules: 'قواعد اور جعلی سروسز',
    auditorTrail: 'حالیہ آڈیٹ سرگرمی',
    nothingHere: 'ابھی دکھانے کے لیے کچھ نہیں۔',
    mockNotice: 'تمام ریکارڈ جعلی ہیں۔',
    yes: 'ہاں', no: 'نہیں',
    approve: 'منظور', reject: 'مسترد', askInfo: 'مزید معلومات',
    reviewSaved: 'جائزہ محفوظ ہو گیا۔',
    ruleActive: 'فعال قاعدہ', ruleVersions: 'قاعدے کے ورژن', ruleRequiresOfficer: 'افسر کی منظوری ضروری',
    auditAction: 'عمل',
    changeLanguage: 'زبان تبدیل کریں', syncSaved: 'محفوظ درخواستیں ہم آہنگ کریں', signOut: 'سائن آؤٹ',
    readStatus: 'صورت حال بلند آواز سے سنیں', mainNav: 'مرکزی نیویگیشن', progress: 'پیش رفت',
    checkEmail: 'براہِ کرم درست ای میل داخل کریں۔', checkPassword: 'براہِ کرم پاس ورڈ داخل کریں۔',
    badCredentials: 'یہ ای میل اور پاس ورڈ میل نہیں کھاتے۔ دوبارہ کوشش کریں۔',
    roleLoadFailed: 'یہ کام کی جگہ لوڈ نہیں ہو سکی۔ دوبارہ کوشش کریں۔', retry: 'دوبارہ کوشش',
    enterRequest: 'براہِ کرم بول کر یا لکھ کر اپنی بات بتائیں۔',
    networkFailed: 'کوئی کنکشن نہیں۔ دوبارہ کوشش کریں۔',
    serverFailed: 'سروس جواب نہیں دے رہی۔ ذرا بعد دوبارہ کوشش کریں۔',
    requestFailed: 'یہ کام نہیں ہوا۔ دوبارہ کوشش کریں۔',
    sessionExpired: 'آپ کا سیشن ختم ہو گیا۔ دوبارہ سائن اِن کریں۔',
    savedCase: c => 'محفوظ: ' + c,
    noSignalSaved: 'کوئی سگنل نہیں۔ آپ کی درخواست اس فون پر محفوظ ہے۔ آن لائن ہونے پر ہم آہنگ کریں۔',
    offlineVoiceSaved: 'محفوظ ہو گیا۔ نیٹ ورک واپس آنے پر ہم آہنگ کریں۔',
    micBusy: 'مائیکروفون مصروف ہے۔ دوبارہ کوشش کریں۔',
    micFailed: 'آواز کی پہچان رک گئی۔ دوبارہ کوشش کریں یا لکھ دیں۔',
    micNetwork: () => navigator.onLine
      ? (state.lang === 'ur'
        ? 'اس براؤزر میں اردو آواز پہچاننے کی سہولت اس وقت کام نہیں کر رہی۔ آپ کا انٹرنیٹ چل رہا ہے۔ اپنی بات لکھ دیں یا زبان انگریزی کر کے بولیں۔'
        : 'آواز پہچاننے کی سہولت اس وقت دستیاب نہیں، حالانکہ انٹرنیٹ چل رہا ہے۔ براہِ کرم لکھ دیں اور بعد میں دوبارہ کوشش کریں۔')
      : 'آواز کی پہچان کے لیے انٹرنیٹ ضروری ہے۔ براہِ کرم لکھ دیں۔',
    micTryingLocale: locale => 'اردو بولنے کی دوسری ترتیب آزمائی جا رہی ہے (' + locale + ')…',
    micNoDevice: 'کوئی مائیکروفون نہیں ملا۔ ڈیوائس چیک کریں یا لکھ دیں۔',
    micLangUnsupported: () => state.lang === 'ur'
      ? 'اس براؤزر میں اردو بولنے کی پہچان نہیں۔ اپنی بات لکھ دیں یا زبان انگریزی کر کے بولیں۔'
      : 'اس براؤزر میں یہ زبان بول کر پہچاننے کی سہولت نہیں۔ براہِ کرم لکھ دیں۔',
    micPermission: 'مائیکروفون کی اجازت نہیں ملی۔ براؤزر میں اجازت دیں یا لکھ دیں۔',
    micUnsupported: 'اس براؤزر میں آواز کی سہولت نہیں۔ براہِ کرم لکھ کر بتائیں۔',
    transcriptReady: 'الفاظ نیچے لکھ دیے گئے ہیں۔ انہیں چیک کریں، ضرورت ہو تو تبدیل کریں، پھر بھیجیں دبائیں۔',
    noAudio: 'کوئی آواز پکڑی نہیں گئی۔ مائیکروفون چیک کریں، پھر دوبارہ کوشش کریں یا لکھ دیں۔',
    noTranscript: () => state.lang === 'ur'
      ? 'آپ کی آواز پکڑی گئی، مگر اس براؤزر نے اردو بات نہیں پہچانی۔ اپنی بات لکھ دیں یا زبان انگریزی کر کے بولیں۔'
      : 'آپ کی آواز پکڑی گئی، مگر اس براؤزر نے بات کو الفاظ میں نہیں بدلا۔ دوبارہ کوشش کریں یا لکھ دیں۔',
    micOnQuiet: 'مائیکروفون چالو ہے — اب بولیں۔',
    micHearing: 'آپ کی آواز سنائی دے رہی ہے۔',
    nothingToSync: 'ابھی ہم آہنگ کرنے کے لیے کچھ نہیں۔',
    synced: (processed, duplicates) => processed + ' محفوظ درخواست(یں) ہم آہنگ ہو گئیں۔ چھوڑی گئی: ' + duplicates + '۔',
    syncFailed: detail => 'فون پر محفوظ ہے۔ دوبارہ کوشش کریں: ' + detail,
    askQuestion: 'پہلے اپنا سوال لکھیں۔',
    statusLoadFailed: 'صورت حال لوڈ نہیں ہو سکی۔ تازہ کاری دبائیں۔',
    storageFull: 'اس فون پر جگہ نہیں۔ پہلے محفوظ درخواستیں ہم آہنگ کریں۔',
    welcome: 'خوش آمدید۔ اپنی بات کہیں۔',
    voiceSaved: 'ہم نے آپ کی درخواست محفوظ کر لی ہے۔ ادائیگی سے پہلے ایک انسان اسے چیک کرے گا۔',
    voiceSavedMissing: list => 'ہم نے آپ کی درخواست محفوظ کر لی ہے۔ اب بھی ضروری ہے: ' + list + '۔ براہِ کرم بتائیں۔',
    urduVoiceMissing: 'اس براؤزر میں اردو آواز دستیاب نہیں۔ الفاظ اسکرین پر دکھائے گئے ہیں اور آپ لکھ کر بھی درخواست دے سکتے ہیں۔ ونڈوز پر اس ڈیمو کو مائیکروسافٹ ایج میں کھولیں — ایج آن لائن اردو آوازیں فراہم کرتا ہے، کسی سیٹنگ کی تبدیلی کے بغیر — پھر صفحہ دوبارہ کھولیں۔',
    refreshCases: 'کیسز تازہ کریں', voiceSetup: 'آواز کی ترتیبات',
    voiceHelp: 'ونڈوز پر اردو آواز مائیکروسافٹ ایج میں کام کرتی ہے۔ کروم صرف آپ کے ڈیوائس پر انسٹال آوازیں پڑھتا ہے۔ نیچے چیک کریں، یا لکھ دیں۔',
    checkVoices: 'آوازیں چیک کریں', testUrdu: 'اردو آزمائیں',
    voicesFound: n => 'اس ڈیوائس پر دستیاب آوازیں: ' + n + '۔',
    urduVoiceReady: names => 'اردو آواز تیار: ' + names + '۔ اردو تقریر کام کرے گی۔',
    urduVoiceMissingShort: 'یہاں کوئی اردو آواز دستیاب نہیں۔ ونڈوز پر اس ڈیمو کو مائیکروسافٹ ایج میں کھولیں — ایج کسی ونڈوز سیٹنگ کی تبدیلی کے بغیر آن لائن اردو آوازیں فراہم کرتا ہے — پھر دوبارہ چیک کریں۔ لکھنا ہمیشہ کام کرتا ہے۔',
    testUrduText: 'آپ کی درخواست محفوظ ہو گئی۔ ایک انسان اسے چیک کرے گا۔',
    ttsUnsupported: 'یہ براؤزر متن کو بلند آواز نہیں پڑھ سکتا۔ الفاظ اسکرین پر دکھائے گئے ہیں۔',
    fieldNames: {
      full_name: 'مکمل نام', cnic: 'شناختی نمبر', monthly_income: 'ماہانہ آمدنی',
      claim_amount: 'دعویٰ کی رقم', district: 'ضلع',
      category: 'زمرہ', dependents: 'زیرِ کفالت'
    }
  }
};

const state = {
  lang: localStorage.getItem('lm_lang') || 'ur',
  token: localStorage.getItem('lm_token') || null,
  role: localStorage.getItem('lm_role') || '',
  clientId: localStorage.getItem('lm_client') || ('device-' + Math.random().toString(36).slice(2, 10)),
  cases: [],
  statusCase: null,
  statusError: false,
  statusLoading: true,
  rolePanelData: null,
  rolePanelError: false,
  reviewing: new Set(),
  claimTouched: {},
  claimSource: {},
};

let recognition = null;
let micAvailable = true;
let micBusy = false;
let startingMic = false;
let cancelMicStart = false;
let stopRequested = false;
let heardTranscript = false;
let recognisedText = '';
let finalisedText = '';
let interimText = '';
let transcriptFinished = false;
let noTranscriptTimer = null;
let peakMicLevel = 0;
let soundDetected = false;
let audioStream = null;
let audioContext = null;
let analyser = null;
let meterFrame = null;
let micLevel = 0;
let toastTimer = null;
let claimTextTimer = null;
let voiceSession = false;
let pendingVoiceField = null;
let voicePromptTimer = null;
// Edge reports 'network' for some Urdu locales it cannot recognise. Try the
// standard Urdu tags before giving up; never fall back to English dictation.
const URDU_RECOGNITION_LOCALES = ['ur-PK', 'ur', 'ur-IN'];
let urduLocaleIndex = 0;
let speechVoices = [];
let voicesLoaded = false;
let voiceDiagShown = false;

if (!localStorage.getItem('lm_client')) localStorage.setItem('lm_client', state.clientId);

const $ = id => document.getElementById(id);
const t = (key, ...args) => {
  const value = (I18N[state.lang] && I18N[state.lang][key]) ?? key;
  return typeof value === 'function' ? value(...args) : value;
};

const ROLE_COPY = {
  citizen: { label: 'citizen', title: 'roleCitizenTitle', intro: 'roleCitizenIntro' },
  helper: { label: 'helperRole', title: 'roleHelperTitle', intro: 'roleHelperIntro' },
  officer: { label: 'officer', title: 'roleOfficerTitle', intro: 'roleOfficerIntro' },
  admin: { label: 'admin', title: 'roleAdminTitle', intro: 'roleAdminIntro' },
  auditor: { label: 'auditor', title: 'roleAuditorTitle', intro: 'roleAuditorIntro' },
};

function statusLabel(status) {
  const labels = t('statusLabels');
  return (labels && labels[status]) || String(status || '').replace(/_/g, ' ');
}

/* Citizen copy never shows internal list representations or long traces. */
function statusReason(caseItem) {
  const raw = String((caseItem && caseItem.decision_reason_simple) || '')
    .replace(/\[[^\]]*\]/g, '').trim();
  const sentence = raw.match(/^[^.!?]+[.!?]?/);
  return sentence ? sentence[0].trim() : '';
}

function renderStatus() {
  const el = $('statusText');
  if (!el) return;
  if (state.statusLoading) el.textContent = t('loading');
  else if (state.statusError) el.textContent = t('statusLoadFailed');
  else el.textContent = state.statusCase ? t('statusSome', state.statusCase) : t('statusNone');
}

/* ---------------- Role-aware workspace chrome ---------------- */
function makeRoleRow(title, detail, meta, buttons) {
  const row = document.createElement('div');
  row.className = 'role-row';
  const main = document.createElement('div');
  main.className = 'role-row-main';
  const strong = document.createElement('strong');
  strong.textContent = String(title);
  main.append(strong);
  if (detail) {
    const span = document.createElement('span');
    span.textContent = String(detail);
    main.append(span);
  }
  if (meta) {
    const small = document.createElement('small');
    small.textContent = String(meta);
    main.append(small);
  }
  row.append(main);
  if (buttons && buttons.length) {
    const actions = document.createElement('div');
    actions.className = 'role-actions';
    buttons.forEach(button => actions.append(button));
    row.append(actions);
  }
  return row;
}

function roleButton(label, decision, caseId) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'btn btn-secondary';
  button.textContent = label;
  button.dataset.review = decision;
  button.dataset.caseId = caseId;
  return button;
}

function renderRolePanel() {
  if ($('rolePanel').hidden) return;
  const copy = ROLE_COPY[state.role];
  if (!copy) return;
  $('rolePanelTitle').textContent = t(copy.title);
  $('rolePanelIntro').textContent = t(copy.intro);
  const body = $('rolePanelBody');
  body.replaceChildren();
  const data = state.rolePanelData;
  if (state.rolePanelError) {
    const empty = document.createElement('div');
    empty.className = 'role-empty';
    empty.textContent = t('roleLoadFailed');
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.className = 'btn btn-secondary';
    retry.textContent = t('retry');
    retry.addEventListener('click', loadRolePanel);
    body.append(empty, retry);
    return;
  }
  if (!data) {
    const empty = document.createElement('div');
    empty.className = 'role-empty';
    empty.textContent = t('nothingHere');
    body.append(empty);
    return;
  }
  if (state.role === 'helper') {
    const families = data.families || [];
    if (!families.length) {
      const empty = document.createElement('div');
      empty.className = 'role-empty';
      empty.textContent = t('nothingHere');
      body.append(empty);
    }
    families.slice(0, 8).forEach(family =>
      body.append(makeRoleRow(family.family_id, family.subject_name, t('mockNotice'))));
    if (families.length > 8) {
      body.append(makeRoleRow(`${families.length} ${t('helperFamilies')}`, '', t('mockNotice')));
    }
  } else if (state.role === 'officer') {
    const queue = Array.isArray(data) ? data : [];
    if (!queue.length) {
      const empty = document.createElement('div');
      empty.className = 'role-empty';
      empty.textContent = t('nothingHere');
      body.append(empty);
    }
    queue.slice(0, 8).forEach(item => {
      const meta = `${statusLabel(item.status)} · ${t('confidence')} ${Math.round((item.confidence || 0) * 100)}% · ${t('ruleActive')} ${item.rule_version || '-'}`;
      const buttons = [
        roleButton(t('approve'), 'approved', item.case_id),
        roleButton(t('askInfo'), 'needs_info', item.case_id),
        roleButton(t('reject'), 'rejected', item.case_id),
      ];
      body.append(makeRoleRow(item.case_number, item.reason, meta, buttons));
    });
  } else if (state.role === 'admin') {
    const rule = data.rule || {};
    const definition = rule.definition || {};
    const rules = data.rules || [];
    body.append(makeRoleRow(
      `${t('ruleActive')} v${rule.version || '-'}`,
      rule.name,
      `${definition.max_income} / ${definition.max_claim_amount} · ${t('mockNotice')}`
    ));
    body.append(makeRoleRow(
      `${rules.length} ${t('ruleVersions')}`,
      `${t('approve')} ≥ ${definition.auto_approve_min_confidence} · ${t('askInfo')} ≥ ${definition.ask_info_min_confidence}`,
      t('mockNotice')
    ));
    body.append(makeRoleRow(
      t('ruleRequiresOfficer'),
      definition.require_officer ? t('yes') : t('no'),
      t('roleServerCheck')
    ));
  } else if (state.role === 'auditor') {
    const events = data.events || [];
    if (!events.length) {
      const empty = document.createElement('div');
      empty.className = 'role-empty';
      empty.textContent = t('nothingHere');
      body.append(empty);
    }
    events.slice(0, 8).forEach(event =>
      body.append(makeRoleRow(
        event.action,
        `${event.actor_type}: ${event.actor_id}`,
        new Date(event.created_at).toLocaleString()
      )));
  }
}

function renderRoleChrome() {
  const copy = ROLE_COPY[state.role];
  const banner = $('roleBanner');
  const isCitizen = !state.role || state.role === 'citizen';
  if (!copy) {
    banner.hidden = true;
    banner.replaceChildren();
    $('roleLabel').textContent = '';
    $('rolePanel').hidden = true;
    $('statusCard').classList.remove('hidden');
    const intake = $('viewHome').querySelector('.intake');
    if (intake) intake.classList.remove('hidden');
    return;
  }
  banner.hidden = false;
  banner.replaceChildren();
  const strong = document.createElement('strong');
  strong.textContent = t(copy.title);
  const intro = document.createElement('span');
  intro.textContent = t(copy.intro);
  const note = document.createElement('small');
  note.textContent = t('roleServerCheck');
  banner.append(strong, intro, note);
  $('roleLabel').textContent = t(copy.label);
  $('rolePanel').hidden = isCitizen;
  $('statusCard').classList.toggle('hidden', !isCitizen);
  const intake = $('viewHome').querySelector('.intake');
  if (intake) intake.classList.toggle('hidden', !isCitizen);
  if (!isCitizen) renderRolePanel();
}

async function loadRolePanel() {
  const role = state.role;
  state.rolePanelData = null;
  state.rolePanelError = false;
  renderRoleChrome();
  if (!role || role === 'citizen') return;
  const body = $('rolePanelBody');
  body.replaceChildren();
  const loading = document.createElement('div');
  loading.className = 'role-empty';
  loading.textContent = t('loading');
  body.append(loading);
  try {
    let data;
    if (role === 'helper') {
      data = await api('/api/admin/helper-families');
    } else if (role === 'officer') {
      data = await api('/api/officer/queue');
    } else if (role === 'admin') {
      const [rule, rules] = await Promise.all([api('/api/rules/active'), api('/api/rules')]);
      data = { rule, rules };
    } else if (role === 'auditor') {
      data = { events: await api('/api/audit?limit=8') };
    }
    state.rolePanelData = data;
    state.rolePanelError = false;
    renderRolePanel();
  } catch (e) {
    state.rolePanelData = null;
    state.rolePanelError = true;
    renderRolePanel();
    toast(friendlyError(e), 'error');
  }
}

async function reviewFromPanel(caseId, decision) {
  if (state.reviewing.has(caseId)) return;
  state.reviewing.add(caseId);
  const buttons = Array.from(document.querySelectorAll('button[data-review]'))
    .filter(button => button.dataset.caseId === caseId);
  buttons.forEach(button => setBusy(button, true));
  try {
    await api(`/api/cases/${encodeURIComponent(caseId)}/review`, {
      method: 'POST',
      body: JSON.stringify({ decision, note: t('mockNotice') }),
    });
    toast(t('reviewSaved'));
    await refreshDashboard();
    await loadRolePanel();
  } catch (e) {
    toast(friendlyError(e), 'error');
  } finally {
    state.reviewing.delete(caseId);
    buttons.forEach(button => setBusy(button, false));
  }
}

function activateRoleWorkspace() {
  state.rolePanelData = null;
  renderRoleChrome();
  loadRolePanel();
}

/* Password visibility: a local convenience only; the field value is unchanged. */
function applyPasswordToggle() {
  const button = $('showPasswordBtn');
  const input = $('passwordInput');
  if (!button || !input) return;
  const visible = input.type === 'text';
  const label = t(visible ? 'hidePassword' : 'showPassword');
  button.setAttribute('aria-label', label);
  button.setAttribute('title', label);
  button.setAttribute('aria-pressed', String(visible));
}

function setPasswordVisible(visible) {
  const input = $('passwordInput');
  if (!input) return;
  input.type = visible ? 'text' : 'password';
  applyPasswordToggle();
}

function togglePasswordVisibility() {
  const input = $('passwordInput');
  if (input) setPasswordVisible(input.type === 'password');
}

function applyLang() {
  const root = document.documentElement;
  root.lang = state.lang;
  root.dir = state.lang === 'ur' ? 'rtl' : 'ltr';
  document.body.lang = state.lang;
  document.body.dir = root.dir;
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => { el.placeholder = t(el.dataset.i18nPh); });
  document.querySelectorAll('[data-i18n-aria]').forEach(el => { el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
  document.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.dataset.i18nTitle); });
  applyPasswordToggle();
  resetRecognitionLocale();
  if (pendingVoiceField && $('micHint')) $('micHint').textContent = t('voiceAwaiting', t(CLAIM_LABEL_KEYS[pendingVoiceField]));
  else if (!micAvailable) $('micHint').textContent = t('micUnsupported');
  renderStatus();
  renderRoleChrome();
  updateNetwork();
  updateVoiceNote();
  if (voiceDiagShown) renderVoiceDiag();
  if ($('voiceMeter') && !$('voiceMeter').classList.contains('hidden')) {
    $('voiceLevelText').textContent = micLevel > 0.05 ? t('micHearing') : t('micOnQuiet');
  }
  updateQueueBadge();
  updateHeaderOffset();
}

function toggleLang() {
  state.lang = state.lang === 'ur' ? 'en' : 'ur';
  localStorage.setItem('lm_lang', state.lang);
  applyLang();
}

function toast(message, kind) {
  const el = $('toast');
  el.textContent = message;
  el.classList.toggle('error', kind === 'error');
  el.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add('hidden'), 4500);
}

function showFieldError(id, message) {
  const el = $(id);
  el.textContent = message;
  el.hidden = !message;
}

/* Structured claim fields. Words from the microphone or request box only fill
   fields the citizen has not edited; the server still validates every value. */
const CLAIM_FIELDS = {
  full_name: 'claimFullName', cnic: 'claimCnic', district: 'claimDistrict',
  category: 'claimCategory', monthly_income: 'claimIncome',
  claim_amount: 'claimAmount', dependents: 'claimDependents'
};
const CLAIM_ERROR_IDS = {
  full_name: 'claimFullNameError', cnic: 'claimCnicError', district: 'claimDistrictError',
  category: 'claimCategoryError', monthly_income: 'claimIncomeError',
  claim_amount: 'claimAmountError', dependents: 'claimDependentsError'
};
const CLAIM_LABEL_KEYS = {
  full_name: 'fullNameLabel', cnic: 'cnicLabel', district: 'districtLabel',
  category: 'categoryLabel', monthly_income: 'incomeLabel',
  claim_amount: 'amountLabel', dependents: 'dependentsLabel'
};

function setClaimError(field, message) {
  const input = $(CLAIM_FIELDS[field]);
  if (input) input.setAttribute('aria-invalid', message ? 'true' : 'false');
  showFieldError(CLAIM_ERROR_IDS[field], message || '');
}

function clearClaimErrors() {
  Object.keys(CLAIM_FIELDS).forEach(field => setClaimError(field, ''));
}

/* Urdu speech commonly returns Arabic-Indic (٠-٩) or Persian (۰-۹) digits.
   Normalise both sets before extraction so CNIC and amounts are bilingual. */
function normaliseDigits(text) {
  return String(text || '')
    .replace(/[\u0660-\u0669]/g, d => String(d.charCodeAt(0) - 0x0660))
    .replace(/[\u06F0-\u06F9]/g, d => String(d.charCodeAt(0) - 0x06F0));
}

function cleanExtractedName(value) {
  return String(value || '')
    .split(/[.۔!?؟،؛]/)[0]
    .replace(/\s+(?:ہے|ہوں|ہیں|is|شخص|صاحب|صاحبہ)(?:\s|$).*$/i, '')
    .replace(/\s+(?:شناختی\s*نمبر|سی\s*این\s*آئی\s*سی|cnic)(?:\s|$).*$/i, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function cleanExtractedDistrict(value) {
  return String(value || '')
    .split(/[.۔!?؟،؛]/)[0]
    .replace(/\s+(?:میں|ہے|ہوں|ہیں|رہتا|رہتی|رہتے|شہر|district)(?:\s|$).*$/i, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function extractClaimFields(text) {
  const clean = normaliseDigits(text).trim();
  const out = {};

  // 5-7-1 digits, with dashes or spaces, in either script after normalisation.
  const cnic = clean.match(/\b\d{5}[-\s]?\d{7}[-\s]?\d\b/);
  if (cnic) out.cnic = cnic[0];

  // Only a stated name fills this field: "I am unemployed in Lahore" is a
  // category and a district, not a person's name.
  const name = clean.match(/(?:my name is|میرا نام)\s+([A-Za-z\u0600-\u06FF]+(?:\s+[A-Za-z\u0600-\u06FF]+){0,3})/i)
    || clean.match(/\bi am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b/);
  if (name) {
    const trimmed = cleanExtractedName(name[1]);
    if (trimmed.length >= 2) out.full_name = trimmed;
  }

  const income = clean.match(/(?:monthly income|income|آمدنی)\s*(?:is|of|≈|=)?\s*(?:rs\.?\s*)?([\d,]{3,})/i)
    || clean.match(/([\d,]{3,})\s*(?:روپے)?\s*(?:ماہانہ\s*)?آمدنی/i);
  if (income) out.monthly_income = income[1].replace(/,/g, '');
  const dependents = clean.match(/(\d{1,2})\s*(?:dependents|children|بچے)/i);
  if (dependents) out.dependents = dependents[1];

  // English states the amount before the cue; Urdu often says it after it.
  const amount = clean.match(/(?:claim(?:ing)?|need|request(?:ing)?|amount|چاہیے|ضرورت|رقم|ادائیگی)\s*(?:of|for|rs\.?\s*)?([\d,]{3,})/i)
    || clean.match(/([\d,]{3,})\s*(?:روپے|rs\.?)?\s*(?:چاہیے|ضرورت|رقم|ادائیگی)/i);
  if (amount) out.claim_amount = amount[1].replace(/,/g, '');

  const lowered = clean.toLowerCase();
  if (/widow|بیوہ/.test(lowered)) out.category = 'widow';
  else if (/disabled|معذور/.test(lowered)) out.category = 'disabled';
  else if (/unemployed|بے روزگار/.test(lowered)) out.category = 'unemployed';
  else if (/low[-\s]?income|کم\s*آمدنی|غربت/.test(lowered)) out.category = 'low_income';

  // "رہائش" is the everyday Urdu word a citizen uses for district.
  const district = clean.match(/(?:in|from|district|رہائش|ضلع|شہر)\s+([A-Za-z\u0600-\u06FF]{2,40})/i);
  if (district) {
    const trimmed = cleanExtractedDistrict(district[1]);
    if (trimmed.length >= 2) out.district = trimmed;
  }
  return out;
}

function updateClaimFillNote() {
  const note = $('claimFillNote');
  if (!note) return;
  const fromVoice = Object.keys(state.claimSource).some(field => state.claimSource[field] === 'voice');
  note.classList.toggle('hidden', !fromVoice);
}

function fillClaimFields(text) {
  const extracted = extractClaimFields(text);
  let filled = 0;
  Object.keys(CLAIM_FIELDS).forEach(field => {
    const value = extracted[field];
    if (value === undefined || state.claimTouched[field]) return;
    const input = $(CLAIM_FIELDS[field]);
    if (!input) return;
    if (input.value !== String(value)) {
      input.value = String(value);
      filled++;
    }
    state.claimSource[field] = 'voice';
    setClaimError(field, '');
  });
  updateClaimFillNote();
  return filled;
}

/* A follow-up answer is often just a value ("Fatima Bibi", "12000"), not a full
   sentence. Pull that one field without disturbing the request text or the
   other fields the citizen already checked. */
function extractSingleClaimField(field, text) {
  // Normalise once so a bare Urdu/Persian-digit answer follows the same path
  // as an English one, including the 13-digit CNIC fallback below.
  const clean = normaliseDigits(String(text || '').trim());
  if (!clean) return undefined;
  const found = extractClaimFields(clean)[field];
  if (found !== undefined) return found;
  const lower = clean.toLowerCase();
  const digits = clean.replace(/\D/g, '');
  if (field === 'full_name') {
    const name = clean
      .replace(/^(?:my name is|i am|میرا نام)\s+/i, '')
      .replace(/\d/g, ' ')
      .replace(/[.,!?؛،۔:|_]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .split(/\s+/).slice(0, 6).join(' ');
    const trimmed = cleanExtractedName(name);
    return trimmed.length >= 2 ? trimmed : undefined;
  }
  if (field === 'cnic') return digits.length >= 13 ? digits.slice(0, 13) : undefined;
  if (field === 'district') {
    const district = clean
      .replace(/^(?:i am from|i am in|i am|from|in|district|میں|ضلع|رہائش|شہر)\s+/i, '')
      .replace(/\d/g, ' ')
      .replace(/[.,!?؛،۔:|_]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .split(/\s+/).slice(0, 3).join(' ');
    const trimmed = cleanExtractedDistrict(district);
    return trimmed.length >= 2 ? trimmed : undefined;
  }
  if (field === 'category') {
    if (/widow|بیوہ/.test(lower)) return 'widow';
    if (/disabled|معذور/.test(lower)) return 'disabled';
    if (/unemployed|بے روزگار/.test(lower)) return 'unemployed';
    if (/low[-\s]?income|کم\s*آمدنی|غربت/.test(lower)) return 'low_income';
    return undefined;
  }
  if (field === 'monthly_income' || field === 'claim_amount') {
    const number = clean.replace(/,/g, '').match(/\d+/);
    return number && Number(number[0]) > 0 ? number[0] : undefined;
  }
  return undefined;
}

function fillSingleClaimField(field, text) {
  const value = extractSingleClaimField(field, text);
  if (value === undefined) return false;
  const input = $(CLAIM_FIELDS[field]);
  if (!input) return false;
  if (state.claimTouched[field]) return true; // never overwrite a user edit
  if (input.value !== String(value)) {
    input.value = String(value);
    state.claimSource[field] = 'voice';
    setClaimError(field, '');
    updateClaimFillNote();
  }
  return true;
}

function markClaimEdited(field) {
  state.claimTouched[field] = true;
  state.claimSource[field] = 'user';
  setClaimError(field, '');
}

function resetClaimFields() {
  Object.keys(CLAIM_FIELDS).forEach(field => {
    const input = $(CLAIM_FIELDS[field]);
    if (!input) return;
    input.value = '';
    delete state.claimTouched[field];
    delete state.claimSource[field];
  });
  clearClaimErrors();
  const note = $('claimFillNote');
  if (note) note.classList.add('hidden');
  clearTimeout(claimTextTimer);
  endVoiceSession();
}

function readClaimForm() {
  const raw = field => {
    const input = $(CLAIM_FIELDS[field]);
    return input ? String(input.value).trim() : '';
  };
  const number = field => {
    const value = raw(field);
    return value === '' ? null : Number(value);
  };
  const dependents = number('dependents');
  return {
    full_name: raw('full_name'),
    cnic: raw('cnic'),
    district: raw('district'),
    category: raw('category') || null,
    monthly_income: number('monthly_income'),
    claim_amount: number('claim_amount'),
    dependents: dependents === null ? 0 : dependents
  };
}

function validateClaimFields(claim) {
  const errors = {};
  const present = value => value !== null && value !== undefined && String(value).trim() !== '';
  ['full_name', 'cnic', 'district', 'category', 'monthly_income', 'claim_amount'].forEach(field => {
    if (!present(claim[field])) errors[field] = t('fieldRequired', t(CLAIM_LABEL_KEYS[field]));
  });
  if (present(claim.cnic) && String(claim.cnic).replace(/\D/g, '').length !== 13) {
    errors.cnic = t('invalidCnic');
  }
  ['monthly_income', 'claim_amount', 'dependents'].forEach(field => {
    const value = claim[field];
    if (value !== null && (!Number.isInteger(value) || value < 0)) errors[field] = t('invalidNumber');
  });
  if (claim.claim_amount !== null && claim.claim_amount === 0 && !errors.claim_amount) {
    errors.claim_amount = t('invalidNumber');
  }
  if (present(claim.monthly_income) && present(claim.claim_amount) && !errors.monthly_income && !errors.claim_amount) {
    if (claim.claim_amount > Math.max(claim.monthly_income * 3, 5000)) errors.claim_amount = t('amountTooHigh');
  }
  if (claim.dependents !== null && claim.dependents > 30 && !errors.dependents) {
    errors.dependents = t('invalidNumber');
  }
  return errors;
}

/* ---------------- Voice-led completion of required claim details ---------------- */
const VOICE_REQUIRED_FIELDS = ['full_name', 'cnic', 'district', 'category', 'monthly_income', 'claim_amount'];

function endVoiceSession() {
  voiceSession = false;
  pendingVoiceField = null;
  if (voicePromptTimer) clearTimeout(voicePromptTimer);
  voicePromptTimer = null;
  if ($('micHint')) $('micHint').textContent = t('micHint');
}

function nextMissingVoiceField() {
  const errors = validateClaimFields(readClaimForm());
  return VOICE_REQUIRED_FIELDS.find(field => errors[field]) || null;
}

function restoreMicHint() {
  if ($('micHint')) $('micHint').textContent = t('micHint');
}

function askForVoiceField(field) {
  pendingVoiceField = field;
  const question = (t('voiceAsk') || {})[field] || t('voiceAskGeneric', t(CLAIM_LABEL_KEYS[field]));
  if ($('micHint')) $('micHint').textContent = t('voiceAwaiting', t(CLAIM_LABEL_KEYS[field]));
  toast(question);
  speakThen(question, () => {
    voicePromptTimer = setTimeout(() => {
      if (voiceSession && pendingVoiceField === field) startMic();
    }, 250);
  });
}

function continueVoiceCompletion() {
  if (!voiceSession) return;
  const field = nextMissingVoiceField();
  if (field) { askForVoiceField(field); return; }
  pendingVoiceField = null;
  restoreMicHint();
  toast(t('voiceAllDone'));
  speak(t('voiceAllDone'));
  if ($('sendBtn')) $('sendBtn').focus();
}

function setBusy(button, busy) {
  if (!button) return;
  button.classList.toggle('busy', busy);
  button.disabled = busy;
  button.setAttribute('aria-busy', busy ? 'true' : 'false');
}

function friendlyError(error) {
  const detail = String((error && error.message) || '');
  if (detail === 'badCredentials') return t('badCredentials');
  if (detail === 'sessionExpired') return t('sessionExpired');
  if (/fetch|network|timeout|offline/i.test(detail)) return t('networkFailed');
  if (/HTTP 5\d\d/.test(detail)) return t('serverFailed');
  return detail || t('requestFailed');
}

/* ---------------- Speech: pick a real installed voice, not just a lang code ---------------- */
function refreshVoices() {
  if (!('speechSynthesis' in window)) return;
  speechVoices = Array.from(window.speechSynthesis.getVoices() || []);
  voicesLoaded = true;
  updateVoiceNote();
}

function findVoice(prefixes) {
  if (!voicesLoaded) {
    // Mark loaded before reading so updateVoiceNote() cannot re-enter here.
    voicesLoaded = true;
    if ('speechSynthesis' in window) {
      speechVoices = Array.from(window.speechSynthesis.getVoices() || []);
    }
  }
  for (const prefix of prefixes) {
    const found = speechVoices.find(v => (v.lang || '').toLowerCase().indexOf(prefix) === 0);
    if (found) return found;
  }
  return null;
}

function urduVoice() { return findVoice(['ur', 'ur-pk', 'ur-in']); }
function englishVoice() { return findVoice(['en-us', 'en-gb', 'en']); }

function updateVoiceNote() {
  const note = $('voiceNote');
  if (!note) return;
  if (state.lang !== 'ur') { note.hidden = true; return; }
  if (!('speechSynthesis' in window)) {
    note.textContent = t('ttsUnsupported');
    note.hidden = false;
    return;
  }
  if (urduVoice()) { note.hidden = true; return; }
  note.textContent = t('urduVoiceMissing');
  note.hidden = false;
}

function speak(text) {
  if (!('speechSynthesis' in window) || !text) return;
  const urdu = state.lang === 'ur';
  const voice = urdu ? urduVoice() : englishVoice();
  // Never read Urdu words with an English voice: that is how the old build "spoke Urdu".
  if (urdu && !voice) { updateVoiceNote(); return; }
  const utter = new SpeechSynthesisUtterance(text.slice(0, 500));
  utter.lang = urdu ? 'ur-PK' : 'en-US';
  if (voice) utter.voice = voice;
  utter.rate = urdu ? 0.85 : 0.95;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
  updateVoiceNote();
}

/* Spoken follow-up question. The callback also runs when no honest voice is
   available, so the citizen still gets the visible prompt and the mic opens. */
function speakThen(text, action) {
  let done = false;
  let fallback = null;
  const finish = () => {
    if (done) return;
    done = true;
    if (fallback) clearTimeout(fallback);
    action();
  };
  if (!('speechSynthesis' in window) || !text) { finish(); return; }
  const urdu = state.lang === 'ur';
  const voice = urdu ? urduVoice() : englishVoice();
  if (urdu && !voice) { updateVoiceNote(); finish(); return; }
  const utter = new SpeechSynthesisUtterance(text.slice(0, 500));
  utter.lang = urdu ? 'ur-PK' : 'en-US';
  if (voice) utter.voice = voice;
  utter.rate = urdu ? 0.85 : 0.95;
  utter.onend = finish;
  utter.onerror = finish;
  fallback = setTimeout(finish, 5000);
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
  updateVoiceNote();
}

/* ---------------- Help page: voice capability diagnostics ---------------- */
function readVoices() {
  if (!('speechSynthesis' in window)) return [];
  speechVoices = Array.from(window.speechSynthesis.getVoices() || []);
  voicesLoaded = true;
  updateVoiceNote();
  return speechVoices;
}

function renderVoiceDiag(message) {
  voiceDiagShown = true;
  const box = $('voiceDiag');
  if (!box) return;
  if (message) { box.textContent = message; return; }
  if (!('speechSynthesis' in window)) { box.textContent = t('ttsUnsupported'); return; }
  const voices = readVoices();
  const urdu = voices.filter(v => /^ur/i.test(v.lang || ''));
  box.textContent = t('voicesFound', voices.length) + ' ' +
    (urdu.length ? t('urduVoiceReady', urdu.map(v => v.name).join(', ')) : t('urduVoiceMissingShort'));
}

function testUrduVoice() {
  voiceDiagShown = true;
  const box = $('voiceDiag');
  if (!('speechSynthesis' in window)) {
    if (box) box.textContent = t('ttsUnsupported');
    return;
  }
  const voices = readVoices();
  const voice = urduVoice();
  if (!voice) {
    if (box) box.textContent = t('voicesFound', voices.length) + ' ' + t('urduVoiceMissingShort');
    return;
  }
  const sample = t('testUrduText');
  const utter = new SpeechSynthesisUtterance(sample);
  utter.lang = 'ur-PK';
  utter.voice = voice;
  utter.rate = 0.85;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utter);
  if (box) box.textContent = t('urduVoiceReady', voice.name);
}

if ('speechSynthesis' in window) {
  refreshVoices();
  window.speechSynthesis.addEventListener('voiceschanged', refreshVoices);
}

async function api(path, options = {}) {
  const headers = Object.assign({}, options.headers || {});
  if (state.token) headers.Authorization = 'Bearer ' + state.token;
  if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const response = await fetch(path, Object.assign({}, options, { headers }));
  if (response.status === 401) {
    if (options.keepSession) throw new Error('badCredentials');
    logout(); throw new Error('sessionExpired');
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.message || data.error || ('HTTP ' + response.status));
  return data;
}

async function login(email, password) {
  showFieldError('loginError', '');
  if (!/^\S+@\S+\.\S+$/.test(email)) {
    showFieldError('loginError', t('checkEmail'));
    $('emailInput').focus();
    return;
  }
  if (!password) {
    showFieldError('loginError', t('checkPassword'));
    $('passwordInput').focus();
    return;
  }
  setBusy($('loginBtn'), true);
  try {
    const data = await api('/api/auth/login', {
      method: 'POST', body: JSON.stringify({ email, password }), keepSession: true
    });
    state.token = data.access_token;
    state.role = data.role || '';
    localStorage.setItem('lm_token', state.token);
    localStorage.setItem('lm_role', state.role);
    setPasswordVisible(false);
    resetClaimFields();
    $('textInput').value = '';
    $('loginScreen').classList.remove('active');
    $('appScreen').classList.add('active');
    goTo('home');
    activateRoleWorkspace();
    await refreshDashboard();
    if (state.role === 'citizen') speak(t('welcome'));
  } catch (e) {
    const message = friendlyError(e);
    if (String((e && e.message) || '') === 'badCredentials') {
      showFieldError('loginError', message);
      $('passwordInput').focus();
    } else {
      toast(message, 'error');
    }
  } finally {
    setBusy($('loginBtn'), false);
  }
}

function logout() {
  state.token = null; state.role = ''; state.cases = []; state.rolePanelData = null;
  state.statusCase = null; state.statusError = false; state.statusLoading = false;
  stopMeter();
  resetClaimFields();
  $('textInput').value = '';
  localStorage.removeItem('lm_token');
  localStorage.removeItem('lm_role');
  $('appScreen').classList.remove('active');
  $('loginScreen').classList.add('active');
  location.hash = '';
  applyView();
  renderRoleChrome();
  $('caseList').replaceChildren();
  renderStatus();
  setProgress(10);
  $('statusIcon').innerHTML = svgIcon('clipboard');
  showFieldError('loginError', '');
  setPasswordVisible(false);
}

function statusMarkup(status) {
  if (status === 'approved') return { icon: 'check', cls: '' };
  if (status === 'blocked' || status === 'auto_block' || status === 'rejected') return { icon: 'cross', cls: 'stop' };
  if (status === 'needs_info' || status === 'human_review') return { icon: 'info', cls: 'warn' };
  if (status === 'pending_officer' || status === 'escalated') return { icon: 'clock', cls: 'warn' };
  return { icon: 'clipboard', cls: '' };
}

function setStatusIcon(status) {
  const mark = statusMarkup(status);
  $('statusIcon').innerHTML = svgIcon(mark.icon);
}

function setProgress(value) {
  const safe = Math.max(0, Math.min(100, Math.round(Number(value) || 0)));
  $('progressBar').style.width = safe + '%';
  $('progressTrack').setAttribute('aria-valuenow', String(safe));
}

function renderCases(cases) {
  const list = $('caseList');
  list.replaceChildren();
  cases.slice(0, 8).forEach(c => {
    const row = document.createElement('div');
    row.className = 'case-item';
    row.setAttribute('role', 'listitem');

    const mark = document.createElement('span');
    const style = statusMarkup(c.status);
    mark.className = 'case-mark' + (style.cls ? ' ' + style.cls : '');
    mark.setAttribute('aria-hidden', 'true');
    mark.innerHTML = svgIcon(style.icon);

    const body = document.createElement('span');
    body.className = 'case-body';
    const strong = document.createElement('strong');
    strong.textContent = c.case_number || '-';
    const meta = document.createElement('span');
    meta.className = 'case-meta';

    const pill = document.createElement('span');
    pill.className = 'pill' + (style.cls ? ' ' + style.cls : '');
    pill.textContent = statusLabel(c.status);

    const confidence = Number.isFinite(Number(c.confidence)) ? Math.round(Number(c.confidence) * 100) : 0;
    const conf = document.createElement('span');
    conf.className = 'confidence';
    conf.textContent = t('confidence') + ' ' + confidence + '%';
    const meter = document.createElement('span');
    meter.className = 'meter';
    meter.setAttribute('aria-hidden', 'true');
    const fill = document.createElement('span');
    fill.style.width = confidence + '%';
    meter.appendChild(fill);
    conf.appendChild(meter);

    meta.append(pill, conf);
    body.append(strong, meta);
    row.append(mark, body);
    list.appendChild(row);
  });
  if (!cases.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-note';
    empty.setAttribute('role', 'listitem');
    empty.textContent = t('statusNone');
    list.appendChild(empty);
  }
}

async function refreshDashboard() {
  if (!state.token) return;
  state.statusLoading = true;
  renderStatus();
  setBusy($('statusRefresh'), true);
  setBusy($('casesRefresh'), true);
  try {
    const dash = await api('/api/dashboard');
    state.cases = dash.recent_cases || [];
    renderCases(state.cases);
    const first = state.cases[0];
    state.statusCase = first;
    state.statusError = false;
    state.statusLoading = false;
    renderStatus();
    setProgress(first ? 20 + Math.round((Number(first.confidence) || 0) * 70) : 10);
    setStatusIcon(first ? first.status : null);
  } catch (e) {
    state.statusError = true;
    state.statusLoading = false;
    renderStatus();
    toast(friendlyError(e), 'error');
  } finally {
    setBusy($('statusRefresh'), false);
    setBusy($('casesRefresh'), false);
  }
}

function queued() {
  try {
    const items = JSON.parse(localStorage.getItem('lm_queue') || '[]');
    return Array.isArray(items) ? items : [];
  } catch (e) {
    try { localStorage.setItem('lm_queue', '[]'); } catch (ignored) { /* storage unavailable */ }
    return [];
  }
}

function queueOp(op) {
  try {
    const items = queued();
    items.push(Object.assign({ op_id: 'op-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7) }, op));
    localStorage.setItem('lm_queue', JSON.stringify(items));
    updateQueueBadge();
    return true;
  } catch (e) {
    toast(t('storageFull'), 'error');
    return false;
  }
}

function updateQueueBadge() {
  const count = queued().length;
  $('queueCount').textContent = String(count);
  $('syncBtn').setAttribute('aria-label', t('syncSaved') + (count ? ' (' + count + ')' : ''));
  $('syncBtn').classList.toggle('hidden', count === 0);
}

async function syncQueue(manual = true) {
  const items = queued();
  if (!items.length) { if (manual) toast(t('nothingToSync')); return; }
  const button = $('syncBtn');
  setBusy(button, true);
  try {
    const result = await api('/api/sync', {
      method: 'POST',
      body: JSON.stringify({ client_id: state.clientId, operations: items })
    });
    localStorage.setItem('lm_queue', '[]');
    updateQueueBadge();
    toast(t('synced', result.processed, result.duplicates_skipped));
    await refreshDashboard();
  } catch (e) {
    toast(t('syncFailed', friendlyError(e)), 'error');
  } finally {
    setBusy(button, false);
  }
}

function speakSavedPrompt(result) {
  const missing = (result && result.missing_fields) || [];
  if (!missing.length) { speak(t('voiceSaved')); return; }
  const names = missing.map(field => I18N[state.lang].fieldNames[field] || field.replace(/_/g, ' '));
  speak(t('voiceSavedMissing', names.join(', ')));
}

async function submitText(text) {
  const value = (text || '').trim();
  if (!value) { toast(t('enterRequest'), 'error'); return; }
  stopActiveRecognition(true);
  const claim = readClaimForm();
  const errors = validateClaimFields(claim);
  if (Object.keys(errors).length) {
    clearClaimErrors();
    Object.keys(errors).forEach(field => setClaimError(field, errors[field]));
    toast(t('fixFields'), 'error');
    if (voiceSession) continueVoiceCompletion();
    else {
      const first = $(CLAIM_FIELDS[Object.keys(errors)[0]]);
      if (first) first.focus();
    }
    return;
  }
  clearClaimErrors();
  const intakePayload = { transcript: value, language: state.lang, claim_data: claim };
  if (!navigator.onLine) {
    if (!queueOp({ op_type: 'voice_intake', payload: intakePayload })) return;
    $('textInput').value = '';
    resetClaimFields();
    toast(t('noSignalSaved'));
    speak(t('offlineVoiceSaved'));
    return;
  }
  setBusy($('sendBtn'), true);
  micBusy = true;
  updateMicControls();
  try {
    const result = await api('/api/ai/voice/intake', {
      method: 'POST', body: JSON.stringify(intakePayload)
    });
    const caseNumber = result && result.case && result.case.case_number;
    toast(caseNumber ? t('savedCase', caseNumber) : t('requestFailed'));
    speakSavedPrompt(result);
    $('textInput').value = '';
    resetClaimFields();
    await refreshDashboard();
  } catch (e) {
    toast(friendlyError(e), 'error');
  } finally {
    setBusy($('sendBtn'), false);
    micBusy = false;
    updateMicControls();
  }
}

async function askHelp() {
  const question = $('helpQuestion').value.trim();
  showFieldError('helpError', '');
  if (!question) { showFieldError('helpError', t('askQuestion')); $('helpQuestion').focus(); return; }
  setBusy($('helpBtn'), true);
  try {
    const result = await api('/api/ai/rag', {
      method: 'POST', body: JSON.stringify({ question, top_k: 2 })
    });
    $('helpAnswer').textContent = result.answer || '';
    speak(result.answer || '');
  } catch (e) {
    toast(friendlyError(e), 'error');
  } finally {
    setBusy($('helpBtn'), false);
  }
}

/* ---------------- Live microphone level meter (Web Audio) ---------------- */
function drawMeter() {
  if (!analyser) return;
  const data = new Uint8Array(analyser.fftSize);
  analyser.getByteTimeDomainData(data);
  let sum = 0;
  for (let i = 0; i < data.length; i++) {
    const value = (data[i] - 128) / 128;
    sum += value * value;
  }
  micLevel = Math.min(1, Math.sqrt(sum / data.length) * 4);
  if (micLevel > peakMicLevel) peakMicLevel = micLevel;
  const bars = $('voiceMeter').querySelectorAll('.bar');
  const middle = (bars.length - 1) / 2;
  bars.forEach((bar, i) => {
    const centreWeight = 1 - Math.abs(i - middle) / middle;
    bar.style.height = Math.round(4 + micLevel * centreWeight * 24) + 'px';
    bar.classList.toggle('loud', micLevel > 0.12);
  });
  const label = micLevel > 0.05 ? t('micHearing') : t('micOnQuiet');
  const text = $('voiceLevelText');
  if (text.textContent !== label) text.textContent = label;
  meterFrame = requestAnimationFrame(drawMeter);
}

async function startMeter() {
  stopMeter();
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !AudioCtx) return false;
  try {
    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioContext = new AudioCtx();
    const source = audioContext.createMediaStreamSource(audioStream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 512;
    analyser.smoothingTimeConstant = 0.7;
    source.connect(analyser);
    $('voiceMeter').classList.remove('hidden');
    $('voiceLevelText').classList.remove('hidden');
    $('voiceLevelText').textContent = t('micOnQuiet');
    drawMeter();
    return true;
  } catch (e) {
    return false;
  }
}

function stopMeter() {
  if (meterFrame) cancelAnimationFrame(meterFrame);
  meterFrame = null;
  if (audioStream) audioStream.getTracks().forEach(track => track.stop());
  audioStream = null;
  if (audioContext) audioContext.close().catch(() => {});
  audioContext = null;
  analyser = null;
  micLevel = 0;
  if ($('voiceMeter')) $('voiceMeter').classList.add('hidden');
  if ($('voiceLevelText')) $('voiceLevelText').classList.add('hidden');
}

/* ---------------- Microphone: live words, stop, then review ---------------- */
function clearNoTranscriptTimer() {
  if (noTranscriptTimer) clearTimeout(noTranscriptTimer);
  noTranscriptTimer = null;
}

function finishWithTranscript() {
  if (transcriptFinished || !recognisedText.trim()) return;
  transcriptFinished = true;
  clearNoTranscriptTimer();
  stopRequested = false;
  setListening(false);
  if (pendingVoiceField) {
    const field = pendingVoiceField;
    const saved = fillSingleClaimField(field, recognisedText);
    pendingVoiceField = null;
    restoreMicHint();
    toast(saved ? t('voiceFieldSaved', t(CLAIM_LABEL_KEYS[field])) : t('voiceFieldMissed', t(CLAIM_LABEL_KEYS[field])));
    continueVoiceCompletion();
    return;
  }
  const box = $('textInput');
  box.value = recognisedText.trim();
  box.focus();
  box.setSelectionRange(box.value.length, box.value.length);
  toast(t('transcriptReady'));
  continueVoiceCompletion();
}

/* Sending always releases the microphone. Once a request is submitted, late
   recognition results must not overwrite the text the citizen already sent. */
function stopActiveRecognition(preserveText = false) {
  if (startingMic) {
    cancelMicStart = true;
    stopMeter();
  }
  if (!recognition || !$('micBtn') || !$('micBtn').classList.contains('listening')) return false;
  if (preserveText) transcriptFinished = true;
  stopRequested = true;
  try { recognition.stop(); } catch (e) { /* already stopped */ }
  setListening(false);
  return true;
}

function scheduleNoTranscript() {
  clearNoTranscriptTimer();
  // A final result can arrive just after onend in some browsers. Wait briefly
  // before claiming nothing was recognised.
  noTranscriptTimer = setTimeout(() => {
    noTranscriptTimer = null;
    if (!stopRequested || transcriptFinished || recognisedText.trim()) return;
    const voicePickedUp = peakMicLevel > 0.05 || soundDetected;
    toast(voicePickedUp ? t('noTranscript') : t('noAudio'), 'error');
    stopRequested = false;
  }, 700);
}

function updateMicControls() {
  const listening = $('micBtn').classList.contains('listening');
  $('micBtn').disabled = listening || startingMic || micBusy || !micAvailable;
  $('stopBtn').classList.toggle('hidden', !listening);
}

function setListening(on) {
  $('micBtn').classList.toggle('listening', on);
  updateMicControls();
  if (!on) stopMeter();
}

function resetRecognitionState() {
  clearNoTranscriptTimer();
  cancelMicStart = false;
  stopRequested = false;
  heardTranscript = false;
  recognisedText = '';
  finalisedText = '';
  interimText = '';
  transcriptFinished = false;
  peakMicLevel = 0;
  soundDetected = false;
}

async function startMic() {
  if (!recognition || $('micBtn').disabled) return;
  if (voicePromptTimer) { clearTimeout(voicePromptTimer); voicePromptTimer = null; }
  voiceSession = true;
  startingMic = true;
  updateMicControls();
  resetRecognitionState();
  // Get microphone access and show live levels before starting recognition,
  // so a silent failure is visible instead of a mysterious "no words" message.
  const meterReady = await startMeter();
  startingMic = false;
  if (cancelMicStart) {
    cancelMicStart = false;
    updateMicControls();
    return;
  }
  if (!meterReady) {
    updateMicControls();
    toast(t('micPermission'), 'error');
    return;
  }
  try { recognition.start(); setListening(true); }
  catch (e) { stopMeter(); updateMicControls(); toast(t('micBusy')); }
}

function recognitionLang() {
  return state.lang === 'ur' ? URDU_RECOGNITION_LOCALES[urduLocaleIndex] : 'en-US';
}

function resetRecognitionLocale() {
  urduLocaleIndex = 0;
  if (recognition) recognition.lang = recognitionLang();
}

/* Some browsers (notably Edge) answer a valid but unsupported Urdu locale with
   a 'network' error even when the device is online. Walk through the other
   standard Urdu tags once; English dictation is never used for Urdu speech. */
function tryNextUrduRecognitionLocale() {
  if (state.lang !== 'ur' || urduLocaleIndex >= URDU_RECOGNITION_LOCALES.length - 1) return false;
  urduLocaleIndex++;
  if (recognition) recognition.lang = recognitionLang();
  if ($('micHint')) $('micHint').textContent = t('micTryingLocale', recognition.lang);
  voicePromptTimer = setTimeout(() => {
    voicePromptTimer = null;
    if (voiceSession) startMic();
  }, 350);
  return true;
}

function initRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    micAvailable = false;
    setListening(false);
    $('micHint').textContent = t('micUnsupported');
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = recognitionLang();
  // Continuous listening keeps recording until the red stop button is pressed.
  // Interim results give us usable words even when a final result arrives late.
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.maxAlternatives = 3;

  $('micBtn').addEventListener('click', () => startMic());
  $('stopBtn').addEventListener('click', () => {
    if (!recognition) return;
    // stop() keeps the audio captured so far and asks for a final result.
    stopActiveRecognition();
    if (recognisedText.trim()) finishWithTranscript();
    else if (pendingVoiceField) {
      const field = pendingVoiceField;
      pendingVoiceField = null;
      stopRequested = false;
      restoreMicHint();
      toast(t('voiceFieldMissed', t(CLAIM_LABEL_KEYS[field])));
      askForVoiceField(field);
    } else scheduleNoTranscript();
  });

  recognition.onresult = event => {
    let finalChunk = '';
    let interimChunk = '';
    const start = typeof event.resultIndex === 'number' ? event.resultIndex : 0;
    for (let i = start; i < event.results.length; i++) {
      const result = event.results[i];
      const piece = result[0] && result[0].transcript ? result[0].transcript : '';
      if (result.isFinal) finalChunk += piece;
      else interimChunk += piece;
    }
    if (finalChunk.trim()) {
      finalisedText = (finalisedText + ' ' + finalChunk).trim();
      interimText = '';
    } else if (interimChunk.trim()) {
      interimText = interimChunk.trim();
    }
    recognisedText = (finalisedText + ' ' + interimText).trim();
    if (!recognisedText || transcriptFinished) return;
    heardTranscript = true;
    clearNoTranscriptTimer();
    // Show words as soon as they are heard; final words replace interim guesses.
    // During a follow-up the answer belongs in its labelled field, not over the
    // citizen's original request text.
    // A follow-up answer is short and addressed to one field. A final result is
    // enough to save it and ask the next question; the citizen does not have to
    // hunt for the Stop button after each answer.
    if (pendingVoiceField && finalChunk.trim()) {
      stopActiveRecognition();
      finishWithTranscript();
      return;
    }
    if (pendingVoiceField) fillSingleClaimField(pendingVoiceField, recognisedText);
    else {
      const box = $('textInput');
      box.value = recognisedText;
      fillClaimFields(recognisedText);
    }
    if (stopRequested || !$('micBtn').classList.contains('listening')) finishWithTranscript();
  };
  recognition.onerror = event => {
    clearNoTranscriptTimer();
    setListening(false);
    stopRequested = false;
    const error = event.error;
    if (error === 'aborted') {
      // Fired when stop() interrupts a start that had not produced speech yet.
      // It is not a hearing failure, so stay quiet.
      return;
    }
    if (error === 'network') {
      // Edge can report 'network' for an Urdu locale its service cannot handle.
      // Try the remaining Urdu tags, but never swap to English dictation.
      if (state.lang === 'ur' && navigator.onLine && tryNextUrduRecognitionLocale()) return;
      toast(t('micNetwork'), 'error');
      if (pendingVoiceField) {
        pendingVoiceField = null;
        restoreMicHint();
      }
      endVoiceSession();
      return;
    }
    if (error === 'not-allowed' || error === 'service-not-allowed') {
      toast(t('micPermission'), 'error');
    } else if (error === 'language-not-supported') {
      toast(t('micLangUnsupported'), 'error');
    } else if (error === 'audio-capture') {
      toast(t('micNoDevice'), 'error');
    } else if (error === 'no-speech' && !recognisedText.trim()) {
      const voicePickedUp = peakMicLevel > 0.05 || soundDetected;
      toast(voicePickedUp ? t('noTranscript') : t('noAudio'), 'error');
    } else {
      toast(t('micFailed'), 'error');
    }
    if (pendingVoiceField) {
      const field = pendingVoiceField;
      pendingVoiceField = null;
      restoreMicHint();
      if (error === 'no-speech' && voiceSession) {
        voicePromptTimer = setTimeout(() => askForVoiceField(field), 900);
      } else {
        endVoiceSession();
      }
    }
  };
  recognition.onend = () => {
    setListening(false);
    if (recognisedText.trim()) finishWithTranscript();
    else if (stopRequested) scheduleNoTranscript();
  };
  // Fallback signal for browsers that fire recognition sound events but block Web Audio.
  recognition.onsoundstart = () => {
    soundDetected = true;
    if (!analyser && !$('voiceLevelText').classList.contains('hidden')) {
      $('voiceLevelText').textContent = t('micHearing');
    }
  };
  updateMicControls();
}

function updateHeaderOffset() {
  const bar = $('prototypeBar');
  if (!bar) return;
  document.documentElement.style.setProperty('--strip-h', Math.ceil(bar.getBoundingClientRect().height) + 'px');
}

function updateNetwork() {
  const badge = $('netBadge');
  const text = badge.querySelector('[data-net-text]');
  if (text) text.textContent = navigator.onLine ? t('online') : t('offlineSaved');
  badge.classList.toggle('offline', !navigator.onLine);
}

function setActiveNav(id) {
  ['navHome', 'navCases', 'navHelp'].forEach(key => {
    const button = $(key);
    const active = key === id;
    button.classList.toggle('active', active);
    if (active) button.setAttribute('aria-current', 'page');
    else button.removeAttribute('aria-current');
  });
}

/* ---------------- Separate pages: hash routing for Home / Cases / Help ---------------- */
const VIEWS = { home: 'viewHome', cases: 'viewCases', help: 'viewHelp' };
const NAVS = { home: 'navHome', cases: 'navCases', help: 'navHelp' };

function currentView() {
  const hash = (location.hash || '').replace(/^#\/?/, '').toLowerCase();
  return VIEWS[hash] ? hash : 'home';
}

function applyView() {
  const view = currentView();
  Object.keys(VIEWS).forEach(key => {
    const el = $(VIEWS[key]);
    if (!el) return;
    const active = key === view;
    el.classList.toggle('active', active);
    el.hidden = !active;
  });
  setActiveNav(NAVS[view]);
  window.scrollTo(0, 0);
}

function goTo(view) {
  if (!VIEWS[view]) view = 'home';
  const target = '#/' + view;
  if (location.hash === target) applyView();
  else location.hash = target;
}

document.addEventListener('DOMContentLoaded', () => {
  applyLang();
  updateQueueBadge();
  initRecognition();
  setStatusIcon(null);

  $('loginForm').addEventListener('submit', event => {
    event.preventDefault();
    login($('emailInput').value.trim(), $('passwordInput').value);
  });
  $('showPasswordBtn').addEventListener('click', togglePasswordVisibility);
  document.querySelectorAll('.chip').forEach(btn =>
    btn.addEventListener('click', () => { $('emailInput').value = btn.dataset.email; }));
  $('logoutBtn').addEventListener('click', logout);
  $('langBtn').addEventListener('click', toggleLang);
  $('loginLangBtn').addEventListener('click', toggleLang);
  $('sendBtn').addEventListener('click', () => submitText($('textInput').value));
  $('textInput').addEventListener('input', () => {
    clearTimeout(claimTextTimer);
    claimTextTimer = setTimeout(() => fillClaimFields($('textInput').value), 450);
  });
  $('textInput').addEventListener('keydown', event => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      submitText($('textInput').value);
    }
  });
  Object.keys(CLAIM_FIELDS).forEach(field => {
    const input = $(CLAIM_FIELDS[field]);
    if (!input) return;
    const edited = () => markClaimEdited(field);
    input.addEventListener('input', edited);
    input.addEventListener('change', edited);
  });
  $('statusRefresh').addEventListener('click', refreshDashboard);
  $('casesRefresh').addEventListener('click', refreshDashboard);
  $('speakStatus').addEventListener('click', () => speak($('statusText').textContent));
  $('syncBtn').addEventListener('click', () => syncQueue());
  $('helpForm').addEventListener('submit', event => { event.preventDefault(); askHelp(); });
  $('checkVoicesBtn').addEventListener('click', () => renderVoiceDiag());
  $('testVoiceBtn').addEventListener('click', testUrduVoice);
  $('rolePanelBody').addEventListener('click', event => {
    const button = event.target.closest('button[data-review]');
    if (button) reviewFromPanel(button.dataset.caseId, button.dataset.review);
  });

  $('navHome').addEventListener('click', () => goTo('home'));
  $('navCases').addEventListener('click', () => goTo('cases'));
  $('navHelp').addEventListener('click', () => goTo('help'));
  window.addEventListener('hashchange', applyView);
  window.addEventListener('online', () => { updateNetwork(); if (queued().length) syncQueue(false); });
  window.addEventListener('offline', updateNetwork);
  window.addEventListener('resize', updateHeaderOffset);

  applyView();

  if (state.token) {
    $('loginScreen').classList.remove('active');
    $('appScreen').classList.add('active');
    // applyView() above already honours an existing #/home|#/cases|#/help hash.
    // Only a fresh login forces Home; a reload keeps the page the citizen was on.
    activateRoleWorkspace();
    refreshDashboard();
  }
});
