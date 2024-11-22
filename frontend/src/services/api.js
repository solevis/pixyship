import axios from 'axios';

const apiService = {
  getConfig() {
    return axios.get(process.env.VUE_APP_PIXYSHIP_API_URL + 'config');
  }
};

export default apiService;
