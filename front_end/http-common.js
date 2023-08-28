// http-common.js
import axios from 'axios';

export default axios.create({
  // baseURL: 'https://perksummit.club:5000',
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});
