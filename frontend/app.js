// ===== ScamGuard AI — Multi-Mode Frontend v2.0 =====
const API_URL = "http://127.0.0.1:8000";
let riskChartInstance = null;
let analysisCount = 0;
let lastResultData = null;
let currentMode = "general";

// ===== MODE SELECTOR =====
function selectMode(mode, el) {
    currentMode = mode;
    document.querySelectorAll('.mode-card').forEach(c => c.classList.remove('active'));
    if (el) el.classList.add('active');
}

// ===== NAVIGATION =====
function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    const el = document.getElementById('page-' + page);
    if (el) el.classList.add('active');
    const link = document.querySelector(`.nav-link[data-page="${page}"]`);
    if (link) link.classList.add('active');
    document.getElementById('navLinks').classList.remove('open');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    if (page === 'stats') initStatsCharts();
}

function toggleMobileMenu() {
    const nav = document.getElementById('navLinks');
    const icon = document.getElementById('menuIcon');
    nav.classList.toggle('open');
    icon.className = nav.classList.contains('open') ? 'ri-close-line' : 'ri-menu-3-line';
}

// ===== TABS =====
function switchTab(type, btn) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const el = document.getElementById('content-' + type);
    if (el) el.classList.add('active');
    if (btn) btn.classList.add('active');
}

// ===== CHAR COUNT =====
const postText = document.getElementById('postText');
const charCount = document.getElementById('charCount');
if (postText && charCount) {
    postText.addEventListener('input', () => { charCount.textContent = postText.value.length + ' حرف'; });
}

// ===== FILE UPLOAD =====
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileAnalyzeBtn = document.getElementById('fileAnalyzeBtn');
const fileSelected = document.getElementById('fileSelected');

if (dropZone) {
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.style.borderColor = 'var(--blue)'; });
    dropZone.addEventListener('dragleave', () => { dropZone.style.borderColor = ''; });
    dropZone.addEventListener('drop', e => { e.preventDefault(); dropZone.style.borderColor = ''; if (e.dataTransfer.files.length) { fileInput.files = e.dataTransfer.files; handleFile(); } });
    fileInput.addEventListener('change', handleFile);
}

function handleFile() {
    if (fileInput.files.length > 0) {
        document.getElementById('fileName').textContent = fileInput.files[0].name;
        fileSelected.classList.remove('hidden');
        dropZone.style.display = 'none';
        fileAnalyzeBtn.disabled = false;
        fileAnalyzeBtn.classList.remove('disabled');
    }
}

function clearFile() {
    fileInput.value = '';
    fileSelected.classList.add('hidden');
    dropZone.style.display = '';
    fileAnalyzeBtn.disabled = true;
    fileAnalyzeBtn.classList.add('disabled');
}

// ===== API CALLS =====
async function postToAPI(endpoint, payload, isFile = false) {
    showLoading(true);
    try {
        let opts = { method: 'POST' };
        if (isFile) {
            const fd = new FormData();
            fd.append('file', payload);
            fd.append('mode', currentMode);
            opts.body = fd;
        } else {
            opts.headers = { 'Content-Type': 'application/json' };
            opts.body = JSON.stringify(payload);
        }
        const res = await fetch(`${API_URL}${endpoint}`, opts);
        let json;
        try { json = await res.json(); } catch { throw new Error("فشل في قراءة استجابة الخادم"); }
        if (!res.ok) throw new Error(json.detail || "فشل في معالجة الطلب");
        displayResults(json.data);
        analysisCount++;
        const c = document.getElementById('analysisCount');
        if (c) c.textContent = analysisCount;
    } catch (err) { toast(err.message); } finally { showLoading(false); }
}

function analyzeText() {
    const text = document.getElementById('postText').value;
    if (!text.trim()) return toast("أدخل نصاً للتحليل");
    postToAPI('/api/v1/analyze', { post_text: text, mode: currentMode });
}
function analyzeFile() {
    const f = document.getElementById('fileInput').files[0];
    if (!f) return;
    postToAPI('/api/v1/analyze-file', f, true);
}
function analyzeUrl() {
    const url = document.getElementById('urlInput').value;
    if (!url.trim()) return toast("أدخل رابطاً صحيحاً");
    postToAPI('/api/v1/analyze-url', { url, mode: currentMode });
}
function testExample(el) {
    const text = el.querySelector('p').textContent;
    document.getElementById('postText').value = text;
    charCount.textContent = text.length + ' حرف';
    showPage('home');
    setTimeout(() => analyzeText(), 300);
}

