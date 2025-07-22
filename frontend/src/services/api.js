import axios from  'axios';
import { ACCESS_TOKEN } from '../constants';

const api = axios.create({
    // baseURL : import.meta.env.API_BASE_URL,
    baseURL : 'http://localhost:8000/api/',
    //baseURL : 'https://roleplayverse.live/api',
    // withCredentials: false,
    // headers: {
    //     'Content-Type': 'application/json',
    //     Accept: 'application/json'
    // }
})

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN)
        if(token){
            config.headers.Authorization = `Bearer ${token}`
        }

        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)



export default api