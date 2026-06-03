/**
 * shippingApi.js — Axios wrapper for the FastAPI backend
 */
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Helper to save records to localStorage
function saveRecords(rawText, filename, records) {
  if (!records || !Array.isArray(records)) return;

  // 1. Load existing collections
  const emails = JSON.parse(localStorage.getItem('shipping_emails') || '[]');
  const tonnages = JSON.parse(localStorage.getItem('shipping_tonnage') || '[]');
  const vcs = JSON.parse(localStorage.getItem('shipping_cargo_vc') || '[]');
  const tcs = JSON.parse(localStorage.getItem('shipping_cargo_tc') || '[]');

  // 2. Generate new email ID
  const maxEmailId = emails.reduce((max, e) => Math.max(max, e.id || 0), 0);
  const newEmailId = maxEmailId + 1;

  // 3. Determine category summary
  const categoriesSeen = new Set(records.map(r => r.category).filter(Boolean));
  let finalCategory = null;
  if (categoriesSeen.size === 1) {
    finalCategory = categoriesSeen.values().next().value;
  } else if (categoriesSeen.size > 1) {
    finalCategory = 'MIXED';
  }

  // 4. Create and save email record
  const emailRec = {
    id: newEmailId,
    filename: filename || null,
    category: finalCategory,
    upload_date: new Date().toISOString(),
    raw_content: rawText
  };
  emails.push(emailRec);
  localStorage.setItem('shipping_emails', JSON.stringify(emails));

  // 5. Create and save records under respective categories
  records.forEach(rec => {
    const cat = rec.category;
    if (cat === 'TONNAGE') {
      const maxId = tonnages.reduce((max, r) => Math.max(max, r.id || 0), 0);
      tonnages.push({
        id: maxId + 1,
        email_id: newEmailId,
        vessel_name: rec.vessel_name || null,
        account_name: rec.account_name || null,
        open_port: rec.open_port || null,
        open_date: rec.open_date || null,
        vessel_type: rec.vessel_type || null,
        vessel_size_dwt: rec.vessel_size_dwt || null,
        flag: rec.flag || null,
        built_year: rec.built_year || null
      });
    } else if (cat === 'CARGO_VC') {
      const maxId = vcs.reduce((max, r) => Math.max(max, r.id || 0), 0);
      vcs.push({
        id: maxId + 1,
        email_id: newEmailId,
        account_name: rec.account_name || null,
        cargo_name: rec.cargo_name || null,
        loading_port: rec.loading_port || null,
        discharge_port: rec.discharge_port || null,
        laycan_raw: rec.laycan_raw || null,
        cargo_type: rec.cargo_type || null,
        quantity: rec.quantity || null,
        commission: rec.commission || null
      });
    } else if (cat === 'CARGO_TC') {
      const maxId = tcs.reduce((max, r) => Math.max(max, r.id || 0), 0);
      tcs.push({
        id: maxId + 1,
        email_id: newEmailId,
        account_name: rec.account_name || null,
        cargo_name: rec.cargo_name || null,
        delivery_port: rec.delivery_port || null,
        redelivery_port: rec.redelivery_port || null,
        duration: rec.duration || null,
        laycan_raw: rec.laycan_raw || null,
        cargo_type: rec.cargo_type || null,
        vessel_size: rec.vessel_size || null,
        commission: rec.commission || null
      });
    }
  });

  // 6. Save records collections
  localStorage.setItem('shipping_tonnage', JSON.stringify(tonnages));
  localStorage.setItem('shipping_cargo_vc', JSON.stringify(vcs));
  localStorage.setItem('shipping_cargo_tc', JSON.stringify(tcs));
}

// ── Primary endpoint
export const extractEmail = (emailText) =>
  api.post('/extract-email', { email_text: emailText }).then((r) => {
    const records = r.data;
    saveRecords(emailText, null, records);
    return records;
  });

// ── Upload file
export const uploadFile = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => {
    const data = r.data; // { filename, records_found, data: results, raw_content }
    saveRecords(data.raw_content, data.filename, data.data);
    return data;
  });
};