function showLoading(show) {
    const o = document.getElementById('loadingOverlay');
    if (o) o.classList.toggle('hidden', !show);
    if (show) { const r = document.getElementById('resultsPanel'); if (r) r.classList.add('hidden'); }
}

function toast(msg) {
    const t = document.createElement('div');
    t.style.cssText = 'position:fixed;top:80px;left:50%;transform:translateX(-50%);z-index:999;padding:12px 24px;border-radius:12px;background:rgba(248,81,73,.12);border:1px solid rgba(248,81,73,.25);color:#f85149;font-weight:600;font-size:.85rem;backdrop-filter:blur(10px);display:flex;align-items:center;gap:8px;font-family:"IBM Plex Sans Arabic",sans-serif;animation:fi .3s ease';
    t.innerHTML = `<i class="ri-error-warning-line"></i> ${msg}`;
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity .4s'; setTimeout(() => t.remove(), 400); }, 3000);
}

// ===== DISPLAY RESULTS =====
// ===== DISPLAY RESULTS =====
function displayResults(data) {
    lastResultData = data;
    saveToHistory(data);
    const panel = document.getElementById('resultsPanel');
    const vr = document.getElementById('verdictResult');
    const vi = document.getElementById('verdictIcon');
    const vc = document.querySelector('.verdict-card');
    const va = document.getElementById('verdictAction');
    const vre = document.getElementById('verdictResultEn');

    document.getElementById('timestamp').textContent = new Date().toLocaleTimeString('ar-SA') + ' — ' + new Date().toLocaleDateString('ar-SA');

    // Verdict
    vr.textContent = data.classification_ar || data.classification;
    vre.textContent = data.classification;
    vr.className = 'verdict-result'; vi.className = 'verdict-icon'; va.className = 'verdict-action';

    if (data.classification.includes("Scam")) {
        vr.classList.add('danger'); vi.classList.add('danger');
        vi.innerHTML = '<i class="ri-skull-2-line"></i>';
        va.classList.add('danger');
        va.innerHTML = '<i class="ri-forbid-2-line"></i> حظر فوري والإبلاغ';
    } else if (data.classification.includes("Suspicious")) {
        vr.classList.add('warning'); vi.classList.add('warning');
        vi.innerHTML = '<i class="ri-alarm-warning-line"></i>';
        va.classList.add('warning');
        va.innerHTML = '<i class="ri-flag-line"></i> وضع علامة تحذيرية';
    } else {
        vr.classList.add('safe'); vi.classList.add('safe');
        vi.innerHTML = '<i class="ri-shield-check-line"></i>';
        va.classList.add('safe');
        va.innerHTML = '<i class="ri-checkbox-circle-line"></i> محتوى آمن';
    }

    // Keywords
    const kb = document.getElementById('keywordsBox');
    kb.innerHTML = '';
    if (!data.keyword_map || data.keyword_map.length === 0) {
        kb.innerHTML = '<span class="empty-msg">لم يتم رصد كلمات مريبة</span>';
    } else {
        data.keyword_map.forEach(k => {
            const tag = document.createElement('span');
            tag.className = `kw-tag ${k.type}`;
            tag.innerHTML = `${k.word} <span class="kw-imp">${k.impact}</span>`;
            kb.appendChild(tag);
        });
    }

    // Indicators
    const on = '<i class="ri-checkbox-circle-fill" style="color:var(--red);font-size:1.1rem"></i>';
    const off = '<i class="ri-checkbox-blank-circle-line" style="color:var(--txt3);font-size:1.1rem"></i>';
    document.getElementById('featFinancial').innerHTML = data.insights.financial_requests_found ? on : off;
    document.getElementById('featUrgency').innerHTML = data.insights.urgency_detected ? on : off;
    document.getElementById('featReligious').innerHTML = data.insights.emotional_manipulation_detected ? on : off;

    // ===== THREATS =====
    const tb = document.getElementById('threatsBox');
    tb.innerHTML = '';
    if (data.threats && data.threats.length > 0) {
        data.threats.forEach(t => {
            const div = document.createElement('div');
            div.className = 'threat-item';
            const words = t.matched_words.map(w => `<span>${w.word}</span>`).join('');
            div.innerHTML = `
                <div class="ti-icon"><i class="ri-error-warning-line"></i></div>
                <div class="ti-body">
                    <strong>${t.name_ar} — ${t.name_en}</strong>
                    <small>Severity: ${t.severity_ar} (${t.severity_en}) | ${t.match_count} indicators</small>
                    <div class="threat-words">${words}</div>
                </div>
                <div class="ti-score ${t.severity_en}">${Math.round(t.score * 100)}%</div>`;
            tb.appendChild(div);
        });
    } else {
        tb.innerHTML = '<span class="empty-msg"><i class="ri-shield-check-line" style="color:var(--green)"></i> لا توجد تهديدات مرصودة — No threats detected</span>';
    }

    // ===== EMOTIONS =====
    if (data.emotions) {
        const emo = data.emotions;
        setEmoBar('emoFear', 'emoFearVal', emo.fear_level);
        setEmoBar('emoHope', 'emoHopeVal', emo.hope_level);
        setEmoBar('emoGuilt', 'emoGuiltVal', emo.guilt_level);
        setEmoBar('emoUrgency', 'emoUrgencyVal', emo.urgency_level);

        const sentEl = document.getElementById('emoSentiment');
        if (emo.bert_available) {
            const icons = { positive: '<i class="ri-emotion-happy-line" style="color:var(--green)"></i>', negative: '<i class="ri-emotion-unhappy-line" style="color:var(--red)"></i>', neutral: '<i class="ri-emotion-normal-line" style="color:var(--txt2)"></i>' };
            sentEl.innerHTML = `<strong>BERT Sentiment:</strong> ${icons[emo.sentiment] || '❓'} ${emo.sentiment_ar} (${emo.sentiment}) — Confidence: ${Math.round(emo.confidence * 100)}% | <strong>Dominant:</strong> ${emo.dominant_emotion_ar} (${emo.dominant_emotion})`;
        } else {
            sentEl.innerHTML = '<i class="ri-information-line"></i> BERT loading... Keyword analysis only.';
        }
        document.getElementById('emotionSection').classList.remove('hidden');
    }

    // ===== RECOMMENDATIONS =====
    const rb = document.getElementById('recsBox');
    rb.innerHTML = '';
    if (data.recommendations && data.recommendations.length > 0) {
        data.recommendations.forEach(r => {
            const div = document.createElement('div');
            div.className = `rec-item ${r.severity}`;
            div.innerHTML = `<div>${r.text_ar}</div><div style="color:var(--txt3);font-size:.7rem;margin-top:4px">${r.text_en}</div>`;
            rb.appendChild(div);
        });
    } else {
        rb.innerHTML = '<span class="empty-msg">لا توجد توصيات</span>';
    }

    updateRiskGauge(data.risk_score);
    panel.classList.remove('hidden');
    panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setEmoBar(barId, valId, level) {
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);
    if (bar) bar.style.width = Math.round(level * 100) + '%';
    if (val) val.textContent = Math.round(level * 100) + '%';
}

