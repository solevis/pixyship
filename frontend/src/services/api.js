import axios from 'axios';

const apiService = {
  getConfig() {
    return axios.get(import.meta.env.VITE_PIXYSHIP_API_URL + 'config');
  }
};

export default apiService;
