import logo from './logo.svg';
import './App.css';
import {BrowserRouter, Route, Routes} from 'react-router-dom'
import Index from './pages/core';
import SignInAndRegister from './pages/users/auth/signinAndRegister';
import Login from './pages/users/auth/login';
import Register from './pages/users/auth/register';
import Home from './pages/core/home';

function App() {
  return (

    <BrowserRouter>
    <Routes>
      <Route 
      path='/'
      element = { <Index /> }
      />
      <Route path="/authenticate" element={<SignInAndRegister />} />
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/home" element={<Home />} />
    </Routes>
    </BrowserRouter>
    
  );
}

export default App;