// ===== RISK GAUGE =====
function updateRiskGauge(score) {
    const c = document.getElementById('riskGauge'); if (!c) return;
    const pct = Math.round(score * 100);
    document.getElementById('riskPct').textContent = pct + '%';
    let color = '#3fb950';
    if (pct > 50) color = '#d29922';
    if (pct > 80) color = '#f85149';
    if (riskChartInstance) riskChartInstance.destroy();
    riskChartInstance = new Chart(c.getContext('2d'), {
        type: 'doughnut',
        data: { datasets: [{ data: [pct, 100 - pct], backgroundColor: [color, 'rgba(255,255,255,.04)'], borderWidth: 0, cutout: '78%', circumference: 240, rotation: 240 }] },
        options: { responsive: true, maintainAspectRatio: true, plugins: { tooltip: { enabled: false }, legend: { display: false } }, animation: { duration: 800 } }
    });
}

// ===== DOWNLOAD REPORT (PDF) =====
async function downloadReport() {
    if (!lastResultData) return toast("لا يوجد تقرير لتنزيله");

    // Show loading state on button
    const btn = document.querySelector('.results-top-actions button');
    if (btn) btn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> جاري إصدار التقرير...';

    const d = lastResultData;
    const time = new Date().toLocaleString('ar-SA');

    // Determine Verdict Colors
    let vColor = '#2e7d32', vBg = '#e8f5e9', vIcon = 'ri-shield-check-line';
    if (d.classification.includes('Scam')) { vColor = '#d32f2f'; vBg = '#ffebee'; vIcon = 'ri-skull-2-line'; }
    else if (d.classification.includes('Suspicious')) { vColor = '#f57f17'; vBg = '#fff8e1'; vIcon = 'ri-alarm-warning-line'; }

    // Build content dynamically
    const keywords = (d.keyword_map && d.keyword_map.length > 0) ? d.keyword_map.map(k => `<span style="display:inline-block;padding:4px 8px;background:#f0f0f0;border-radius:4px;margin:3px;font-size:12px;color:#333">${k.word} <b style="color:${k.type === 'danger' ? '#d32f2f' : '#f57f17'}">${k.impact}</b></span>`).join('') : '<p style="color:#666">لم يتم رصد كلمات مريبة</p>';

    const threats = (d.threats && d.threats.length > 0) ? d.threats.map(t => `<div style="padding:10px;border-right:3px solid ${t.severity_en === 'critical' ? '#d32f2f' : (t.severity_en === 'high' ? '#f57f17' : '#1976d2')};background:#f8f9fa;margin-bottom:8px"><strong>${t.name_ar}</strong> (${t.name_en}) <br><span style="color:#666;font-size:12px">خطورة: ${t.severity_ar} | مطابقة: ${Math.round(t.score * 100)}%</span></div>`).join('') : '<p style="color:#666">لا توجد تهديدات مرصودة</p>';

    const recs = (d.recommendations && d.recommendations.length > 0) ? d.recommendations.map(r => `<li style="margin-bottom:8px;font-size:13px">${r.text_ar} <br><span style="color:#888;font-size:11px">${r.text_en}</span></li>`).join('') : '<li>لا توجد توصيات</li>';

    // Create a temporary container for the PDF content
    const container = document.createElement('div');
    // Position it safely off-screen below the viewport so the browser fully renders it
    container.style.position = 'fixed';
    container.style.top = '100vh';
    container.style.left = '0';
    container.style.width = '800px';
    container.style.padding = '40px';
    container.style.fontFamily = "'IBM Plex Sans Arabic', 'Noto Kufi Arabic', Arial, sans-serif";
    container.style.backgroundColor = '#ffffff';
    container.style.color = '#111111';
    container.dir = 'rtl';

    container.innerHTML = `
        <div style="text-align:center;border-bottom:2px solid #eeeeee;padding-bottom:20px;margin-bottom:30px">
            <h1 style="color:#1a1a2e;font-size:24px;margin-bottom:5px;font-family:'Noto Kufi Arabic',sans-serif">ScamGuard AI</h1>
            <p style="color:#666666;font-size:14px;margin:0">تقرير الفحص الأمني الشامل | Security Analysis Report</p>
        </div>

        <div style="background:${vBg};color:${vColor};border:2px solid ${vColor};border-radius:8px;padding:20px;text-align:center;margin-bottom:30px">
            <h2 style="margin:0;font-size:22px;font-family:'Noto Kufi Arabic',sans-serif">${d.classification_ar}</h2>
            <p style="margin:5px 0 0 0;font-size:14px;opacity:0.9">${d.classification}</p>
        </div>

        <table style="width:100%;border-collapse:collapse;margin-bottom:30px;font-size:13px;color:#333333">
            <tr><td style="padding:10px;border-bottom:1px solid #eeeeee;color:#555555;width:30%">تاريخ التقرير Date</td><td style="padding:10px;border-bottom:1px solid #eeeeee;font-weight:bold">${time}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #eeeeee;color:#555555">وضع التحليل Mode</td><td style="padding:10px;border-bottom:1px solid #eeeeee;font-weight:bold">${d.mode}</td></tr>
            <tr><td style="padding:10px;border-bottom:1px solid #eeeeee;color:#555555">كثافة الخطر Risk Score</td><td style="padding:10px;border-bottom:1px solid #eeeeee;font-weight:bold">${Math.round(d.risk_score * 100)}%</td></tr>
        </table>

        <div style="margin-bottom:25px;page-break-inside:avoid">
            <h3 style="color:#1a1a2e;border-bottom:1px solid #eeeeee;padding-bottom:5px;font-family:'Noto Kufi Arabic',sans-serif">النص المحلل Analyzed Text</h3>
            <div style="background:#f8f9fa;padding:15px;border-radius:6px;font-size:12px;line-height:1.6;color:#333333;border:1px solid #e0e0e0;white-space:pre-wrap">${d.original_text}</div>
        </div>

        <div style="display:flex;gap:20px;margin-bottom:25px;page-break-inside:avoid">
            <div style="flex:1">
                <h3 style="color:#1a1a2e;border-bottom:1px solid #eeeeee;padding-bottom:5px;font-family:'Noto Kufi Arabic',sans-serif">التهديدات Threats</h3>
                ${threats}
            </div>
            <div style="flex:1">
                <h3 style="color:#1a1a2e;border-bottom:1px solid #eeeeee;padding-bottom:5px;font-family:'Noto Kufi Arabic',sans-serif">كلمات مفتاحية Keywords</h3>
                <div>${keywords}</div>
            </div>
        </div>

        ${d.emotions ? `
        <div style="margin-bottom:25px;page-break-inside:avoid">
            <h3 style="color:#1a1a2e;border-bottom:1px solid #eeeeee;padding-bottom:5px;font-family:'Noto Kufi Arabic',sans-serif">تحليل المشاعر BERT Emotions</h3>
            <table style="width:100%;font-size:12px;background:#fcfcfc;border:1px solid #eeeeee">
                <tr>
                    <td style="padding:10px;border-right:1px solid #eee">الخوف: <b>${Math.round(d.emotions.fear_level * 100)}%</b></td>
                    <td style="padding:10px;border-right:1px solid #eee">الأمل: <b>${Math.round(d.emotions.hope_level * 100)}%</b></td>
                    <td style="padding:10px;border-right:1px solid #eee">الذنب: <b>${Math.round(d.emotions.guilt_level * 100)}%</b></td>
                    <td style="padding:10px">الاستعجال: <b>${Math.round(d.emotions.urgency_level * 100)}%</b></td>
                </tr>
            </table>
            <div style="margin-top:10px;padding:12px;background:#e3f2fd;border-radius:4px;font-size:12px;color:#1565c0;border:1px solid #bbdefb">
                <b>الانطباع العام Sentiment:</b> ${d.emotions.sentiment_ar} (${Math.round(d.emotions.confidence * 100)}%) | <b>الشعور الغالب:</b> ${d.emotions.dominant_emotion_ar}
            </div>
        </div>` : ''}

        <div style="margin-bottom:30px;page-break-inside:avoid">
            <h3 style="color:#1a1a2e;border-bottom:1px solid #eeeeee;padding-bottom:5px;font-family:'Noto Kufi Arabic',sans-serif">التوصيات Recommendations</h3>
            <ul style="padding-right:20px;color:#333333;margin:10px 0;line-height:1.7">${recs}</ul>
        </div>

        <div style="text-align:center;border-top:1px solid #eeeeee;padding-top:15px;color:#777777;font-size:11px;margin-top:auto">
            <p style="margin:0;font-weight:bold">تم توليد هذا التقرير تلقائياً بواسطة ScamGuard AI - تقنية Linear SVM + BERT NLP</p>
            <p style="margin:4px 0 0 0">Developed by Eng. Abdessamad Bourkibate — Academic Research 2026 ©</p>
        </div>
    `;

    document.body.appendChild(container);

    // Give browser time to paint the element fully
    await new Promise(r => setTimeout(r, 600));

    const opt = {
        margin: [0.5, 0.5, 0.5, 0.5],
        filename: `ScamGuard_Report_${Date.now()}.pdf`,
        image: { type: 'jpeg', quality: 1.0 },
        html2canvas: { scale: 2, useCORS: true, logging: true, background: '#ffffff' },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    try {
        await html2pdf().set(opt).from(container).save();
        toast("تم تحميل التقرير (PDF) بنجاح!");
    } catch (err) {
        console.error("PDF Generate Error:", err);
        toast("حدث خطأ أثناء تحميل التقرير (PDF)");
    } finally {
        container.remove();
        if (btn) btn.innerHTML = '<i class="ri-download-2-line"></i> Download';
    }
}

// ===== FEATURE CHART =====
function initFeatureChart() {
    const c = document.getElementById('featureChart'); if (!c) return;
    new Chart(c.getContext('2d'), {
        type: 'polarArea',
        data: { labels: ['Financial', 'Urgency', 'Religious', 'Grooming', 'Bullying'], datasets: [{ data: [80, 60, 45, 70, 50], backgroundColor: ['rgba(248,81,73,.4)', 'rgba(210,153,34,.4)', 'rgba(88,166,255,.4)', 'rgba(255,140,0,.4)', 'rgba(188,140,255,.4)'], borderColor: ['#f85149', '#d29922', '#58a6ff', '#ff8c00', '#bc8cff'], borderWidth: 1.5 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { display: false }, pointLabels: { display: false } } }, plugins: { legend: { position: 'bottom', labels: { color: '#8b949e', font: { family: 'Inter', size: 10 }, padding: 10, usePointStyle: true } } } }
    });
}

// ===== STATS CHARTS =====
let statsInit = false;
function initStatsCharts() {
    if (statsInit) return; statsInit = true;
    const fnt = { family: 'IBM Plex Sans Arabic', size: 11 };
    const gc = 'rgba(255,255,255,.04)';

    new Chart(document.getElementById('dataDistChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: ['Legitimate (187,777)', 'Scam (20,880)', 'Suspicious (1,294)'], datasets: [{ data: [187777, 20880, 1294], backgroundColor: ['rgba(63,185,80,.6)', 'rgba(248,81,73,.6)', 'rgba(210,153,34,.6)'], borderColor: ['#3fb950', '#f85149', '#d29922'], borderWidth: 2, hoverOffset: 8 }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: { legend: { position: 'bottom', labels: { color: '#8b949e', font: fnt, padding: 14, usePointStyle: true } } } }
    });

    new Chart(document.getElementById('modelCompChart').getContext('2d'), {
        type: 'bar',
        data: { labels: ['Linear SVM', 'SGD Classifier', 'Logistic Regression'], datasets: [{ label: 'Accuracy %', data: [99.35, 97.77, 93.67], backgroundColor: ['rgba(63,185,80,.5)', 'rgba(88,166,255,.5)', 'rgba(210,153,34,.5)'], borderColor: ['#3fb950', '#58a6ff', '#d29922'], borderWidth: 2, borderRadius: 8, barPercentage: 0.6 }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', scales: { x: { min: 85, max: 100, grid: { color: gc }, ticks: { color: '#8b949e', font: fnt, callback: v => v + '%' } }, y: { grid: { display: false }, ticks: { color: '#f0f6fc', font: { ...fnt, weight: 'bold' } } } }, plugins: { legend: { display: false } } }
    });

    new Chart(document.getElementById('confusionChart').getContext('2d'), {
        type: 'bar',
        data: { labels: ['Legitimate', 'Suspicious', 'Scam'], datasets: [{ label: 'Correct', data: [37378, 244, 4095], backgroundColor: 'rgba(63,185,80,.5)', borderColor: '#3fb950', borderWidth: 1.5, borderRadius: 6 }, { label: 'Errors', data: [177, 15, 81], backgroundColor: 'rgba(248,81,73,.5)', borderColor: '#f85149', borderWidth: 1.5, borderRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { x: { grid: { display: false }, ticks: { color: '#f0f6fc', font: fnt } }, y: { grid: { color: gc }, ticks: { color: '#8b949e', font: fnt } } }, plugins: { legend: { position: 'bottom', labels: { color: '#8b949e', font: fnt, usePointStyle: true } } } }
    });

    new Chart(document.getElementById('metricsChart').getContext('2d'), {
        type: 'radar',
        data: { labels: ['Precision', 'Recall', 'F1-Score'], datasets: [{ label: 'Legitimate', data: [1.00, 1.00, 1.00], borderColor: '#3fb950', backgroundColor: 'rgba(63,185,80,.1)', pointBackgroundColor: '#3fb950', borderWidth: 2 }, { label: 'Suspicious', data: [0.98, 0.94, 0.96], borderColor: '#d29922', backgroundColor: 'rgba(210,153,34,.1)', pointBackgroundColor: '#d29922', borderWidth: 2 }, { label: 'Scam', data: [0.96, 0.98, 0.97], borderColor: '#f85149', backgroundColor: 'rgba(248,81,73,.1)', pointBackgroundColor: '#f85149', borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { min: 0.8, max: 1.0, grid: { color: gc }, angleLines: { color: gc }, ticks: { color: '#8b949e', font: fnt, backdropColor: 'transparent' }, pointLabels: { color: '#f0f6fc', font: { ...fnt, size: 12 } } } }, plugins: { legend: { position: 'bottom', labels: { color: '#8b949e', font: fnt, usePointStyle: true } } } }
    });
}

// ===== NEURAL NETWORK BG =====
function initNeuralBg() {
    const canvas = document.getElementById('neuralCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width, height, particles = [];

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 1.5 + 0.5;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > width) this.vx = -this.vx;
            if (this.y < 0 || this.y > height) this.vy = -this.vy;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(88, 166, 255, 0.4)';
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        const numParticles = Math.min(Math.floor((width * height) / 15000), 100);
        for (let i = 0; i < numParticles; i++) {
            particles.push(new Particle());
        }
    }
    initParticles();

    function animate() {
        ctx.clearRect(0, 0, width, height);

        for (let i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();

            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 150) {
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(88, 166, 255, ${0.15 - dist / 1000})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }

    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(initParticles, 200);
    });

    animate();
}

// ===== HISTORY MANAGEMENT =====
const MAX_HISTORY = 10;
function saveToHistory(data) {
    let history = JSON.parse(localStorage.getItem('scamguard_history') || '[]');
    const item = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        classification: data.classification,
        classification_ar: data.classification_ar,
        risk_score: data.risk_score,
        text: data.original_text.substring(0, 100) + (data.original_text.length > 100 ? '...' : '')
    };
    history.unshift(item);
    if (history.length > MAX_HISTORY) history.pop();
    localStorage.setItem('scamguard_history', JSON.stringify(history));
    renderHistory();
}

function toggleHistory() {
    const modal = document.getElementById('historyModal');
    if (!modal) return;
    const isHidden = modal.classList.contains('hidden');
    modal.classList.toggle('hidden');
    if (isHidden) renderHistory();
}

function clearHistory() {
    if (confirm('هل أنت متأكد من مسح سجل الفحوصات؟')) {
        localStorage.removeItem('scamguard_history');
        renderHistory();
        toast("تم مسح السجل بنجاح");
    }
}

function renderHistory() {
    const list = document.getElementById('historyList');
    if (!list) return;
    const history = JSON.parse(localStorage.getItem('scamguard_history') || '[]');
    list.innerHTML = '';

    if (history.length === 0) {
        list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--txt3)"><i class="ri-history-line" style="font-size:2rem;display:block;margin-bottom:10px;opacity:.3"></i> لا يوجد سجل فحوصات حالياً</div>';
        return;
    }

    history.forEach(item => {
        const div = document.createElement('div');
        div.style.cssText = 'padding:15px;border:1px solid var(--bdr);border-radius:12px;margin-bottom:10px;background:rgba(255,255,255,.02);cursor:default';
        const date = new Date(item.timestamp).toLocaleString('ar-SA', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' });

        let clr = 'var(--green)';
        if (item.classification.includes('Scam')) clr = 'var(--red)';
        else if (item.classification.includes('Suspicious')) clr = 'var(--amber)';

        div.innerHTML = `
            <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                <span style="font-size:.7rem;color:var(--txt3)">${date}</span>
                <span style="font-size:.75rem;font-weight:bold;color:${clr}">${item.classification_ar} (${Math.round(item.risk_score * 100)}%)</span>
            </div>
            <p style="font-size:.8rem;color:var(--txt2);margin:0;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${item.text}</p>
        `;
        list.appendChild(div);
    });
}

// ===== INIT =====
window.addEventListener('DOMContentLoaded', () => {
    initFeatureChart();
    updateRiskGauge(0);
    initNeuralBg();
    renderHistory();
});
