/**
 * ui.js - DOM management and rendering
 */
const UI = {
    showLoading(show = true) {
        const loader = document.getElementById('globalLoader');
        show ? loader.classList.remove('hidden') : loader.classList.add('hidden');
    },

    renderDropdowns(data) {
        const etl = document.getElementById('p_etl');
        const htl = document.getElementById('p_htl');
        
        // Discovery pools
        const d_etl = document.getElementById('discovery_etlPool');
        const d_htl = document.getElementById('discovery_htlPool');
        
        const filter = (list) => list.filter(v => v.length < 35 && !v.includes('('));

        const populate = (el, list, selectAll=false) => {
            if (!el) return;
            const filtered = filter(list);
            el.innerHTML = filtered.map(v => `<option value="${v}" ${selectAll ? 'selected' : ''}>${v}</option>`).join('');
        };

        populate(etl, data.etl);
        populate(htl, data.htl);
        populate(d_etl, data.etl, true);
        populate(d_htl, data.htl, true);
    },

    renderTable(data) {
        const head = document.getElementById('tableHeader');
        const body = document.getElementById('tableBody');
        if (!head || !body) return;

        head.innerHTML = ''; body.innerHTML = '';
        if (!data.length) {
            body.innerHTML = '<tr><td colspan="10">No data found in database.</td></tr>';
            return;
        }

        const keys = Object.keys(data[0]).filter(k => k !== 'composition_short_form' && k !== 'id');
        keys.forEach(k => {
            const th = document.createElement('th');
            // Format: lowercase_with_underscores and monospace
            th.textContent = k.toLowerCase().replace(/\s+/g, '_');
            th.style.fontFamily = "'Fira Code', monospace";
            th.style.fontSize = "0.75rem";
            th.style.letterSpacing = "0";
            head.appendChild(th);
        });

        data.forEach(row => {
            const tr = document.createElement('tr');
            keys.forEach(k => {
                const td = document.createElement('td');
                const val = row[k];
                td.textContent = (typeof val === 'number') ? val.toFixed(3) : (val ?? '-');
                tr.appendChild(td);
            });
            body.appendChild(tr);
        });
    },

    renderDictionary(data) {
        const body = document.getElementById('dictionaryBody');
        if (!body) return;
        body.innerHTML = data.map(item => `
            <tr>
                <td style="font-family: 'Fira Code', monospace; color: var(--primary); font-weight: 600;">${item.name}</td>
                <td>${item.description}</td>
                <td class="text-muted" style="font-size: 0.8rem;">${item.context}</td>
            </tr>
        `).join('');
    },

    renderImportanceChart(data) {
        if (!window.shapChartInstance) return;
        
        const labels = data.importances.map(i => i.feature.toLowerCase());
        const values = data.importances.map(i => i.importance);
        
        window.shapChartInstance.data.labels = labels;
        window.shapChartInstance.data.datasets[0].data = values;
        window.shapChartInstance.data.datasets[0].label = `Importance for ${data.model_name}`;
        window.shapChartInstance.update();
    },

    renderPredictionResult(data, label, unit) {
        const area = document.getElementById('labResult');
        const val = data.pce_t80 || data.ts80m || data.band_gap || data.jv_default_pce;
        
        area.innerHTML = `
            <div class="result-card-large">
                <h3 class="text-muted">${label}</h3>
                <div class="metric-value" style="font-size: 3.5rem; margin: 1rem 0;">
                    ${val.toFixed(2)} <span style="font-size: 1.2rem">${unit}</span>
                </div>
                <div class="uncertainty-viz">
                    <p>90% Prediction Interval: <strong>${data.lower_bound.toFixed(2)} - ${data.upper_bound.toFixed(2)} ${unit}</strong></p>
                    <div class="u-bar"><div class="u-fill" style="width: 70%; left: 15%"></div></div>
                    <p class="text-muted" style="margin-top: 1rem; font-size: 0.8rem;">
                        Uncertainty Range: ±${(data.uncertainty_range/2).toFixed(3)}
                    </p>
                </div>
            </div>
        `;
    },

    renderDiscoveryResult(data, mode) {
        const area = document.getElementById('discoveryResultArea');
        const color = mode === 'band_gap' ? 'var(--primary)' : 'var(--accent)';
        
        let optMsgHtml = '';
        if (data.optimization_message) {
            const isSuccess = data.optimization_message.includes("optimized and ready");
            const msgClass = isSuccess ? "optimization-success" : "optimization-warning";
            const msgIcon = isSuccess ? "✅" : "⚠️";
            const msgLabel = isSuccess ? "Optimization Success" : "Optimization Note";
            
            optMsgHtml = `
                <div class="${msgClass}">
                    <strong>${msgIcon} ${msgLabel}:</strong> ${data.optimization_message}
                </div>
            `;
        }

        area.innerHTML = `
            <div class="result-card-large" style="border-color: ${color}; border-width: 2px;">
                ${optMsgHtml}
                <h3 style="color: ${color}">${mode === 'band_gap' ? 'Optimal Composition' : 'Champion Device Stack'}</h3>
                <div class="metric-value" style="color: ${color}; margin: 1.5rem 0; font-size: 1.6rem; font-family: 'Fira Code', monospace; word-break: break-all; background: var(--bg-page); padding: 1rem; border-radius: 8px;">
                    ${data.composition_long_form}
                </div>
                
                <div class="stats-grid-small">
                    <div class="stat-item"><span>Predicted ${mode === 'band_gap' ? 'Eg' : 'T80'}:</span> <strong>${(data.predicted_band_gap || data.predicted_pce_t80).toFixed(3)}</strong></div>
                    <div class="stat-item"><span>Tolerance Factor:</span> <strong>${data.tolerance_factor.toFixed(3)}</strong></div>
                </div>

                ${mode === 'solar_panel' ? `
                <div class="stats-grid-small" style="margin-top: -1rem;">
                    <div class="stat-item"><span>Architecture:</span> <strong>${data.cell_architecture}</strong></div>
                    <div class="stat-item"><span>ETL:</span> <strong>${data.etl_stack_sequence}</strong></div>
                    <div class="stat-item"><span>HTL:</span> <strong>${data.htl_stack_sequence}</strong></div>
                    <div class="stat-item"><span>Back Contact:</span> <strong>${data.backcontact_stack_sequence}</strong></div>
                </div>
                ` : ''}
            </div>
        `;
    },

    showError(msg, targetId) {
        const area = document.getElementById(targetId);
        area.innerHTML = `<div class="error-box"><strong>Simulation Error:</strong><br>${msg}</div>`;
    }
};
