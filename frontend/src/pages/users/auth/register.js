import React from "react";
import { useState } from "react";
import {useNavigate} from 'react-router-dom'
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../../../constants";
import api from '../../../services/api';
import LoadingIndicator from "../../../components/loadingIndicator";


export default function Register() {
  
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()  

  const handleSubmit = async (e) =>{
    e.preventDefault()
    setLoading(true)
    try{
      const res = await api.post('users/register' , {username, password})
      navigate('/login')
    }catch(e){
      alert(e)
    }finally{
      setLoading(false)
    }
  }

  
  
  return (
    <div className="min-h-screen bg-dark flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-900 p-8 rounded-3xl shadow-xl">
        <h2 className="text-2xl font-bold text-orange-500 mb-6 text-center">Créer un compte</h2>
        <form className="space-y-5">
          <input type="text" placeholder="Nom d'utilisateur" className="w-full border border-gray-700 p-3 rounded-3xl bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <input type="email" placeholder="Email" className="w-full border border-gray-700 p-3 rounded-3xl bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <input type="password" placeholder="Mot de passe" className="w-full border border-gray-700 p-3 rounded-3xl bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <input type="password" placeholder="Confirmer le mot de passe" className="w-full border border-gray-700 p-3 rounded-3xl bg-gray-800 text-white focus:outline-none focus:ring-2 focus:ring-orange-500" />
          <button type="submit" className="w-full py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-3xl font-semibold">S’inscrire</button>
        </form>
        <p className="text-sm text-center text-gray-400 mt-4">Déjà un compte ? <a href="/login" className="text-orange-400 hover:underline">Se connecter</a></p>
      </div>
    </div>
  );
}
