import React from "react";
import { useState } from "react";
import {useNavigate} from 'react-router-dom'
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../../constants";
import api from '../../../services/api';
import LoadingIndicator from "../../../components/loadingIndicator";

export default function Login() {

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()  

  const handleSubmit = async (e) =>{
    e.preventDefault()
    setLoading(true)
    try{
      const res = await api.post('token/' , {username, password})
      if(res.status == 200){
        localStorage.setItem(ACCESS_TOKEN, res.data.access)
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh)
        console.log(res)
        navigate('/home')
      }
      
    }catch(e){
      alert(e)
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-dark flex items-center justify-center px-4">
      <div 
      className="max-w-md w-full bg-gray-900 p-8 rounded-3xl border border-gray-700 shadow-xl">
        <h2 
        className="text-2xl font-bold text-orange-500 mb-6 text-center">Connexion</h2>
        <form onSubmit={handleSubmit}
        className="space-y-5">
          <input value={username} onChange={(e) => setUsername(e.target.value) } type="text" placeholder="Nom d'utilisateur ou email" 
          className="w-full p-3 rounded-3xl border border-gray-700 bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <input value={password} onChange={(e)=> setPassword(e.target.value)}  type="password" placeholder="Mot de passe" 
          className="w-full p-3 rounded-3xl border border-gray-700 bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          
          {loading &&  <LoadingIndicator /> }
          
          <button type="submit" 
          className="w-full py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-3xl font-semibold">Se connecter</button>
        </form>
        <p className="text-sm text-center text-gray-400 mt-4">Pas encore de compte ? <a href="/register" className="text-orange-400 hover:underline">Créer un compte</a></p>
      </div>
    </div>
  );
}
