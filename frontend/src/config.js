export default {
  apiBaseUrl: 'http://new-db-server:3306',
  enableAudit: true
}

export const API_CONFIG = {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token'),
    'Content-Type': 'application/json'
  }
} 