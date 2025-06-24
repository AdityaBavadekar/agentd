// const BACKEND_BASE_URL = 'http://127.0.0.1:8080/';
const BACKEND_BASE_URL = 'https://agentd.adityabavadekar.tech/';

const API_ENDPOINTS = {
    API_STATUS: 'api/status',
    API_RUN: 'api/run',
    API_SESSION_STATUS: 'api/status',
    API_ANSWER: 'api/answer',
    API_HEALTH: 'api/health',
};

function getApiUrl(endpoint:string): string {
    return `${BACKEND_BASE_URL}${endpoint}`;
}

function getSessionStatus(sessionId: string): string {
    return getApiUrl(API_ENDPOINTS.API_SESSION_STATUS + `/${sessionId}`);
}

function postSessionAnswer(sessionId: string): string {
    return getApiUrl(API_ENDPOINTS.API_ANSWER + `/${sessionId}`);
}

export {
    API_ENDPOINTS,
    getApiUrl,
    getSessionStatus,
    postSessionAnswer
}