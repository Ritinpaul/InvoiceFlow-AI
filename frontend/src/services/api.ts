import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const uploadInvoice = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    // Adjust content-type for multipart/form-data
    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getInvoices = async () => {
    const response = await api.get('/invoices');
    return response.data;
};

export default api;
