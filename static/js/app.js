document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const tabPaste = document.getElementById('tab-paste');
    const tabUpload = document.getElementById('tab-upload');
    const contentPaste = document.getElementById('content-paste');
    const contentUpload = document.getElementById('content-upload');

    // Controls
    const csvTextArea = document.getElementById('csv-text');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileDetails = document.getElementById('file-details');
    const fileNameSpan = document.getElementById('file-name');
    const fileSizeSpan = document.getElementById('file-size');
    const removeFileBtn = document.getElementById('remove-file-btn');

    const delimiterSelect = document.getElementById('delimiter-select');
    const formatSelect = document.getElementById('format-select');
    const keyColumnGroup = document.getElementById('key-column-group');
    const keyColumnInput = document.getElementById('key-column-input');
    const headerToggle = document.getElementById('header-toggle');
    const prettyToggle = document.getElementById('pretty-toggle');

    const previewBtn = document.getElementById('preview-btn');
    const convertBtn = document.getElementById('convert-btn');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');

    const statusMessage = document.getElementById('status-message');
    const tablePreviewContainer = document.getElementById('table-preview-container');
    const previewTable = document.getElementById('preview-table');
    const jsonOutput = document.getElementById('json-output');

    let currentFile = null;
    let activeTab = 'paste';
    let currentJobId = null;

    // Tabs
    tabPaste.addEventListener('click', () => {
        activeTab = 'paste';
        tabPaste.classList.add('active');
        tabUpload.classList.remove('active');
        contentPaste.classList.remove('hidden');
        contentUpload.classList.add('hidden');
    });

    tabUpload.addEventListener('click', () => {
        activeTab = 'upload';
        tabUpload.classList.add('active');
        tabPaste.classList.remove('active');
        contentUpload.classList.remove('hidden');
        contentPaste.classList.add('hidden');
    });

    // Format selection
    formatSelect.addEventListener('change', () => {
        keyColumnGroup.style.display = formatSelect.value === 'nested_json' ? 'flex' : 'none';
    });

    // File Drag & Drop
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files[0]) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    removeFileBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        fileDetails.classList.add('hidden');
        dropZone.classList.remove('hidden');
    });

    function handleFileSelect(file) {
        currentFile = file;
        fileNameSpan.textContent = file.name;
        fileSizeSpan.textContent = (file.size / 1024).toFixed(1) + ' KB';
        fileDetails.classList.remove('hidden');
        dropZone.classList.add('hidden');
    }

    function showStatus(text, type = 'success') {
        statusMessage.textContent = text;
        statusMessage.className = `status-message ${type}`;
        statusMessage.classList.remove('hidden');
        setTimeout(() => statusMessage.classList.add('hidden'), 5000);
    }

    // Preview
    previewBtn.addEventListener('click', async () => {
        const formData = new FormData();
        const delim = delimiterSelect.value;
        const hasHeader = headerToggle.checked;

        if (activeTab === 'upload') {
            if (!currentFile) {
                showStatus('Please select a file to preview.', 'error');
                return;
            }
            formData.append('file', currentFile);
        } else {
            const text = csvTextArea.value.trim();
            if (!text) {
                showStatus('Please enter CSV text to preview.', 'error');
                return;
            }
            formData.append('text', text);
        }

        formData.append('delimiter', delim);
        formData.append('hasHeader', hasHeader);

        try {
            previewBtn.disabled = true;
            previewBtn.textContent = 'Analyzing...';
            const res = await fetch('/api/preview', { method: 'POST', body: formData });
            const data = await res.json();

            if (!res.ok) throw new Error(data.error || 'Preview failed');

            renderTablePreview(data.data);
            showStatus(`Preview generated (${data.previewRows} of ${data.totalRows} rows). Delimiter: '${data.delimiter}'`, 'success');
        } catch (err) {
            showStatus(err.message, 'error');
        } finally {
            previewBtn.disabled = false;
            previewBtn.textContent = 'Preview Table';
        }
    });

    function renderTablePreview(rows) {
        if (!rows || rows.length === 0) {
            tablePreviewContainer.classList.add('hidden');
            return;
        }

        previewTable.innerHTML = '';
        tablePreviewContainer.classList.remove('hidden');

        let headers = [];
        if (typeof rows[0] === 'object' && !Array.isArray(rows[0])) {
            headers = Object.keys(rows[0]);
            const headerRow = document.createElement('tr');
            headers.forEach(h => {
                const th = document.createElement('th');
                th.textContent = h;
                headerRow.appendChild(th);
            });
            previewTable.appendChild(headerRow);

            rows.forEach(r => {
                const tr = document.createElement('tr');
                headers.forEach(h => {
                    const td = document.createElement('td');
                    td.textContent = r[h] !== undefined ? r[h] : '';
                    tr.appendChild(td);
                });
                previewTable.appendChild(tr);
            });
        } else if (Array.isArray(rows[0])) {
            rows.forEach((row, i) => {
                const tr = document.createElement('tr');
                row.forEach(cell => {
                    const el = document.createElement(i === 0 ? 'th' : 'td');
                    el.textContent = cell;
                    tr.appendChild(el);
                });
                previewTable.appendChild(tr);
            });
        }
    }

    // Convert
    convertBtn.addEventListener('click', async () => {
        const formData = new FormData();
        const delim = delimiterSelect.value;
        const fmt = formatSelect.value;
        const hasHeader = headerToggle.checked;
        const pretty = prettyToggle.checked;
        const keyCol = keyColumnInput.value.trim();

        if (activeTab === 'upload') {
            if (!currentFile) {
                showStatus('Please select a file to convert.', 'error');
                return;
            }
            formData.append('file', currentFile);
        } else {
            const text = csvTextArea.value.trim();
            if (!text) {
                showStatus('Please enter CSV text to convert.', 'error');
                return;
            }
            formData.append('text', text);
        }

        formData.append('delimiter', delim);
        formData.append('format', fmt);
        formData.append('hasHeader', hasHeader);
        formData.append('prettyPrint', pretty);
        if (fmt === 'nested_json' && keyCol) {
            formData.append('keyColumn', keyCol);
        }

        try {
            convertBtn.disabled = true;
            convertBtn.textContent = 'Converting...';
            const res = await fetch('/api/convert', { method: 'POST', body: formData });
            const data = await res.json();

            if (!res.ok) throw new Error(data.error || 'Conversion failed');

            currentJobId = data.jobId;
            jsonOutput.querySelector('code').textContent = data.jsonString;
            showStatus(`Successfully converted ${data.rowCount} records into ${data.format}!`, 'success');
        } catch (err) {
            showStatus(err.message, 'error');
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = 'Convert to JSON';
        }
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', () => {
        const text = jsonOutput.querySelector('code').textContent;
        if (!text || text.startsWith('//')) {
            showStatus('Nothing to copy yet.', 'error');
            return;
        }
        navigator.clipboard.writeText(text).then(() => {
            showStatus('Copied JSON to clipboard!', 'success');
        });
    });

    // Download
    downloadBtn.addEventListener('click', () => {
        if (!currentJobId) {
            const text = jsonOutput.querySelector('code').textContent;
            if (!text || text.startsWith('//')) {
                showStatus('No converted JSON available for download.', 'error');
                return;
            }
            const blob = new Blob([text], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted.json';
            a.click();
            URL.revokeObjectURL(url);
            showStatus('Downloaded JSON file.', 'success');
            return;
        }
        window.location.href = `/api/download/${currentJobId}`;
    });
});