// ── Records
export const getAllRecords = async (skip = 0, limit = 50) => {
  const emails = JSON.parse(localStorage.getItem('shipping_emails') || '[]');
  // Sort descending by id
  const sorted = emails.slice().sort((a, b) => b.id - a.id);
  const data = sorted.slice(skip, skip + limit);
  return {
    total: sorted.length,
    skip,
    limit,
    data
  };
};

// ── Search endpoints
export const searchTonnage = async (params = {}) => {
  const tonnages = JSON.parse(localStorage.getItem('shipping_tonnage') || '[]');
  
  let filtered = tonnages;
  if (params.open_port) {
    const q = params.open_port.toLowerCase();
    filtered = filtered.filter(t => t.open_port && t.open_port.toLowerCase().includes(q));
  }
  if (params.flag) {
    const q = params.flag.toLowerCase();
    filtered = filtered.filter(t => t.flag && t.flag.toLowerCase().includes(q));
  }
  if (params.built_year) {
    const q = String(params.built_year);
    filtered = filtered.filter(t => t.built_year && String(t.built_year) === q);
  }
  if (params.min_dwt !== undefined && params.min_dwt !== null) {
    filtered = filtered.filter(t => t.vessel_size_dwt && parseInt(t.vessel_size_dwt) >= parseInt(params.min_dwt));
  }
  if (params.max_dwt !== undefined && params.max_dwt !== null) {
    filtered = filtered.filter(t => t.vessel_size_dwt && parseInt(t.vessel_size_dwt) <= parseInt(params.max_dwt));
  }

  // Sort descending
  const sorted = filtered.slice().sort((a, b) => b.id - a.id);
  const skip = params.skip || 0;
  const limit = params.limit || 50;
  return {
    total: sorted.length,
    data: sorted.slice(skip, skip + limit)
  };
};

export const searchCargoVC = async (params = {}) => {
  const vcs = JSON.parse(localStorage.getItem('shipping_cargo_vc') || '[]');

  let filtered = vcs;
  if (params.loading_port) {
    const q = params.loading_port.toLowerCase();
    filtered = filtered.filter(t => t.loading_port && t.loading_port.toLowerCase().includes(q));
  }
  if (params.discharge_port) {
    const q = params.discharge_port.toLowerCase();
    filtered = filtered.filter(t => t.discharge_port && t.discharge_port.toLowerCase().includes(q));
  }
  if (params.laycan_month) {
    const q = params.laycan_month.toLowerCase();
    filtered = filtered.filter(t => t.laycan_raw && t.laycan_raw.toLowerCase().includes(q));
  }

  // Sort descending
  const sorted = filtered.slice().sort((a, b) => b.id - a.id);
  const skip = params.skip || 0;
  const limit = params.limit || 50;
  return {
    total: sorted.length,
    data: sorted.slice(skip, skip + limit)
  };
};

export const searchCargoTC = async (params = {}) => {
  const tcs = JSON.parse(localStorage.getItem('shipping_cargo_tc') || '[]');

  let filtered = tcs;
  if (params.delivery_port) {
    const q = params.delivery_port.toLowerCase();
    filtered = filtered.filter(t => t.delivery_port && t.delivery_port.toLowerCase().includes(q));
  }
  if (params.redelivery_port) {
    const q = params.redelivery_port.toLowerCase();
    filtered = filtered.filter(t => t.redelivery_port && t.redelivery_port.toLowerCase().includes(q));
  }
  if (params.vessel_size) {
    const q = params.vessel_size.toLowerCase();
    filtered = filtered.filter(t => t.vessel_size && t.vessel_size.toLowerCase().includes(q));
  }

  // Sort descending
  const sorted = filtered.slice().sort((a, b) => b.id - a.id);
  const skip = params.skip || 0;
  const limit = params.limit || 50;
  return {
    total: sorted.length,
    data: sorted.slice(skip, skip + limit)
  };
};

export default api;
