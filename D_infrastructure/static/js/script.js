document.addEventListener('DOMContentLoaded', () => {
    // DOM Elemente zentral verwalten
    const ui = {
        dropZone: document.getElementById('drop-zone'),
        fileInput: document.getElementById('file'),
        fileInfo: document.getElementById('file-info'),
        resultArea: document.getElementById('result-area'),
        resultTitle: document.getElementById('result-title'),
        noResultsMessage: document.getElementById('no-results-message'),
        resultsContent: document.getElementById('results-content'),
        resultBody: document.getElementById('result-body'),
        downloadBtn: document.getElementById('download-btn'),
        loading: document.getElementById('loading'),
        // Filter
        filterJa: document.getElementById('filter-ja'),
        filterNein: document.getElementById('filter-nein'),
        filterStueck: document.getElementById('filter-stueck'),
        filterKg: document.getElementById('filter-kg'),
        groupFilter: document.getElementById('group-filter'),
        filterError: document.getElementById('filter-error'),
        // Modal
        modal: document.getElementById('image-modal'),
        explanationImg: document.getElementById('explanation-img'),
        modalImg: document.getElementById('modal-img'),
        closeModal: document.querySelector('.close')
    };

    // App Status
    let state = {
        results: [],
        filename: ""
    };

    // Konfiguration sicher aus dem DOM laden
    const config = (() => {
        const configElement = document.getElementById('app-config');
        try {
            return configElement ? JSON.parse(configElement.textContent) : { configPostfix: "_vorschlaege_IN_KASSA" };
        } catch (e) {
            console.error("Fehler beim Laden der Konfiguration:", e);
            return { configPostfix: "_vorschlaege_IN_KASSA" };
        }
    })();

    // --- Modal Logik ---
    if (ui.explanationImg && ui.modal) {
        ui.explanationImg.addEventListener('click', () => {
            ui.modal.style.display = "block";
            ui.modalImg.src = ui.explanationImg.src;
        });

        const hideModal = () => ui.modal.style.display = "none";
        if (ui.closeModal) ui.closeModal.addEventListener('click', hideModal);
        window.addEventListener('click', (e) => { if (e.target === ui.modal) hideModal(); });
    }

    // --- Hilfsfunktionen ---
    const toggleLoading = (isLoading) => {
        ui.loading.classList.toggle('hidden', !isLoading);
        ui.dropZone.classList.toggle('hidden', isLoading);
        if (isLoading) ui.resultArea.classList.add('hidden');
    };

    const updateFileInfo = (file) => {
        ui.fileInfo.textContent = `Verarbeite: ${file.name}`;
        ui.fileInfo.style.display = 'block';
    };

    // --- Drag & Drop ---
    if (ui.dropZone) {
        ui.dropZone.addEventListener('click', () => ui.fileInput.click());

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(name => {
            ui.dropZone.addEventListener(name, (e) => {
                e.preventDefault();
                if (['dragenter', 'dragover'].includes(name)) ui.dropZone.classList.add('dragover');
                else ui.dropZone.classList.remove('dragover');
            });
        });

        ui.dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                ui.fileInput.files = files;
                handleUpload(files[0]);
            }
        });
    }

    if (ui.fileInput) {
        ui.fileInput.addEventListener('change', () => {
            if (ui.fileInput.files.length > 0) handleUpload(ui.fileInput.files[0]);
        });
    }

    // --- API & Datenverarbeitung ---
    async function handleUpload(file) {
        updateFileInfo(file);
        toggleLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/process', { method: 'POST', body: formData });
            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Fehler beim Verarbeiten');
            }
            
            const data = await response.json();
            state.results = data.results;
            state.filename = data.filename;
            
            displayResults(state.results);
        } catch (error) {
            alert(error.message);
            toggleLoading(false);
        } finally {
            ui.loading.classList.add('hidden');
        }
    }

    function displayResults(results) {
        const hasResults = results && results.length > 0;

        // UI-Elemente basierend auf Ergebnissen umschalten
        if (ui.noResultsMessage) ui.noResultsMessage.classList.toggle('hidden', hasResults);
        if (ui.resultsContent) ui.resultsContent.classList.toggle('hidden', !hasResults);
        if (ui.resultTitle) ui.resultTitle.classList.toggle('hidden', !hasResults);
        
        // Filter zurücksetzen bei neuem Display
        if (ui.filterJa) ui.filterJa.checked = true;
        if (ui.filterNein) ui.filterNein.checked = true;
        if (ui.filterStueck) ui.filterStueck.checked = true;
        if (ui.filterKg) ui.filterKg.checked = true;
        if (ui.groupFilter) ui.groupFilter.value = '';
        if (ui.filterError) ui.filterError.classList.add('hidden');

        ui.resultBody.innerHTML = '';
        
        if (hasResults) {
            results.forEach(row => {
                const tr = document.createElement('tr');
                // Metadaten für Filterung speichern
                tr.dataset.status = row['ändern_auf'] || '';
                tr.dataset.einheit = row['einheit'] || '';
                tr.dataset.gruppe = row['gruppe'] || '';
                
                // Definiere Spalten-Mapping (Key im Objekt -> Textinhalt)
                const columns = [
                    { key: 'Name' },
                    { key: 'ID' },
                    { key: 'gruppe' },
                    { key: 'barcode' },
                    { key: 'ändern_auf', isBold: true }
                ];

                columns.forEach(col => {
                    const td = document.createElement('td');
                    const val = row[col.key] || '';
                    if (col.isBold) {
                        const strong = document.createElement('strong');
                        strong.textContent = val;
                        td.appendChild(strong);
                    } else {
                        td.textContent = val;
                    }
                    tr.appendChild(td);
                });

                ui.resultBody.appendChild(tr);
            });
        }
        
        ui.resultArea.classList.remove('hidden');
        applyAllFilters();
    }

    // --- Filter Logik ---
    const getFilterValues = () => ({
        ja: ui.filterJa ? ui.filterJa.checked : true,
        nein: ui.filterNein ? ui.filterNein.checked : true,
        stueck: ui.filterStueck ? ui.filterStueck.checked : true,
        kg: ui.filterKg ? ui.filterKg.checked : true,
        group: ui.groupFilter ? ui.groupFilter.value.trim() : ""
    });

    function applyAllFilters() {
        const filters = getFilterValues();
        const rows = ui.resultBody.querySelectorAll('tr');
        
        // Validierung der Gruppen-ID
        const isNumeric = /^\d*$/.test(filters.group);
        if (ui.filterError) {
            ui.filterError.classList.toggle('hidden', isNumeric);
        }

        rows.forEach(row => {
            const status = row.dataset.status;
            const einheit = row.dataset.einheit;
            const gruppe = row.dataset.gruppe;

            // 1. Basis-Regel: Ohne Einheit immer ausblenden
            if (!einheit || einheit.trim() === "") {
                row.classList.add('hidden');
                return;
            }

            // 2. Filter nach Status (JA/NEIN)
            let matchStatus = false;
            if (status === 'Ja' && filters.ja) matchStatus = true;
            if (status === 'Nein' && filters.nein) matchStatus = true;

            // 3. Filter nach Einheit (Stück/kg)
            let matchEinheit = false;
            if (einheit === 'Stück' && filters.stueck) matchEinheit = true;
            if (einheit === 'kg' && filters.kg) matchEinheit = true;

            // 4. Filter nach Gruppe
            let matchGroup = (filters.group === "" || gruppe === filters.group);

            const isVisible = matchStatus && matchEinheit && matchGroup;
            row.classList.toggle('hidden', !isVisible);
        });
    }

    [ui.filterJa, ui.filterNein, ui.filterStueck, ui.filterKg].forEach(el => {
        if (el) el.addEventListener('change', applyAllFilters);
    });

    if (ui.groupFilter) {
        ui.groupFilter.addEventListener('input', applyAllFilters);
    }

    const sanitizeForCsv = (val) => {
        const str = String(val === null || val === undefined ? '' : val);
        const dangerousStarts = ['=', '+', '-', '@', '\t', '\r'];
        if (dangerousStarts.some(start => str.startsWith(start))) {
            return `'${str}`;
        }
        return str;
    };

    // --- CSV Download ---
    if (ui.downloadBtn) {
        ui.downloadBtn.addEventListener('click', () => {
            if (state.results.length === 0) return;
            
            const headers = ['Name', 'ID', 'gruppe', 'barcode', 'extnr', 'ändern_auf', 'einheit'];
            const csvRows = [
                headers.join(';'),
                ...state.results.map(res => headers.map(h => sanitizeForCsv(res[h])).join(';'))
            ];
            
            const csvContent = "\ufeff" + csvRows.join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            
            const dotIndex = state.filename.lastIndexOf('.');
            const baseName = dotIndex !== -1 ? state.filename.substring(0, dotIndex) : state.filename;
            
            link.href = url;
            link.download = `${baseName}${config.configPostfix}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        });
    }
});
