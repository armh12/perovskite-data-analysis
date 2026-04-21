/**
 * app.js - Application logic and entry point
 */
document.addEventListener('DOMContentLoaded', async () => {
    App.init();
});

const App = {
    offset: 0,
    limit: 20,

    async init() {
        this.initTabs();
        this.initExplorer();
        this.initForms();
        this.initCharts();
        
        // Initial Data
        const dropdowns = await API.fetchDropdowns();
        UI.renderDropdowns(dropdowns);
        
        // Load initial SHAP data for dashboard
        this.updateDashboardShap('stability');
    },

    initTabs() {
        // Main Nav
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.nav-btn, .tab-content').forEach(el => el.classList.remove('active'));
                btn.classList.add('active');
                document.getElementById(btn.dataset.tab).classList.add('active');
            });
        });

        // Sub Nav
        document.querySelectorAll('.sub-nav-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const parent = btn.closest('.tab-content') || document;
                const tabId = btn.dataset.subtab;

                parent.querySelectorAll('.sub-nav-btn, .sub-tab-content').forEach(el => el.classList.remove('active'));
                btn.classList.add('active');
                
                const contentEl = document.getElementById(tabId);
                if (contentEl) contentEl.classList.add('active');
                
                // Dashboard specific: Update SHAP chart
                if (tabId.startsWith('shap-')) {
                    const target = tabId.replace('shap-', '');
                    this.updateDashboardShap(target === 'bandgap' ? 'band_gap' : target);
                }

                // Explorer specific: Dictionary logic
                if (tabId === 'dictionary-view') {
                    const dict = await API.fetchDictionary();
                    UI.renderDictionary(dict);
                }

                if (tabId === 'labResult') {
                    document.getElementById('labResult').innerHTML = '<div class="placeholder">Results will appear here</div>';
                }
                
                // Hide device config for Band Gap lab
                const deviceConfig = document.querySelector('.device-config');
                if (deviceConfig) {
                    if (tabId === 'bandgap-lab') {
                        deviceConfig.classList.add('hidden');
                    } else if (['stability-lab', 'ts80m-lab', 'jv-lab'].includes(tabId)) {
                        deviceConfig.classList.remove('hidden');
                    }
                }
            });
        });
    },

    async updateDashboardShap(target) {
        try {
            const data = await API.fetchFeatureImportance(target);
            UI.renderImportanceChart(data);
        } catch (e) {
            console.error("Failed to update SHAP chart:", e);
        }
    },

    initExplorer() {
        const update = async () => {
            const table = document.getElementById('tableSelector').value;
            const data = await API.fetchExplorerData(table, this.offset, this.limit);
            UI.renderTable(data);
            document.getElementById('pageInfo').textContent = `Page ${Math.floor(this.offset/this.limit) + 1}`;
        };

        document.getElementById('nextPage').onclick = () => { this.offset += this.limit; update(); };
        document.getElementById('prevPage').onclick = () => { if(this.offset >= this.limit) { this.offset -= this.limit; update(); } };
        document.getElementById('tableSelector').onchange = () => { this.offset = 0; update(); };
        
        update();
    },

    initForms() {
        // Discovery Toggle Logic
        const discMode = document.getElementById('discoveryMode');
        if (discMode) {
            discMode.addEventListener('change', () => {
                const isSolar = discMode.value === 'solar_panel';
                document.getElementById('solarDiscoveryParams').classList.toggle('hidden', !isSolar);
            });
        }

        // Prediction Lab
        document.getElementById('runPrediction').onclick = async () => {
            const activeTab = document.querySelector('#prediction .sub-nav-btn.active').dataset.subtab;
            const payload = this._buildPredictionPayload(activeTab);
            
            UI.showLoading(true);
            try {
                const res = await API.runPrediction(activeTab, payload);
                const config = {
                    'stability-lab': ['Stability Lifetime', 'Hours'],
                    'ts80m-lab': ['Metric TS80m', 'Hours'],
                    'bandgap-lab': ['Optical Band Gap', 'eV'],
                    'jv-lab': ['Device Efficiency (PCE)', '%']
                };
                UI.renderPredictionResult(res, ...config[activeTab]);
            } catch (e) {
                UI.showError(e.message, 'labResult');
            } finally {
                UI.showLoading(false);
            }
        };

        // Discovery
        document.getElementById('runDiscovery').onclick = async () => {
            const mode = document.getElementById('discoveryMode').value;
            const target = document.getElementById('discoveryTarget').value;
            const inorganic = document.getElementById('discoveryInorganic').checked;
            
            const getSelected = (id) => Array.from(document.getElementById(id).selectedOptions).map(o => o.value);
            
            const a_site_cations = getSelected('discovery_aPool');
            const c_site_anions = getSelected('discovery_cPool');
            
            let extra = {};
            if (mode === 'solar_panel') {
                extra = {
                    architectures: getSelected('discovery_archPool'),
                    etl_stacks: getSelected('discovery_etlPool'),
                    htl_stacks: getSelected('discovery_htlPool'),
                    backcontact_stacks: getSelected('discovery_bcPool'),
                    annealing_temp: parseFloat(document.getElementById('discovery_annTemp').value) || null,
                    annealing_time: parseFloat(document.getElementById('discovery_annTime').value) || null
                };
            }
            
            UI.showLoading(true);
            try {
                const res = await API.runDiscovery(mode, target, inorganic, a_site_cations, c_site_anions, extra);
                UI.renderDiscoveryResult(res, mode);
            } catch (e) {
                UI.showError(e.message, 'discoveryResultArea');
            } finally {
                UI.showLoading(false);
            }
        };
    },

    _buildPredictionPayload(tab) {
        const getVal = (id) => document.getElementById(id).value;
        const getNum = (id) => parseFloat(getVal(id));
        const parseSite = (str) => {
            const regex = /([a-zA-Z]+)([0-9.]+)/g;
            const site = [];
            let m;
            while ((m = regex.exec(str)) !== null) {
                site.push({ name: m[1], frequence: parseFloat(m[2]) });
            }
            return site;
        };

        const base = {
            perovskite_composition: {
                A_site: parseSite(getVal('inp_aSite')),
                B_site: parseSite(getVal('inp_bSite')),
                C_site: parseSite(getVal('inp_cSite'))
            },
            inorganic_composition: document.getElementById('inp_inorganic').checked
        };

        if (tab === 'stability-lab' || tab === 'ts80m-lab') {
            return {
                ...base,
                acc_temp: getNum('s_temp'),
                acc_humidity: getNum('s_hum'),
                pce_initial: getNum('s_pce'),
                band_gap: 1.55, 
                cell_area: 0.1,
                voc_initial: 1.1, jsc_initial: 22, ff_initial: 0.75,
                stability_protocol: "ISOS-L-1",
                stability_light_intensity: 1.0,
                perovskite_annealing_temp: 100, perovskite_annealing_time: 10,
                backcontact: "Au",
                etl_stack_sequence: getVal('p_etl'),
                htl_stack_sequence: getVal('p_htl'),
                cell_architecture: getVal('p_arch')
            };
        } else if (tab === 'bandgap-lab') {
            return base;
        } else if (tab === 'jv-lab') {
            return {
                ...base,
                band_gap: getNum('jv_bg'),
                cell_area: getNum('jv_area'),
                perovskite_annealing_temp: 100, perovskite_annealing_time: 10,
                backcontact: "Au",
                etl_stack_sequence: getVal('p_etl'),
                htl_stack_sequence: getVal('p_htl'),
                cell_architecture: getVal('p_arch')
            };
        }
    },

    initCharts() {
        const ctx = document.getElementById('shapChart')?.getContext('2d');
        if (!ctx) return;
        
        window.shapChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Feature Importance',
                    data: [],
                    backgroundColor: '#4f46e5',
                    borderRadius: 4
                }]
            },
            options: { 
                indexAxis: 'y', 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#64748b', font: { family: 'Fira Code' } },
                        grid: { color: '#f1f5f9' },
                        title: { display: true, text: 'Relative Importance Score', color: '#64748b' }
                    },
                    y: {
                        ticks: { color: '#1e293b', font: { family: 'Fira Code', weight: 'bold' } },
                        grid: { display: false }
                    }
                }
            }
        });
    }
};
