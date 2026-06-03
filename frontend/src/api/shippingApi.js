/**
 * shippingApi.js — Axios wrapper for the FastAPI backend
 */
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Primary endpoint
export const extractEmail = (emailText) =>
  api.post('/extract-email', { email_text: emailText }).then((r) => r.data);

// ── Upload file
export const uploadFile = (file) => {
  const form = new FormData();
  form.append('file', file);
  return api.post('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then((r) => r.data);
};

// ── Records
export const getAllRecords = (skip = 0, limit = 50) =>
  api.get('/records/all', { params: { skip, limit } }).then((r) => r.data);

// ── Search endpoints
export const searchTonnage = (params) =>
  api.get('/search/tonnage', { params }).then((r) => r.data);

export const searchCargoVC = (params) =>
  api.get('/search/cargo_vc', { params }).then((r) => r.data);

export const searchCargoTC = (params) =>
  api.get('/search/cargo_tc', { params }).then((r) => r.data);

export default api;
