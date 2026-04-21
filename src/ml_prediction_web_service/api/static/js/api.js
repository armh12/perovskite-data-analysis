/**
 * api.js - Data access layer for Perovskite CORE
 */
const API = {
    async fetchDropdowns() {
        const endpoints = {
            etl: '/data/etl_stacks',
            htl: '/data/htl_stacks'
        };
        const res = {};
        for (const [key, url] of Object.entries(endpoints)) {
            try {
                const response = await fetch(url);
                res[key] = await response.json();
            } catch (e) {
                console.error(`Error fetching ${key}:`, e);
                res[key] = [];
            }
        }
        return res;
    },

    async fetchExplorerData(table, offset, limit) {
        const url = table === 'perovskites' ? '/data/perovskites' : '/data/solar_panels';
        const response = await fetch(`${url}?offset=${offset}&limit=${limit}`);
        return response.json();
    },

    async fetchDictionary() {
        const response = await fetch('/dictionary/');
        return response.json();
    },

    async fetchFeatureImportance(target) {
        const response = await fetch(`/analysis/feature_importance/${target}`);
        return response.json();
    },

    async runPrediction(type, payload) {
        const endpoints = {
            'stability-lab': '/prediction/stability_pce_t80',
            'ts80m-lab': '/prediction/stability_ts80m',
            'bandgap-lab': '/prediction/band_gap',
            'jv-lab': '/prediction/jv_default_pce'
        };
        const response = await fetch(endpoints[type], {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail ? JSON.stringify(err.detail) : "Prediction Failed");
        }
        return response.json();
    },

    async runDiscovery(mode, target, is_inorganic, a_site_cations, c_site_anions, extraParams = {}) {
        const url = mode === 'band_gap' ? '/discovery/band_gap' : '/discovery/solar_panel';
        const payload = mode === 'band_gap' 
            ? { target_band_gap: parseFloat(target), is_inorganic, max_trials: 100, a_site_cations, c_site_anions }
            : { target_pce_t80: parseFloat(target), is_inorganic, max_trials: 100, a_site_cations, c_site_anions, ...extraParams };
        
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail ? JSON.stringify(err.detail) : "Discovery Engine Timeout or Failure");
        }
        return response.json();
    }
};
