import React from 'react'
import Home from './Pages/Home'
import { Route, Routes } from "react-router-dom";
import Register from './Pages/Register';

const App = () => {
  return (
    <>
      <Routes>
        <Route path="/" element={<Register />} />
        <Route path="/home" element={<Home />} />
      </Routes>
    </>
  )
}

export default App
